"""YJK static analysis skill -- runtime.

Delegates the actual YJKAPI work to a subprocess running YJK's
bundled Python 3.10 (``yjk_driver.py``).  This module runs under the
project's own venv Python and therefore cannot import YJKAPI directly.

Environment variables
---------------------
YJKS_ROOT or YJK_PATH : str
    YJK 8.0 installation root (``yjks.exe`` and ``Python310`` live here).
    The official YJK SDK samples use ``YJKS_ROOT``; ``YJK_PATH`` is an
    alias supported for compatibility.
YJKS_EXE : str, optional
    Direct path to ``yjks.exe``.  Overrides root-directory derivation.
YJK_PYTHON_BIN : str, optional
    Direct path to YJK's Python 3.10 interpreter.
    Defaults to ``<install_root>/Python310/python.exe``.
YJK_WORK_DIR : str, optional
    Base directory for YJK project files.
    Defaults to ``<tempdir>/yjk_projects``.
YJK_VERSION : str, optional
    YJK version string passed to ControlConfig.  Default ``8.0.0``.
YJK_TIMEOUT_S : str, optional
    Subprocess timeout in seconds.  Default ``600``.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict

from contracts import EngineNotAvailableError


def _yjk_install_root() -> str:
    """Resolve install root: ``YJK_PATH`` if set, else ``YJKS_ROOT``."""
    return (os.getenv("YJK_PATH", "").strip() or os.getenv("YJKS_ROOT", "").strip())


def _resolve_yjk_python() -> str:
    """Return the path to YJK's bundled Python 3.10 executable."""
    explicit = os.getenv("YJK_PYTHON_BIN", "").strip()
    if explicit and Path(explicit).is_file():
        return explicit

    root = _yjk_install_root()
    if not root:
        raise EngineNotAvailableError(
            engine="yjk",
            reason="YJK install root not set (set YJKS_ROOT or YJK_PATH)",
        )
    if not Path(root).is_dir():
        raise EngineNotAvailableError(
            engine="yjk",
            reason=f"YJK install directory does not exist: {root}",
        )

    python_exe = Path(root) / "Python310" / "python.exe"
    if not python_exe.is_file():
        raise EngineNotAvailableError(
            engine="yjk",
            reason=f"YJK Python 3.10 not found at {python_exe}",
        )
    return str(python_exe)


def _resolve_work_dir() -> Path:
    """Return the work directory for this analysis run."""
    base = os.getenv("YJK_WORK_DIR", "").strip()
    if not base:
        base = str(Path(tempfile.gettempdir()) / "yjk_projects")
    project_name = f"sc_{uuid.uuid4().hex[:8]}"
    work = Path(base) / project_name
    work.mkdir(parents=True, exist_ok=True)
    return work


def run_analysis(model: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point called by the analysis registry.

    Parameters
    ----------
    model : dict
        Deserialized StructureModelV2 payload (raw dict).
    parameters : dict
        Analysis parameters forwarded from the API request.

    Returns
    -------
    dict
        AnalysisResult-shaped dict with status / summary / detailed / warnings.
    """
    yjk_python = _resolve_yjk_python()
    work_dir = _resolve_work_dir()
    timeout = int(os.getenv("YJK_TIMEOUT_S", "600").strip() or "600")

    # Write V2 model JSON to work directory.
    # `model` may arrive as a Pydantic object (StructureModelV1); serialize it first.
    model_dict = model.model_dump(mode="json") if hasattr(model, "model_dump") else model
    model_path = work_dir / "model.json"
    model_path.write_text(json.dumps(model_dict, ensure_ascii=False), encoding="utf-8")

    # Locate the driver script (sibling of this file)
    driver_path = Path(__file__).resolve().parent / "yjk_driver.py"
    if not driver_path.is_file():
        raise RuntimeError(f"YJK driver script not found: {driver_path}")

    # Build environment for the subprocess.
    # Ensure both YJKS_ROOT and YJK_PATH are set for SDK scripts / driver.
    env = os.environ.copy()
    root = _yjk_install_root()
    if root:
        env.setdefault("YJKS_ROOT", root)
        env.setdefault("YJK_PATH", root)
    for key in ("YJKS_EXE", "YJK_VERSION", "YJK_PYTHON_BIN"):
        val = os.getenv(key, "").strip()
        if val:
            env[key] = val

    warnings: list[str] = []

    # Launch the driver under YJK's Python 3.10
    try:
        result = subprocess.run(
            [yjk_python, str(driver_path), str(model_path), str(work_dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(work_dir),
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"YJK analysis timed out after {timeout}s")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Cannot launch YJK Python: {exc}")

    # Parse stdout as JSON result
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0 and not stdout:
        stderr_snippet = stderr[:500] if stderr else "(no stderr)"
        raise RuntimeError(
            f"YJK driver exited with code {result.returncode}. stderr: {stderr_snippet}"
        )

    if not stdout:
        raise RuntimeError("YJK driver produced no output")

    try:
        output = json.loads(stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"YJK driver output is not valid JSON. "
            f"stdout (first 500 chars): {stdout[:500]}"
        )

    status = output.get("status", "error")
    if status == "error":
        error_msg = output.get("detailed", {}).get("error", "Unknown YJK error")
        raise RuntimeError(f"YJK analysis failed: {error_msg}")

    if stderr:
        warnings.append(f"YJK stderr: {stderr[:300]}")

    existing_warnings = output.get("warnings", [])
    if isinstance(existing_warnings, list):
        warnings.extend(existing_warnings)

    return {
        "status": output.get("status", "success"),
        "summary": output.get("summary", {}),
        "data": output.get("data", {}),
        "detailed": output.get("detailed", {}),
        "warnings": warnings,
    }

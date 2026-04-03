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
YJK_INVISIBLE : str, optional
    Set to ``"1"`` to launch YJK headlessly (no GUI window).
    Default ``"0"`` — YJK GUI is visible so the user can observe the run.
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
    """Return a per-run subdirectory under YJK_WORK_DIR.

    YJK_WORK_DIR should be set by the user so that generated project files,
    .OUT results, and logs land in a known, reviewable location.
    Falls back to the system temp directory when unset (not recommended).
    """
    import warnings
    base = os.getenv("YJK_WORK_DIR", "").strip()
    if not base:
        fallback = str(Path(tempfile.gettempdir()) / "yjk_projects")
        warnings.warn(
            "YJK_WORK_DIR is not set; using system temp directory as fallback: "
            f"{fallback}. Set YJK_WORK_DIR in .env to a persistent location.",
            stacklevel=2,
        )
        base = fallback
    project_name = f"sc_{uuid.uuid4().hex[:8]}"
    work = Path(base) / project_name
    work.mkdir(parents=True, exist_ok=True)
    return work


def _extract_last_json(text: str) -> dict | None:
    """Extract the last complete JSON object from text.

    YJK's Python runtime may print non-JSON lines (copyright banners,
    init messages) to stdout before our _emit_json() call.  We scan
    backwards for the last '{' ... '}' block that parses cleanly.
    """
    # Fast path: the whole string is valid JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Scan for the last '{' and try progressively larger suffixes
    last_brace = text.rfind('{')
    if last_brace == -1:
        return None
    try:
        return json.loads(text[last_brace:])
    except json.JSONDecodeError:
        pass

    # Fallback: try each line from the end
    lines = text.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        candidate = '\n'.join(lines[i:]).strip()
        if candidate.startswith('{'):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    return None


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
    for key in ("YJKS_EXE", "YJK_VERSION", "YJK_PYTHON_BIN", "YJK_INVISIBLE"):
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

    # Parse stdout as JSON result.
    # The driver writes only ONE JSON blob to stdout; all progress/debug
    # output goes to stderr so the user can see it in the backend log.
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if stderr:
        import logging
        logging.getLogger("yjk-runtime").info("YJK driver stderr:\n%s", stderr)

    if result.returncode != 0 and not stdout:
        stderr_snippet = stderr[:800] if stderr else "(no stderr)"
        raise RuntimeError(
            f"YJK driver exited with code {result.returncode}.\n"
            f"stderr: {stderr_snippet}"
        )

    if not stdout:
        stderr_snippet = stderr[:800] if stderr else "(no stderr)"
        raise RuntimeError(
            f"YJK driver produced no stdout output.\n"
            f"stderr: {stderr_snippet}"
        )

    # YJK's Python runtime may print non-JSON text (copyright banners,
    # init messages) to stdout before our _emit_json() call.  Extract
    # the last complete JSON object from stdout so those lines don't
    # break parsing.
    output = _extract_last_json(stdout)
    if output is None:
        raise RuntimeError(
            f"YJK driver output is not valid JSON.\n"
            f"stdout (first 500 chars): {stdout[:500]}\n"
            f"stderr (first 500 chars): {stderr[:500]}"
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

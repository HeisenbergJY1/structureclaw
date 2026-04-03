# -*- coding: utf-8 -*-
"""YJK analysis driver -- subprocess entry point.

Must run under YJK's bundled Python 3.10.  Do NOT add extra CLI
arguments; YJKAPI uses sys.argv[1] for internal state and will
break if unexpected args are present.

Usage (called by runtime.py via subprocess):
    <YJK_PYTHON> yjk_driver.py <model.json> <work_dir>

Reads the V2 model JSON, converts to .ydb, launches YJK, runs a
full static analysis, extracts structured results via yjks_pyload,
and outputs the combined result JSON to stdout.

The sequence below strictly follows the proven three_story_steel_frame.py
pattern from the YJK SDK.
"""
from __future__ import annotations

import json
import os
import shutil
import sys


def _setup_yjk_path() -> str:
    """Prepend YJK install root to PATH so YJKAPI can find native DLLs.

    Returns the resolved YJKS_ROOT directory.
    """
    yjks_root = os.environ.get(
        "YJKS_ROOT",
        os.environ.get("YJK_PATH", r"D:\YJKS\YJKS_8_0_0"),
    ).strip().strip('"')

    yjks_exe_env = os.environ.get("YJKS_EXE", "").strip().strip('"')
    if yjks_exe_env and os.path.isfile(yjks_exe_env):
        root = os.path.dirname(os.path.abspath(yjks_exe_env))
        os.environ["PATH"] = root + os.pathsep + os.environ.get("PATH", "")
        return root
    if os.path.isdir(yjks_root):
        os.environ["PATH"] = yjks_root + os.pathsep + os.environ.get("PATH", "")
    return yjks_root


def _find_yjks_exe(root: str) -> str | None:
    for name in ("yjks.exe", "YJKS.exe"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            return p
    return None


def _run_cmd(cmd: str, arg: str = "") -> None:
    from YJKAPI import YJKSControl
    YJKSControl.RunCmd(cmd, arg)


def _collect_out_files(work_dir: str) -> str:
    """Read .OUT/.out files under work_dir as fallback result text."""
    lines: list[str] = []
    for root, _dirs, files in os.walk(work_dir):
        for f in sorted(files):
            if f.upper().endswith(".OUT"):
                fp = os.path.join(root, f)
                try:
                    text = open(fp, encoding="gbk", errors="replace").read()
                    lines.append(f"=== {f} ===\n{text[:3000]}")
                except Exception:
                    pass
    return "\n\n".join(lines) if lines else "(no .OUT files found)"


def main() -> int:
    # -- Parse arguments ------------------------------------------------
    # We receive exactly 2 args: model_json_path and work_dir.
    # sys.argv is: [yjk_driver.py, model.json, work_dir]
    # BUT YJKAPI __init__.py reads sys.argv[1] as "state" -- so we must
    # consume and then strip our args before YJKAPI import.
    if len(sys.argv) < 3:
        _error("Usage: yjk_driver.py <model.json> <work_dir>")
        return 1

    model_path = sys.argv[1]
    work_dir = sys.argv[2]

    # Strip our arguments so YJKAPI sees no stray sys.argv[1]
    sys.argv = [sys.argv[0]]

    yjks_root = _setup_yjk_path()

    # -- Now safe to import YJKAPI --------------------------------------
    from YJKAPI import ControlConfig, YJKSControl

    # -- Read V2 model JSON ---------------------------------------------
    with open(model_path, "r", encoding="utf-8") as f:
        model_data = json.load(f)

    project_name = model_data.get("project", {}).get("name", "sc_model") if isinstance(model_data.get("project"), dict) else "sc_model"
    project_name = project_name or "sc_model"
    ydb_filename = f"{project_name}.ydb"

    # -- Phase 1: Convert V2 -> .ydb ------------------------------------
    from yjk_converter import convert_v2_to_ydb

    try:
        ydb_path = convert_v2_to_ydb(model_data, work_dir, ydb_filename)
    except Exception as exc:
        _error(f"V2 -> YDB conversion failed: {exc}")
        return 1

    # -- Phase 2: Launch YJK (strict three_story_steel_frame.py) --------
    yjks_exe_env = os.environ.get("YJKS_EXE", "").strip().strip('"')
    yjks_exe = yjks_exe_env if yjks_exe_env and os.path.isfile(yjks_exe_env) else _find_yjks_exe(yjks_root)

    if not yjks_exe or not os.path.isfile(yjks_exe):
        _error(f"yjks.exe not found (YJKS_ROOT={yjks_root})")
        return 1

    version = os.environ.get("YJK_VERSION", "8.0.0").strip()

    cfg = ControlConfig()
    cfg.Version = version
    cfg.Invisible = True
    YJKSControl.initConfig(cfg)
    msg = YJKSControl.RunYJK(yjks_exe)

    # -- Phase 3: Open/create project + import ydb ----------------------
    yjk_project = os.path.join(work_dir, f"{project_name}.yjk")
    if os.path.isfile(yjk_project):
        _run_cmd("UIOpen", yjk_project)
    else:
        _run_cmd("UINew", yjk_project)

    _run_cmd("yjk_importydb", ydb_path)

    # -- Phase 4: Model preparation (exact three_story_steel_frame.py) --
    _run_cmd("yjk_repair")
    _run_cmd("yjk_save")
    _run_cmd("yjk_formslab_alllayer")
    _run_cmd("yjk_setlayersupport")

    # -- Phase 5: Preprocessing + full analysis -------------------------
    _run_cmd("yjkspre_genmodrel")
    _run_cmd("yjktransload_tlplan")
    _run_cmd("yjktransload_tlvert")
    _run_cmd("SetCurrentLabel", "IDSPRE_ROOT")
    _run_cmd("yjkdesign_dsncalculating_all")
    _run_cmd("SetCurrentLabel", "IDDSN_DSP")

    # -- Phase 6: Extract structured results via yjks_pyload ------------
    extract_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_results.py")
    extract_dst = os.path.join(work_dir, "extract_results.py")
    if os.path.isfile(extract_src) and extract_src != extract_dst:
        shutil.copy2(extract_src, extract_dst)

    results_json_path = os.path.join(work_dir, "results.json")
    structured_data = None

    if os.path.isfile(extract_dst):
        try:
            YJKSControl.RunCmd("yjks_pyload", extract_dst, "extract")
            if os.path.isfile(results_json_path):
                with open(results_json_path, "r", encoding="utf-8") as rf:
                    structured_data = json.load(rf)
        except Exception:
            pass

    # -- Phase 7: Build final output ------------------------------------
    warnings: list[str] = []
    if structured_data is None:
        warnings.append("Structured result extraction failed; falling back to .OUT files")

    output = {
        "status": "success",
        "summary": {
            "engine": "yjk-static",
            "ydb_path": ydb_path,
            "yjk_project": yjk_project,
            "work_dir": work_dir,
        },
        "data": structured_data or {},
        "detailed": {},
        "warnings": warnings,
    }

    if structured_data:
        meta = structured_data.get("meta", {})
        output["summary"]["n_floors"] = meta.get("n_floors")
        output["summary"]["n_nodes"] = meta.get("n_nodes")
        output["summary"]["load_cases"] = meta.get("load_cases")
        output["summary"]["floor_stats"] = structured_data.get("floor_stats", [])
    else:
        output["detailed"]["raw_output"] = _collect_out_files(work_dir)

    print(json.dumps(output, ensure_ascii=False))
    return 0


def _error(message: str) -> None:
    print(json.dumps({
        "status": "error",
        "summary": {"engine": "yjk-static"},
        "data": {},
        "detailed": {"error": message},
        "warnings": [message],
    }, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())

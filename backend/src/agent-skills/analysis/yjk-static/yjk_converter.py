# -*- coding: utf-8 -*-
"""V2 StructureModelV2 JSON -> YJK .ydb via YJKAPI DataFunc.

Runs under YJK's bundled Python 3.10.  Imported by yjk_driver.py.

Supported:
  - Steel I-section (mat=5, kind=2): ShapeVal "tw,H,B1,tf1,B2,tf2"
  - Steel tube      (mat=5, kind=8): ShapeVal "D,d"
  - Concrete rect   (mat=6, kind=1): ShapeVal "B,H"
  - Standard steel  (kind=26):       name lookup, e.g. "HW350X350"
  - Concrete circle (mat=6, kind=3): ShapeVal "D"

Unit conventions:
  V2 JSON coordinates: meters   -> YJK: mm  (multiply by 1000)
  V2 section dims:     mm       -> YJK: mm  (pass through)
  V2 floor heights:    meters   -> YJK: mm  (multiply by 1000)
  V2 floor loads:      kN/m2    -> YJK: kN/m2 (pass through)
"""
from __future__ import annotations

import os
from typing import Any

from YJKAPI import *

M_TO_MM = 1000.0

# material category -> YJK mat type
_CATEGORY_TO_MAT: dict[str, int] = {
    "steel": 5,
    "concrete": 6,
    "rebar": 6,
    "other": 6,
}

# V2 section type string -> YJK section kind integer
_TYPE_TO_KIND: dict[str, int] = {
    "rectangular": 1,
    "I": 2,
    "H": 2,
    "circular": 3,
    "box": 4,
    "tube": 8,
    "T": 5,
    "L": 6,
}


def _get_floor_loads(story: dict) -> tuple[float, float]:
    """Extract dead and live load values from a V2 story dict."""
    dead = 5.0
    live = 2.0
    for fl in story.get("floor_loads", []):
        if fl.get("type") == "dead":
            dead = float(fl["value"])
        elif fl.get("type") == "live":
            live = float(fl["value"])
    return dead, live


def _infer_section_roles(data: dict) -> dict[str, str]:
    """Build {section_id: "column"|"beam"} by scanning element types."""
    roles: dict[str, str] = {}
    for elem in data.get("elements", []):
        sec_id = elem.get("section", "")
        etype = elem.get("type", "beam")
        if etype == "column" and roles.get(sec_id) != "column":
            roles[sec_id] = "column"
        elif sec_id not in roles:
            roles[sec_id] = "beam"
    return roles


def _resolve_mat_type(sec: dict, data: dict) -> int:
    """Determine YJK material type integer for a section."""
    props = sec.get("properties", {})
    if "mat" in props:
        return int(props["mat"])

    mat_map: dict[str, dict] = {m["id"]: m for m in data.get("materials", [])}
    for elem in data.get("elements", []):
        if elem.get("section") == sec["id"]:
            mat = mat_map.get(elem.get("material", ""))
            if mat:
                cat = mat.get("category", "steel")
                return _CATEGORY_TO_MAT.get(cat, 6)
            break
    return 5


def _build_shape_val(sec: dict, kind: int) -> tuple[int, str, str]:
    """Return (kind, ShapeVal, name) for a V2 section dict.

    Priority:
      1. standard_steel_name -> kind=26
      2. properties with detailed geometry -> build ShapeVal
      3. top-level width/height -> rectangular fallback
    """
    props = sec.get("properties", {})
    extra = sec.get("extra", {})

    std_name = (
        props.get("standard_steel_name")
        or extra.get("standard_steel_name")
        or ""
    )
    if std_name:
        return 26, "", str(std_name)

    # PKPM-style shape dict
    shape = props.get("shape") or sec.get("shape")
    if isinstance(shape, dict):
        sk = shape.get("kind", "")
        if sk in ("H", "I") or kind == 2:
            tw = shape.get("tw", 10)
            H = shape.get("H", sec.get("height", 400))
            B1 = shape.get("B1", shape.get("B", sec.get("width", 200)))
            tf1 = shape.get("tf1", shape.get("tf", 14))
            B2 = shape.get("B2", B1)
            tf2 = shape.get("tf2", tf1)
            return 2, f"{int(tw)},{int(H)},{int(B1)},{int(tf1)},{int(B2)},{int(tf2)}", ""
        if sk == "Box" or kind == 4:
            H = shape.get("H", 400)
            B = shape.get("B", 400)
            T = shape.get("T", 20)
            return 4, f"{int(H)},{int(B)},{int(T)}", ""
        if sk == "Tube" or kind == 8:
            D = shape.get("D", 200)
            d = shape.get("d", D - 20)
            return 8, f"{int(D)},{int(d)}", ""

    if kind == 2:
        tw = props.get("tw", 10)
        H = props.get("H", sec.get("height", 400))
        B1 = props.get("B1", props.get("B", sec.get("width", 200)))
        tf1 = props.get("tf1", props.get("tf", 14))
        B2 = props.get("B2", B1)
        tf2 = props.get("tf2", tf1)
        return 2, f"{int(tw)},{int(H)},{int(B1)},{int(tf1)},{int(B2)},{int(tf2)}", ""

    if kind == 8:
        D = props.get("D", sec.get("diameter", 200))
        d = props.get("d", D - 20 if D else 180)
        return 8, f"{int(D)},{int(d)}", ""

    if kind == 3:
        D = sec.get("diameter") or props.get("D", 400)
        return 3, f"{int(D)}", ""

    w = sec.get("width") or props.get("B", 400)
    h = sec.get("height") or props.get("H", 600)
    return 1, f"{int(w)},{int(h)}", sec.get("name", "")


def _extract_grid_spans(nodes: list[dict]) -> tuple[list[int], list[int]]:
    """Derive axis-grid span arrays from V2 node coordinates (meters -> mm)."""
    xs: set[float] = set()
    ys: set[float] = set()
    for n in nodes:
        xs.add(round(float(n["x"]) * M_TO_MM, 1))
        ys.add(round(float(n["y"]) * M_TO_MM, 1))

    sorted_x = sorted(xs)
    sorted_y = sorted(ys)

    if len(sorted_x) < 2 or len(sorted_y) < 2:
        raise ValueError(
            f"Need at least 2 unique X and 2 unique Y coordinates, "
            f"got {len(sorted_x)} X and {len(sorted_y)} Y"
        )

    xspans = [int(sorted_x[0])]
    for i in range(1, len(sorted_x)):
        xspans.append(int(round(sorted_x[i] - sorted_x[i - 1])))

    yspans = [int(sorted_y[0])]
    for i in range(1, len(sorted_y)):
        yspans.append(int(round(sorted_y[i] - sorted_y[i - 1])))

    return xspans, yspans


def convert_v2_to_ydb(
    data: dict[str, Any],
    work_dir: str,
    ydb_filename: str = "model.ydb",
) -> str:
    """Convert a V2 StructureModelV2 JSON dict to a YJK .ydb file.

    Returns the absolute path to the generated .ydb.
    """
    os.makedirs(work_dir, exist_ok=True)
    warnings: list[str] = []

    stories = sorted(
        data.get("stories", []),
        key=lambda s: float(s.get("elevation", 0)),
    )
    if not stories:
        raise ValueError("V2 model has no stories defined")

    first_story = stories[0]
    height_mm = int(round(float(first_story["height"]) * M_TO_MM))
    dead, live = _get_floor_loads(first_story)

    data_func = DataFunc()
    std_flr = data_func.StdFlr_Generate(height_mm, dead, live)

    section_roles = _infer_section_roles(data)

    col_defs: dict[str, Any] = {}
    beam_defs: dict[str, Any] = {}

    for sec in data.get("sections", []):
        sec_id = sec["id"]
        role = section_roles.get(sec_id, "beam")

        sec_type_str = sec.get("type", "rectangular")
        kind = _TYPE_TO_KIND.get(sec_type_str, 1)
        mat = _resolve_mat_type(sec, data)

        kind, shape_val, name = _build_shape_val(sec, kind)

        try:
            if role == "column":
                col_defs[sec_id] = data_func.ColSect_Def(mat, kind, shape_val, name)
            else:
                beam_defs[sec_id] = data_func.BeamSect_Def(mat, kind, shape_val, name)
        except Exception as exc:
            warnings.append(f"Section '{sec_id}' definition failed: {exc}")

    if not col_defs:
        col_defs["_fallback_col"] = data_func.ColSect_Def(5, 2, "20,650,400,28,400,28")
        warnings.append("No column sections defined; using default steel I-section")
    if not beam_defs:
        beam_defs["_fallback_beam"] = data_func.BeamSect_Def(5, 2, "18,900,300,26,300,26")
        warnings.append("No beam sections defined; using default steel I-section")

    nodes = data.get("nodes", [])
    if not nodes:
        raise ValueError("V2 model has no nodes")

    xspans, yspans = _extract_grid_spans(nodes)

    nodelist = data_func.node_generate(xspans, yspans, std_flr)

    first_col = next(iter(col_defs.values()))
    data_func.column_arrange(nodelist, first_col)

    first_beam = next(iter(beam_defs.values()))
    grid_x = data_func.grid_generate(nodelist, 0, 1)
    grid_y = data_func.grid_generate(nodelist, 1, 0)
    data_func.beam_arrange(grid_x, first_beam)
    data_func.beam_arrange(grid_y, first_beam)

    n_stories = len(stories)
    data_func.Floors_Assemb(0, std_flr, n_stories, height_mm)

    data_func.DbModel_Assign()
    model = data_func.GetDbModelData()
    reader = Hi_AddToAndReadYjk(model)
    reader.CreateYDB(work_dir, ydb_filename)

    ydb_path = os.path.join(work_dir, ydb_filename)
    return ydb_path

# Analysis Skills

## Purpose

- One software x one analysis category = one skill
- Every selectable analysis skill must describe itself in `intent.md` frontmatter
- Every selectable analysis skill keeps its own `runtime.py` and any Python helpers it needs
- `runtime/` only keeps execution plumbing such as worker/api/registry; it is not a skill

## Layout

```
opensees-static/          # OpenSees — static / linear-elastic
opensees-dynamic/         # OpenSees — modal + time-history
opensees-seismic/         # OpenSees — response spectrum + pushover
opensees-nonlinear/       # OpenSees — nonlinear (placeholder)
simplified-static/        # Built-in simplified — static
simplified-dynamic/       # Built-in simplified — dynamic
simplified-seismic/       # Built-in simplified — seismic
pkpm-static/              # PKPM SATWE — static (stub, requires PKPM)
yjk-static/               # YJK — static (stub, requires YJK)
runtime/                  # Execution plumbing only (worker, API, registry)
  contracts.py            # AnalysisResult TypedDict, EngineNotAvailableError
  opensees_shared/        # Shared helpers for all OpenSees skills (tags, result)
```

## Engine Skill Contract

Every `runtime.py` **must** expose:

```python
def run_analysis(model, parameters: Dict[str, Any]) -> AnalysisResult
```

### Execution lifecycle (enforced by `registry.py`)

1. Registry selects engine → finds matching skill → imports `runtime.py`
2. Calls `run_analysis(model, parameters)`
3. **SUCCESS** → return `AnalysisResult(status="success", summary=..., detailed=...)`
4. **PARTIAL** → return `AnalysisResult(status="partial", ...)` with warnings
5. **FAILURE** → `raise RuntimeError(...)` — do NOT return an error dict
6. **ENGINE UNAVAILABLE** → `raise EngineNotAvailableError(engine, reason)`
7. Registry catches exception → tries fallback engine → re-raises if no fallback

### Result collection

- `registry._run_python_analysis()` injects `meta` into the returned dict
- Skill `run_analysis()` must NOT set `meta`; it is owned by the registry

## Rules

- Do not put user-selectable analysis semantics or solver code directly under `runtime/`
- New analysis support should add a new skill folder with `intent.md`, `runtime.py`, and any helper modules it needs
- If a software does not support an analysis type, do not create a fake skill for it
- Failures must raise exceptions — the registry's fallback mechanism depends on it

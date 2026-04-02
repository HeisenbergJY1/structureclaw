"""PKPM static analysis skill — stub runtime.

This module will be filled in once the PKPM APIPyInterface integration
is implemented.  For now it raises EngineNotAvailableError so the
registry can fall back to another engine automatically.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from contracts import EngineNotAvailableError


def run_analysis(model: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point called by the analysis registry.

    Parameters
    ----------
    model : dict
        Deserialized StructureModelV2 payload (dict, not Pydantic instance).
    parameters : dict
        Analysis parameters forwarded from the API request.

    Returns
    -------
    dict
        AnalysisResult-shaped dict with status / summary / detailed / warnings.

    Raises
    ------
    EngineNotAvailableError
        Always raised in this stub version.
    """
    cycle_path = os.getenv("PKPM_CYCLE_PATH", "").strip()
    if not cycle_path:
        raise EngineNotAvailableError(
            engine="pkpm",
            reason="PKPM_CYCLE_PATH environment variable is not set",
        )
    raise EngineNotAvailableError(
        engine="pkpm",
        reason="PKPM analysis runtime is not yet implemented",
    )

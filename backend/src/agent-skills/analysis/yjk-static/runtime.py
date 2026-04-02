"""YJK static analysis skill — stub runtime.

This module will be filled in once the YJK API integration is
implemented.  For now it raises EngineNotAvailableError so the
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
    yjk_path = os.getenv("YJK_PATH", "").strip()
    if not yjk_path:
        raise EngineNotAvailableError(
            engine="yjk",
            reason="YJK_PATH environment variable is not set",
        )
    raise EngineNotAvailableError(
        engine="yjk",
        reason="YJK analysis runtime is not yet implemented",
    )

from __future__ import annotations

from typing import Any, Dict, List, Optional

from contracts import AnalysisResult


def build_success_result(
    summary: Dict[str, Any],
    detailed: Dict[str, Any],
    warnings: Optional[List[str]] = None,
) -> AnalysisResult:
    """Construct a normalised success AnalysisResult."""
    return AnalysisResult(
        status="success",
        summary=summary,
        detailed=detailed,
        warnings=warnings or [],
    )


def build_error_result(message: str) -> AnalysisResult:
    """Construct a normalised error AnalysisResult (use only when raising is not possible)."""
    return AnalysisResult(
        status="error",
        summary={"error": message},
        detailed={},
        warnings=[],
    )

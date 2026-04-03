"""Shared contracts for analysis skill runtimes.

Provides exception types used by all builtin skill ``runtime.py`` modules
(OpenSees, PKPM, YJK, etc.) and consumed by the engine registry for
fallback decisions.
"""

from __future__ import annotations


class EngineNotAvailableError(RuntimeError):
    """Raised when a required analysis engine is not installed or configured."""

    def __init__(self, engine: str, reason: str) -> None:
        self.engine = engine
        self.reason = reason
        super().__init__(f"Engine '{engine}' is not available: {reason}")

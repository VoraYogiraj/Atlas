"""
Atlas Validation Severity

Defines validation severity levels.

Specification:
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model
"""

from __future__ import annotations

from enum import Enum


class AtlasValidationSeverity(str, Enum):
    """
    Severity of a validation result.

    Severity increases from INFORMATION to CRITICAL.
    """

    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        """
        Return the numeric severity rank.

        Higher values represent greater significance.
        """
        return {
            AtlasValidationSeverity.INFORMATION: 0,
            AtlasValidationSeverity.WARNING: 1,
            AtlasValidationSeverity.ERROR: 2,
            AtlasValidationSeverity.CRITICAL: 3,
        }[self]

    def __lt__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(
            other,
            AtlasValidationSeverity,
        ):
            return NotImplemented

        return self.rank < other.rank

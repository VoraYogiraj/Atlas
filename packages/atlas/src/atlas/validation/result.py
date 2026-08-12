"""
Atlas Validation Result

Defines an immutable validation finding.

Specification:
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from atlas.core.aid import AtlasID
from atlas.validation.category import AtlasValidationCategory
from atlas.validation.severity import AtlasValidationSeverity


@dataclass(frozen=True, slots=True)
class AtlasValidationResult:
    """
    Represents one validation finding.

    A validation result is immutable once created.
    """

    id: str
    resource_id: AtlasID
    category: AtlasValidationCategory
    severity: AtlasValidationSeverity
    rule: str
    message: str
    explanation: str
    suggested_resolution: str
    timestamp: datetime

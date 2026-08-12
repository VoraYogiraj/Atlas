"""
Atlas Constraint

ENG-027 — Property Constraints & Unit-Aware Evaluation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from atlas.constraints.operator import AtlasConstraintOperator


@dataclass(frozen=True, slots=True)
class AtlasConstraint:
    """
    Immutable engineering requirement applied to a Resource Property.
    """

    id: str
    property_id: str
    operator: AtlasConstraintOperator
    expected_value: Any
    expected_unit: str | None = None
    context: dict[str, Any] | None = field(default=None)
    source: str | None = None

    def __post_init__(self) -> None:
        if self.context is not None:
            object.__setattr__(
                self,
                "context",
                dict(self.context),
            )
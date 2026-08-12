"""
Atlas Validation Rule

Defines an explicit validation rule.

Specification:
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from atlas.validation.category import AtlasValidationCategory
from atlas.validation.result import AtlasValidationResult

if TYPE_CHECKING:
    from atlas.core.resource import AtlasResource


ValidationCallable = Callable[
    ["AtlasResource"],
    list[AtlasValidationResult],
]


@dataclass(frozen=True, slots=True)
class AtlasValidationRule:
    """
    Represents an immutable validation rule.

    A rule evaluates an AtlasResource and returns zero or more
    validation results.
    """

    id: str
    category: AtlasValidationCategory
    _validator: ValidationCallable

    def __init__(
        self,
        *,
        id: str,
        category: AtlasValidationCategory,
        validate: ValidationCallable,
    ) -> None:
        object.__setattr__(self, "id", id)
        object.__setattr__(
            self,
            "category",
            category,
        )
        object.__setattr__(
            self,
            "_validator",
            validate,
        )

    def validate(
        self,
        resource: AtlasResource,
    ) -> list[AtlasValidationResult]:
        """
        Evaluate the Resource using this validation rule.
        """
        return self._validator(resource)

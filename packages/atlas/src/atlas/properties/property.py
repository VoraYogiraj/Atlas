"""
Atlas Property

Defines an engineering property associated with an Atlas Resource.

Specification:
    ENG-004 — Resource Properties
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AtlasProperty:
    """
    Represents a single engineering property.

    Properties describe characteristics of a Resource.
    """

    id: str
    name: str
    value: Any

    data_type: str

    unit: str | None = None

    description: str = ""

    required: bool = False

    @property
    def has_value(self) -> bool:
        """
        Returns True if the property contains a value.
        """
        return self.value is not None

    def __repr__(self) -> str:
        return (
            f"AtlasProperty("
            f"id='{self.id}', "
            f"value={self.value!r})"
        )
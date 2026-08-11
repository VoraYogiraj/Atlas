"""
Atlas Category

Defines a reusable organizational category for Atlas Resources.

Specification:
ENG-025 — Resource Categories
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasCategory:
    """
    Represents an immutable Resource Category.

    Categories provide reusable organizational groupings for
    Atlas Resources without changing their classification,
    properties, relationships, lifecycle, or semantic tags.
    """

    id: str
    name: str
    description: str = ""

    def __repr__(self) -> str:
        return (
            "AtlasCategory("
            f"id='{self.id}', "
            f"name='{self.name}')"
        )
"""
Atlas Semantic Tag

Defines an immutable semantic tag that can be attached to
Atlas Resources.

ENG-024 — Semantic Tags
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasSemanticTag:
    """
    Represents an immutable semantic tag.

    Semantic tags are reusable across multiple Atlas Resources.
    """

    id: str
    name: str
    description: str = ""

    def __repr__(self) -> str:
        return (
            "AtlasSemanticTag("
            f"id='{self.id}', "
            f"name='{self.name}')"
        )
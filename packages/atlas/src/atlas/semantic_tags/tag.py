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

    A semantic tag provides a reusable semantic meaning that can
    be associated with one or more Atlas Resources.

    Parameters
    ----------
    id:
        Stable identifier for the semantic tag.

    name:
        Human-readable name of the semantic tag.

    description:
        Optional description explaining the semantic meaning.
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
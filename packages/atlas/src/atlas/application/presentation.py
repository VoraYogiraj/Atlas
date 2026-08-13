"""
Atlas Presentation Models

ENG-039 — Atlas UI Architecture

Presentation models are UI-facing representations and are not canonical
Atlas domain objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.core.aid import AtlasID


@dataclass(frozen=True, slots=True)
class AtlasResourcePresentation:
    """
    Read-oriented presentation representation of an Atlas Resource.

    This intentionally does not inherit from or contain the canonical
    AtlasResource object.
    """

    resource_id: AtlasID | None
    name: str
    classification: str | None = None
    properties: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    tags: tuple[Any, ...] = ()
    categories: tuple[Any, ...] = ()
    lifecycle: str | None = None
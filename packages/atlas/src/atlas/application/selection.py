"""
Atlas Resource Selection

ENG-039 — Atlas UI Architecture

Selection is identity-based and never owns a Resource copy.
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.core.aid import AtlasID


@dataclass(slots=True)
class AtlasResourceSelection:
    """
    UI selection represented only by canonical AtlasID.
    """

    resource_id: AtlasID

    def __post_init__(self) -> None:
        if not isinstance(self.resource_id, AtlasID):
            raise TypeError("resource_id must be an AtlasID")
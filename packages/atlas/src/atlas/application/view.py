"""
Atlas UI View

ENG-040 — Atlas UI Application Shell
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AtlasView:
    """
    Main workspace presentation View.

    A View is a UI object and does not own canonical Atlas engineering state.
    """

    view_id: str
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.view_id, str):
            raise TypeError("view_id must be a string")

        if not self.view_id.strip():
            raise ValueError("view_id cannot be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name cannot be empty")
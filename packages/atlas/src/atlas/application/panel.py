"""
Atlas UI Panel

ENG-040 — Atlas UI Application Shell
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AtlasPanel:
    """
    Presentation panel hosted by an AtlasWorkspace.

    Panels are UI/application objects. They do not own canonical
    Atlas engineering state.
    """

    panel_id: str
    name: str
    description: str = ""
    visible: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.panel_id, str):
            raise TypeError("panel_id must be a string")

        if not self.panel_id.strip():
            raise ValueError("panel_id cannot be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not isinstance(self.visible, bool):
            raise TypeError("visible must be a boolean")

    def set_visible(self, visible: bool) -> None:
        """Set presentation visibility."""
        if not isinstance(visible, bool):
            raise TypeError("visible must be a boolean")

        self.visible = visible
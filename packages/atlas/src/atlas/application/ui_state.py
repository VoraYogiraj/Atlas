"""
Atlas UI State

ENG-039 — Atlas UI Architecture

UI state is explicitly separate from engineering state.
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.core.aid import AtlasID


@dataclass(slots=True)
class AtlasUIState:
    """
    Transient presentation/application state.

    This object deliberately does not own an AtlasProject, Resource,
    Registry, or Graph.
    """

    selected_resource_id: AtlasID | None = None
    active_panel: str | None = None

    def set_selection(self, resource_id: AtlasID | None) -> None:
        if resource_id is not None and not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID or None"
            )

        self.selected_resource_id = resource_id
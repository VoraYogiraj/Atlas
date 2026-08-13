"""
Atlas UI Panel Registry

ENG-040 — Atlas UI Application Shell
"""

from __future__ import annotations

from atlas.application.panel import AtlasPanel


class AtlasPanelRegistry:
    """
    Registry for UI Panels.

    This registry is intentionally separate from Atlas Resource and
    Project registries.
    """

    def __init__(self) -> None:
        self._panels: dict[str, AtlasPanel] = {}

    def register(self, panel: AtlasPanel) -> None:
        """Register a panel using its stable UI identity."""
        if not isinstance(panel, AtlasPanel):
            raise TypeError("panel must be an AtlasPanel")

        if panel.panel_id in self._panels:
            raise ValueError(
                f"Panel '{panel.panel_id}' is already registered"
            )

        self._panels[panel.panel_id] = panel

    def get(self, panel_id: str) -> AtlasPanel:
        """Return a registered panel by identity."""
        if not isinstance(panel_id, str):
            raise TypeError("panel_id must be a string")

        try:
            return self._panels[panel_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown panel: {panel_id}"
            ) from exc

    def ids(self) -> tuple[str, ...]:
        """Return registered panel identities."""
        return tuple(self._panels)

    def contains(self, panel_id: str) -> bool:
        """Return whether a panel identity is registered."""
        return panel_id in self._panels

    def __len__(self) -> int:
        return len(self._panels)
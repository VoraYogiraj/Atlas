"""
Atlas UI View Registry

ENG-040 — Atlas UI Application Shell
"""

from __future__ import annotations

from atlas.application.view import AtlasView


class AtlasViewRegistry:
    """
    Registry for main workspace Views.

    This registry contains presentation Views only.
    """

    def __init__(self) -> None:
        self._views: dict[str, AtlasView] = {}

    def register(self, view: AtlasView) -> None:
        """Register a View using its stable UI identity."""
        if not isinstance(view, AtlasView):
            raise TypeError("view must be an AtlasView")

        if view.view_id in self._views:
            raise ValueError(
                f"View '{view.view_id}' is already registered"
            )

        self._views[view.view_id] = view

    def get(self, view_id: str) -> AtlasView:
        """Return a registered View by identity."""
        if not isinstance(view_id, str):
            raise TypeError("view_id must be a string")

        try:
            return self._views[view_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown view: {view_id}"
            ) from exc

    def ids(self) -> tuple[str, ...]:
        """Return registered View identities."""
        return tuple(self._views)

    def contains(self, view_id: str) -> bool:
        """Return whether a View identity is registered."""
        return view_id in self._views

    def __len__(self) -> int:
        return len(self._views)
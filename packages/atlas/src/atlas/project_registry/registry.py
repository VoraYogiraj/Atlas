"""
Atlas Project Registry

Provides controlled registration and lookup of Atlas Projects.

Specification:
    ENG-010 — Project Registry
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.core.aid import AtlasID
from atlas.project import AtlasProject


class AtlasProjectRegistry:
    """
    Registry of Atlas Projects.

    Projects are indexed by their immutable AtlasID.

    The Registry provides:
        - registration
        - lookup
        - existence checks
        - removal
        - iteration
        - count
    """

    def __init__(self) -> None:
        self._projects: dict[AtlasID, AtlasProject] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, project: AtlasProject) -> None:
        """
        Register a Project.

        Raises
        ------
        ValueError
            If a Project with the same AtlasID is already registered.
        """
        if project.aid in self._projects:
            raise ValueError(
                f"Project already registered: {project.aid}"
            )

        self._projects[project.aid] = project

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, aid: AtlasID) -> AtlasProject | None:
        """
        Return a Project by AtlasID.

        Returns None when the Project is not registered.
        """
        return self._projects.get(aid)

    def require(self, aid: AtlasID) -> AtlasProject:
        """
        Return a Project by AtlasID.

        Raises
        ------
        KeyError
            If the Project is not registered.
        """
        try:
            return self._projects[aid]
        except KeyError:
            raise KeyError(f"Project not found: {aid}") from None

    # ------------------------------------------------------------------
    # Existence
    # ------------------------------------------------------------------

    def contains(self, aid: AtlasID) -> bool:
        """Return True if a Project is registered."""
        return aid in self._projects

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def unregister(self, aid: AtlasID) -> AtlasProject | None:
        """
        Remove and return a Project.

        Returns None when the Project is not registered.
        """
        return self._projects.pop(aid, None)

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Return the number of registered Projects."""
        return len(self._projects)

    def __len__(self) -> int:
        """Return the number of registered Projects."""
        return len(self._projects)

    def __iter__(self) -> Iterator[AtlasProject]:
        """Iterate over registered Projects."""
        return iter(self._projects.values())

    def clear(self) -> None:
        """Remove all registered Projects."""
        self._projects.clear()
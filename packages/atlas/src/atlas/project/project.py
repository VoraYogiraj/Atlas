"""
Atlas Project

Defines the top-level project context that owns Atlas Resources.

Specification:
    ENG-009 — Atlas Project
"""

from __future__ import annotations

from atlas.core.aid import AtlasID
from atlas.resource_registry import AtlasResourceRegistry


class AtlasProject:
    """
    Top-level container for an Atlas project.

    An AtlasProject owns its Resource Registry and provides
    project-level identity, naming, and metadata.

    A Project does not directly manage individual Resource
    implementation details. Those concerns belong to the
    Resource and Resource Registry layers.
    """

    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        if not name.strip():
            raise ValueError("Project name cannot be empty")

        self._id = AtlasID.generate()
        self._name = name
        self._metadata: dict[str, object] = {}
        self._registry = AtlasResourceRegistry()

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def aid(self) -> AtlasID:
        """Return the immutable Project identity."""
        return self._id

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the Project name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the Project name."""
        if not value.strip():
            raise ValueError("Project name cannot be empty")

        self._name = value

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, object]:
        """Return Project metadata."""
        return self._metadata

    # ------------------------------------------------------------------
    # Resource Registry
    # ------------------------------------------------------------------

    @property
    def resources(self) -> AtlasResourceRegistry:
        """
        Return the Resource Registry owned by this Project.
        """
        return self._registry

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"name='{self.name}', "
            f"resources={self.resources.count})"
        )
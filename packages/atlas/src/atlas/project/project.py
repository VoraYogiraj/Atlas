"""
Atlas Project

Defines the top-level project context that owns Atlas Resources
and their relationships.

Specification:
ENG-009 / ENG-011 — Atlas Project + Resource Graph Integration
"""

from __future__ import annotations

from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.resource_registry import AtlasResourceRegistry


class AtlasProject:
    """
    Top-level container for an Atlas project.

    An AtlasProject owns:

        - Project identity
        - Project name
        - Project metadata
        - Resource Registry
        - Resource Graph

    The Resource Registry owns Resources.

    The Resource Graph manages Relationships between Resources.
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
        self._graph = AtlasResourceGraph(self._registry)

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
    # Resource API
    # ------------------------------------------------------------------

    def add_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource:
        """
        Add a Resource to this Project.

        Resource ownership remains with the Project's Resource Registry.

        Parameters
        ----------
        resource:
            Resource to register with the Project.

        Returns
        -------
        AtlasResource
            The same Resource instance that was registered.

        Raises
        ------
        ValueError
            If a Resource with the same identity is already registered.
        """
        self._registry.register(resource)

        return resource

    def remove_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource | None:
        """
        Remove a Resource from this Project.

        Parameters
        ----------
        resource:
            Resource to remove.

        Returns
        -------
        AtlasResource | None
            The removed Resource, or None if it is not registered.
        """
        return self._registry.unregister(resource.aid)

    # ------------------------------------------------------------------
    # Resource Graph
    # ------------------------------------------------------------------

    @property
    def graph(self) -> AtlasResourceGraph:
        """
        Return the Resource Graph owned by this Project.
        """
        return self._graph

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"name='{self.name}', "
            f"resources={self.resources.count}, "
            f"relationships={self.graph.count})"
        )
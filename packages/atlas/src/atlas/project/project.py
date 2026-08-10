"""
Atlas Project

Defines the top-level project context that owns Atlas Resources,
Classifications, and their Relationships.

Specification:
ENG-009 / ENG-011 — Atlas Project + Resource Graph Integration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from atlas.classification.registry import AtlasClassificationRegistry
from atlas.core.aid import AtlasID
from atlas.graph import AtlasResourceGraph
from atlas.resource_registry import AtlasResourceRegistry

if TYPE_CHECKING:
    from atlas.core.resource import AtlasResource
    from atlas.relationships.relationship import AtlasRelationship


class AtlasProject:
    """
    Top-level container for an Atlas project.

    An AtlasProject owns:

        - Project identity
        - Project name
        - Project metadata
        - Classification Registry
        - Resource Registry
        - Resource Graph

    The Classification Registry owns the project's valid
    Classification definitions.

    The Resource Registry owns Resources.

    The Resource Graph manages Relationships between Resources.
    """

    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        if not name.strip():
            raise ValueError(
                "Project name cannot be empty"
            )

        self._id = AtlasID.generate()
        self._name = name
        self._metadata: dict[str, object] = {}

        self._classifications = AtlasClassificationRegistry()
        self._registry = AtlasResourceRegistry()
        self._graph = AtlasResourceGraph(
            self._registry
        )

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
    def name(
        self,
        value: str,
    ) -> None:
        """Set the Project name."""
        if not value.strip():
            raise ValueError(
                "Project name cannot be empty"
            )

        self._name = value

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, object]:
        """Return Project metadata."""
        return self._metadata

    # ------------------------------------------------------------------
    # Classification Registry
    # ------------------------------------------------------------------

    @property
    def classifications(self) -> AtlasClassificationRegistry:
        """
        Return the Classification Registry owned by this Project.
        """
        return self._classifications

    def add_classification(
        self,
        classification: object,
    ) -> object:
        """
        Register a Classification with this Project.

        Returns the registered Classification.
        """
        return self._classifications.register(
            classification
        )

    def remove_classification(
        self,
        classification_id: str,
    ) -> object | None:
        """
        Remove a Classification from this Project.

        Returns the removed Classification, or None when
        the Classification is not registered.
        """
        return self._classifications.unregister(
            classification_id
        )

    # ------------------------------------------------------------------
    # Resource Registry
    # ------------------------------------------------------------------

    @property
    def resources(self) -> AtlasResourceRegistry:
        """
        Return the Resource Registry owned by this Project.
        """
        return self._registry

    def add_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource:
        """
        Add a Resource to this Project.

        The Resource's Classification must already be registered
        with this Project.

        Returns
        -------
        AtlasResource
            The registered Resource.
        """
        classification_id = resource.classification.id

        if not self._classifications.contains(
            classification_id
        ):
            raise ValueError(
                "Resource classification is not registered "
                f"with this Project: {classification_id}"
            )

        self._registry.register(
            resource
        )

        return resource

    def remove_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource | None:
        """
        Remove a Resource from this Project.

        Returns the removed Resource, or None if it is not
        registered.
        """
        return self._registry.unregister(
            resource.aid
        )

    # ------------------------------------------------------------------
    # Resource Classification Queries
    # ------------------------------------------------------------------

    def resources_for_classification(
        self,
        classification_id: str,
    ) -> list[AtlasResource]:
        """
        Return all Resources belonging to a Classification.

        The query is delegated to the Project-owned Resource
        Registry.

        Resources are returned in registration order.

        Raises
        ------
        ValueError
            If classification_id is empty or whitespace.
        """
        return self._registry.for_classification(
            classification_id
        )

    # ------------------------------------------------------------------
    # Resource Graph
    # ------------------------------------------------------------------

    @property
    def graph(self) -> AtlasResourceGraph:
        """
        Return the Resource Graph owned by this Project.
        """
        return self._graph

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship:
        """
        Add a Relationship to this Project.

        The Resource Graph validates that both endpoint Resources
        belong to this Project.

        Returns
        -------
        AtlasRelationship
            The registered Relationship.
        """
        self._graph.add(
            relationship
        )

        return relationship

    def remove_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship | None:
        """
        Remove a Relationship from this Project.

        Returns the removed Relationship, or None if it is not
        registered.
        """
        return self._graph.remove(
            relationship.id
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"name='{self.name}', "
            f"classifications={self.classifications.count}, "
            f"resources={self.resources.count}, "
            f"relationships={self.graph.count})"
        )
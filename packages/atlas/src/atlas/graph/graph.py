"""
Atlas Resource Graph

Provides project-level relationship management between Atlas Resources.

Specification:
    ENG-011 — Resource Graph
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.relationships.relationship import AtlasRelationship


class AtlasResourceGraph:
    """
    Project-level graph of Atlas Resources and their relationships.

    The graph does not own Resource objects. Resource ownership remains
    with AtlasResourceRegistry.

    The graph manages relationships between registered Resources.
    """

    def __init__(self) -> None:
        self._relationships: list[AtlasRelationship] = []

    # ------------------------------------------------------------------
    # Relationship Registration
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> None:
        """
        Add a relationship to the graph.

        Raises
        ------
        ValueError
            If the relationship is already present.
        """
        if relationship in self._relationships:
            raise ValueError(
                "Relationship already exists in graph"
            )

        self._relationships.append(relationship)

    # ------------------------------------------------------------------
    # Relationship Lookup
    # ------------------------------------------------------------------

    def contains(
        self,
        relationship: AtlasRelationship,
    ) -> bool:
        """Return True if the relationship exists in the graph."""
        return relationship in self._relationships

    def get_between(
        self,
        first: AtlasResource,
        second: AtlasResource,
    ) -> list[AtlasRelationship]:
        """
        Return relationships connecting two Resources.
        """
        return [
            relationship
            for relationship in self._relationships
            if relationship.involves(first.aid)
            and relationship.involves(second.aid)
        ]

    def for_resource(
        self,
        resource: AtlasResource,
    ) -> list[AtlasRelationship]:
        """
        Return all relationships involving a Resource.
        """
        return [
            relationship
            for relationship in self._relationships
            if relationship.involves(resource.aid)
        ]

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def remove_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship | None:
        """
        Remove and return a relationship.

        Returns None if it is not present.
        """
        if relationship not in self._relationships:
            return None

        self._relationships.remove(relationship)
        return relationship

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Return the number of relationships in the graph."""
        return len(self._relationships)

    def __len__(self) -> int:
        """Return the number of relationships in the graph."""
        return len(self._relationships)

    def __iter__(self) -> Iterator[AtlasRelationship]:
        """Iterate over relationships."""
        return iter(self._relationships)

    def clear(self) -> None:
        """Remove all relationships from the graph."""
        self._relationships.clear()
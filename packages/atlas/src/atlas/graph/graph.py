"""
Atlas Resource Graph

Provides project-level relationship management between Atlas Resources.

Specification:
ENG-011 — Resource Graph
ENG-012 — Project Graph Integrity
ENG-013 — Graph Queries
ENG-014 — Graph Traversal
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from atlas.core.resource import AtlasResource
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


class AtlasResourceGraph:
    """
    Project-level graph of Atlas Resources and their relationships.

    The graph does not own Resource objects.

    Resource ownership remains with AtlasResourceRegistry.

    The graph manages Relationships between Resources that belong
    to its associated Resource Registry.
    """

    def __init__(
        self,
        resources: AtlasResourceRegistry,
    ) -> None:
        self._resources = resources
        self._relationships: list[AtlasRelationship] = []

    # ------------------------------------------------------------------
    # Resource Registry
    # ------------------------------------------------------------------

    @property
    def resources(self) -> AtlasResourceRegistry:
        """
        Return the Resource Registry associated with this graph.
        """
        return self._resources

    # ------------------------------------------------------------------
    # Integrity
    # ------------------------------------------------------------------

    def _validate_resource(
        self,
        resource: AtlasResource,
    ) -> None:
        """
        Ensure that a Resource belongs to this graph's Resource Registry.

        Raises
        ------
        ValueError
            If the Resource does not belong to the associated registry.
        """
        if not self._resources.contains(resource.aid):
            raise ValueError(
                f"Resource does not belong to graph registry: "
                f"{resource.aid}"
            )

    def _validate_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> None:
        """
        Ensure both endpoints of a Relationship belong to this graph.
        """
        self._validate_resource(relationship.source)
        self._validate_resource(relationship.target)

    # ------------------------------------------------------------------
    # Relationship Registration
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> None:
        """
        Add a Relationship to the graph.

        Both endpoint Resources must belong to this graph's
        Resource Registry.

        Raises
        ------
        ValueError
            If either endpoint is not registered or the relationship
            already exists.
        """
        self._validate_relationship(relationship)

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
        """
        Return True if the Relationship exists in the graph.
        """
        return relationship in self._relationships

    def get_between(
        self,
        first: AtlasResource,
        second: AtlasResource,
    ) -> list[AtlasRelationship]:
        """
        Return Relationships connecting two Resources.

        Relationship direction is ignored for this lookup.

        Both Resources must belong to this graph.
        """
        self._validate_resource(first)
        self._validate_resource(second)

        first_id = first.aid
        second_id = second.aid

        return [
            relationship
            for relationship in self._relationships
            if (
                (
                    relationship.source.aid == first_id
                    and relationship.target.aid == second_id
                )
                or (
                    relationship.source.aid == second_id
                    and relationship.target.aid == first_id
                )
            )
        ]

    def for_resource(
        self,
        resource: AtlasResource,
    ) -> list[AtlasRelationship]:
        """
        Return all Relationships involving a Resource.

        The Resource must belong to this graph.
        """
        self._validate_resource(resource)

        resource_id = resource.aid

        return [
            relationship
            for relationship in self._relationships
            if (
                relationship.source.aid == resource_id
                or relationship.target.aid == resource_id
            )
        ]

    # ------------------------------------------------------------------
    # Graph Queries
    # ------------------------------------------------------------------

    def neighbors(
        self,
        resource: AtlasResource,
    ) -> list[AtlasResource]:
        """
        Return Resources directly connected to a Resource.

        Relationship direction is ignored.

        The returned Resources are resolved through the graph's
        Resource Registry.

        Raises
        ------
        ValueError
            If the Resource does not belong to this graph.
        """
        self._validate_resource(resource)

        resource_id = resource.aid
        neighbor_ids = []

        for relationship in self._relationships:
            if relationship.source.aid == resource_id:
                neighbor_ids.append(relationship.target.aid)

            elif relationship.target.aid == resource_id:
                neighbor_ids.append(relationship.source.aid)

        return [
            self._resources.require(neighbor_id)
            for neighbor_id in neighbor_ids
        ]

    def relationships_of_type(
        self,
        resource: AtlasResource,
        relationship_type: str,
    ) -> list[AtlasRelationship]:
        """
        Return relationships of a specific type involving a Resource.

        Relationship direction is ignored.

        Raises
        ------
        ValueError
            If the Resource does not belong to this graph.
        """
        self._validate_resource(resource)

        resource_id = resource.aid

        return [
            relationship
            for relationship in self._relationships
            if (
                (
                    relationship.source.aid == resource_id
                    or relationship.target.aid == resource_id
                )
                and relationship.relationship_type == relationship_type
            )
        ]

    def connected(
        self,
        first: AtlasResource,
        second: AtlasResource,
    ) -> bool:
        """
        Return True if two Resources are directly connected.

        This checks direct relationships only.

        It does not perform multi-hop graph traversal.
        """
        return bool(
            self.get_between(
                first,
                second,
            )
        )

    # ------------------------------------------------------------------
    # Graph Traversal
    # ------------------------------------------------------------------

    def _traversal_neighbors(
        self,
        resource: AtlasResource,
    ) -> list[AtlasResource]:
        """
        Return traversal neighbors with outgoing relationships
        visited before incoming relationships.

        Relationship direction does not restrict reachability, but
        direction provides deterministic traversal ordering.

        Outgoing relationships are returned first, followed by
        incoming relationships.

        Duplicate Resources are removed while preserving order.
        """
        self._validate_resource(resource)

        resource_id = resource.aid

        outgoing_ids = []
        incoming_ids = []

        for relationship in self._relationships:
            if relationship.source.aid == resource_id:
                if relationship.target.aid not in outgoing_ids:
                    outgoing_ids.append(
                        relationship.target.aid
                    )

            elif relationship.target.aid == resource_id:
                if relationship.source.aid not in incoming_ids:
                    incoming_ids.append(
                        relationship.source.aid
                    )

        neighbor_ids = outgoing_ids + [
            neighbor_id
            for neighbor_id in incoming_ids
            if neighbor_id not in outgoing_ids
        ]

        return [
            self._resources.require(neighbor_id)
            for neighbor_id in neighbor_ids
        ]

    def traverse(
        self,
        resource: AtlasResource,
        max_depth: int | None = None,
    ) -> list[AtlasResource]:
        """
        Traverse the graph from a starting Resource using breadth-first
        search.

        The starting Resource is always included in the result.

        Relationship direction does not restrict traversal.

        Parameters
        ----------
        resource:
            Resource from which traversal begins.

        max_depth:
            Maximum number of relationship hops.

            None:
                Traverse all reachable Resources.

            0:
                Return only the starting Resource.

            1:
                Return the starting Resource and direct neighbors.

            2:
                Traverse up to two relationship hops.

        Returns
        -------
        list[AtlasResource]
            Resources in deterministic breadth-first discovery order.

        Raises
        ------
        ValueError
            If the Resource is not registered with this graph.

            If max_depth is negative.
        """
        self._validate_resource(resource)

        if max_depth is not None and max_depth < 0:
            raise ValueError(
                "max_depth must be greater than or equal to 0"
            )

        result: list[AtlasResource] = []

        visited = {resource.aid}

        queue: deque[tuple[AtlasResource, int]] = deque(
            [(resource, 0)]
        )

        while queue:
            current, depth = queue.popleft()

            result.append(current)

            if (
                max_depth is not None
                and depth >= max_depth
            ):
                continue

            for neighbor in self._traversal_neighbors(current):
                if neighbor.aid in visited:
                    continue

                visited.add(neighbor.aid)

                queue.append(
                    (
                        neighbor,
                        depth + 1,
                    )
                )

        return result

    def reachable(
        self,
        source: AtlasResource,
        target: AtlasResource,
    ) -> bool:
        """
        Return True if target is reachable from source.

        Traversal is multi-hop and relationship direction-independent.

        A Resource is reachable from itself.

        Raises
        ------
        ValueError
            If either Resource does not belong to this graph.
        """
        self._validate_resource(source)
        self._validate_resource(target)

        if source.aid == target.aid:
            return True

        visited = {source.aid}

        queue: deque[AtlasResource] = deque(
            [source]
        )

        while queue:
            current = queue.popleft()

            for neighbor in self._traversal_neighbors(current):
                if neighbor.aid in visited:
                    continue

                if neighbor.aid == target.aid:
                    return True

                visited.add(neighbor.aid)
                queue.append(neighbor)

        return False

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def remove_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship | None:
        """
        Remove and return a Relationship.

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
        """
        Return the number of Relationships in the graph.
        """
        return len(self._relationships)

    def __len__(self) -> int:
        """
        Return the number of Relationships in the graph.
        """
        return len(self._relationships)

    def __iter__(self) -> Iterator[AtlasRelationship]:
        """
        Iterate over Relationships.
        """
        return iter(self._relationships)

    def clear(self) -> None:
        """
        Remove all Relationships from the graph.
        """
        self._relationships.clear()
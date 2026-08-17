"""
Atlas Project

Provides the project-level container that owns:

    - Resources
    - Resource relationships
    - Classifications
    - Classification hierarchy
    - Canonical Resource spatial state

Specifications:
    ENG-001 — Project
    ENG-008 — Resource Registry
    ENG-011 — Resource Graph
    ENG-012 — Project Graph Integrity
    ENG-018 — Classification Registry
    ENG-019 — Project Classification Integrity
    ENG-022 — Project Relationship Queries
    ENG-053 — Atlas Resource Move
    ENG-054 — Atlas Resource Rotate
"""

from __future__ import annotations

from typing import Any

from atlas.classification.classification import AtlasClassification
from atlas.classification.hierarchy import AtlasClassificationHierarchy
from atlas.classification.registry import AtlasClassificationRegistry
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.core.spatial import (
    AtlasSpatialPosition,
    AtlasSpatialRotation,
    AtlasSpatialStateRegistry,
)
from atlas.graph.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


class AtlasProject:
    """
    Project-level Atlas context.

    A Project owns its Resource Registry, Resource Graph,
    Classification Registry, Classification Hierarchy,
    and canonical spatial state registry.

    Spatial state is separate from AtlasResource and is keyed by
    canonical AtlasID.
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Project name must be a string"
            )

        if not name.strip():
            raise ValueError(
                "Project name cannot be empty"
            )

        self._aid = AtlasID.generate()
        self._name = name
        self._metadata = dict(
            metadata or {}
        )

        # --------------------------------------------------------------
        # Resource context
        # --------------------------------------------------------------

        self._resources = AtlasResourceRegistry()

        self._spatial_states = (
            AtlasSpatialStateRegistry()
        )

        self._graph = AtlasResourceGraph(
            self._resources
        )

        # --------------------------------------------------------------
        # Classification context
        # --------------------------------------------------------------

        self._classifications = (
            AtlasClassificationRegistry()
        )

        self._classification_hierarchy = (
            AtlasClassificationHierarchy()
        )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def aid(self) -> AtlasID:
        """Return the immutable Project ID."""
        return self._aid

    @property
    def id(self) -> AtlasID:
        """Alias for the Project ID."""
        return self._aid

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
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "Project name must be a string"
            )

        if not value.strip():
            raise ValueError(
                "Project name cannot be empty"
            )

        self._name = value

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, Any]:
        """Return Project metadata."""
        return self._metadata

    # ------------------------------------------------------------------
    # Resource Registry
    # ------------------------------------------------------------------

    @property
    def resources(self) -> AtlasResourceRegistry:
        """Return the canonical Resource Registry."""
        return self._resources

    @property
    def resource_registry(
        self,
    ) -> AtlasResourceRegistry:
        """Alias for the canonical Resource Registry."""
        return self._resources

    # ------------------------------------------------------------------
    # Spatial State
    # ------------------------------------------------------------------

    @property
    def spatial_states(
        self,
    ) -> AtlasSpatialStateRegistry:
        """
        Return the Project-owned canonical spatial state registry.
        """
        return self._spatial_states

    # ------------------------------------------------------------------
    # Resource Graph
    # ------------------------------------------------------------------

    @property
    def graph(self) -> AtlasResourceGraph:
        """Return the Resource Graph."""
        return self._graph

    @property
    def resource_graph(
        self,
    ) -> AtlasResourceGraph:
        """Alias for the Resource Graph."""
        return self._graph

    # ------------------------------------------------------------------
    # Classification Registry
    # ------------------------------------------------------------------

    @property
    def classifications(
        self,
    ) -> AtlasClassificationRegistry:
        """Return the Classification Registry."""
        return self._classifications

    @property
    def classification_registry(
        self,
    ) -> AtlasClassificationRegistry:
        """Alias for the Classification Registry."""
        return self._classifications

    # ------------------------------------------------------------------
    # Classification Hierarchy
    # ------------------------------------------------------------------

    @property
    def classification_hierarchy(
        self,
    ) -> AtlasClassificationHierarchy:
        """Return the Classification Hierarchy."""
        return self._classification_hierarchy

    # ------------------------------------------------------------------
    # Classification Management
    # ------------------------------------------------------------------

    def add_classification(
        self,
        classification: AtlasClassification,
    ) -> AtlasClassification:
        if not isinstance(
            classification,
            AtlasClassification,
        ):
            raise TypeError(
                "classification must be an AtlasClassification"
            )

        classification_id = classification.id

        if self._classifications.contains(
            classification_id
        ):
            raise ValueError(
                "Classification already registered: "
                f"{classification_id}"
            )

        self._classification_hierarchy.add(
            classification
        )

        try:
            self._classifications.register(
                classification
            )
        except Exception:
            self._classifications.remove(
                classification_id
            )
            raise

        return classification

    def get_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        return self._classifications.get(
            classification_id
        )

    def require_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification:
        return self._classifications.require(
            classification_id
        )

    def remove_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        classification = self._classifications.get(
            classification_id
        )

        if classification is None:
            return None

        children = self._classification_hierarchy.children(
            classification
        )

        if children:
            raise ValueError(
                "Cannot remove Classification with children: "
                f"{classification_id}"
            )

        for resource in self._resources:
            if resource.classification.id == classification_id:
                raise ValueError(
                    "Cannot remove Classification used by "
                    f"Resource: {classification_id}"
                )

        removed = self._classification_hierarchy.remove(
            classification_id
        )

        if removed is None:
            return None

        try:
            return self._classifications.remove(
                classification_id
            )
        except Exception:
            self._classification_hierarchy.add(
                classification
            )
            raise

    # ------------------------------------------------------------------
    # Resource Management
    # ------------------------------------------------------------------

    def _initialize_spatial_state(
        self,
        resource: AtlasResource,
    ) -> None:
        """
        Initialize the complete canonical spatial state for a Resource.

        Both ENG-053 position and ENG-054 rotation start at origin/zero.
        """
        self._spatial_states.set_position(
            resource.aid,
            AtlasSpatialPosition(
                x=0.0,
                y=0.0,
                z=0.0,
            ),
        )

        self._spatial_states.set_rotation(
            resource.aid,
            AtlasSpatialRotation(
                x=0.0,
                y=0.0,
                z=0.0,
            ),
        )

    def add_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource:
        """
        Add a Resource through the Project-integrity boundary.

        The Resource Classification must already be registered with
        this Project.
        """
        if not isinstance(
            resource,
            AtlasResource,
        ):
            raise TypeError(
                "resource must be an AtlasResource"
            )

        classification_id = (
            resource.classification.id
        )

        if not self._classifications.contains(
            classification_id
        ):
            raise ValueError(
                "Resource classification is not registered "
                f"with this Project: {classification_id}"
            )

        self._resources.register(
            resource
        )

        self._initialize_spatial_state(
            resource
        )

        return resource

    def get_resource(
        self,
        aid: AtlasID,
    ) -> AtlasResource | None:
        """
        Return a Resource by identifier.

        Missing identifiers return None.

        This method intentionally remains permissive for established
        Registry/Agent read semantics. Strict canonical identity
        validation belongs to callers that explicitly require AtlasID,
        such as Resource Move and Resource Rotate.
        """
        return self._resources.get(
            aid
        )

    def require_resource(
        self,
        aid: AtlasID,
    ) -> AtlasResource:
        """
        Return a required Resource.

        Strictly requires AtlasID.
        """
        if not isinstance(
            aid,
            AtlasID,
        ):
            raise TypeError(
                "aid must be an AtlasID"
            )

        return self._resources.require(
            aid
        )

    def remove_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource | None:
        """
        Remove a Resource and all associated canonical spatial state.
        """
        if not isinstance(
            resource,
            AtlasResource,
        ):
            raise TypeError(
                "resource must be an AtlasResource"
            )

        registered = self._resources.get(
            resource.aid
        )

        if registered is None:
            return None

        relationships = self._graph.for_resource(
            registered
        )

        for relationship in relationships:
            self._graph.remove_relationship(
                relationship
            )

        removed = self._resources.unregister(
            registered.aid
        )

        if removed is not None:
            self._spatial_states.remove(
                registered.aid
            )

        return removed

    # ------------------------------------------------------------------
    # Resource Classification Queries
    # ------------------------------------------------------------------

    def resources_for_classification(
        self,
        classification_id: str,
    ) -> list[AtlasResource]:
        if not isinstance(
            classification_id,
            str,
        ):
            raise TypeError(
                "classification_id must be a string"
            )

        if not classification_id.strip():
            raise ValueError(
                "classification_id cannot be empty"
            )

        return [
            resource
            for resource in self._resources
            if resource.classification.id
            == classification_id
        ]

    # ------------------------------------------------------------------
    # Relationship Management
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship:
        if not isinstance(
            relationship,
            AtlasRelationship,
        ):
            raise TypeError(
                "relationship must be an AtlasRelationship"
            )

        self._graph.add_relationship(
            relationship
        )

        return relationship

    # ------------------------------------------------------------------
    # Relationship Queries
    # ------------------------------------------------------------------

    def relationships_for_resource(
        self,
        resource: AtlasResource,
    ) -> list[AtlasRelationship]:
        return self._graph.for_resource(
            resource
        )

    def outgoing_relationships(
        self,
        resource: AtlasResource,
    ) -> list[AtlasRelationship]:
        return self._graph.outgoing(
            resource
        )

    def incoming_relationships(
        self,
        resource: AtlasResource,
    ) -> list[AtlasRelationship]:
        return self._graph.incoming(
            resource
        )

    def relationships_by_type(
        self,
        relationship_type: str,
    ) -> list[AtlasRelationship]:
        return self._graph.for_relationship_type(
            relationship_type
        )

    # ------------------------------------------------------------------
    # Relationship Removal
    # ------------------------------------------------------------------

    def remove_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship | None:
        return self._graph.remove_relationship(
            relationship
        )

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    @property
    def resource_count(self) -> int:
        return self._resources.count

    @property
    def relationship_count(self) -> int:
        return self._graph.count

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self._resources.count

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "AtlasProject("
            f"aid={self.aid}, "
            f"name={self.name!r}, "
            f"classifications="
            f"{self._classifications.count}, "
            f"resources="
            f"{self._resources.count}, "
            f"relationships="
            f"{self._graph.count}"
            ")"
        )
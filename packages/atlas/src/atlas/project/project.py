"""
Atlas Project

Provides the project-level container that owns:

    - Resources
    - Resource relationships
    - Classifications
    - Classification hierarchy

A Project defines the boundary within which Resources,
Classifications, and Relationships are considered valid.

Specifications:
    ENG-001 — Project
    ENG-008 — Resource Registry
    ENG-011 — Resource Graph
    ENG-012 — Project Graph Integrity
    ENG-018 — Classification Registry
    ENG-019 — Project Classification Integrity
"""

from __future__ import annotations

from typing import Any

from atlas.classification.classification import AtlasClassification
from atlas.classification.hierarchy import AtlasClassificationHierarchy
from atlas.classification.registry import AtlasClassificationRegistry
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.graph.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


class AtlasProject:
    """
    Project-level Atlas context.

    A Project owns its Resource Registry, Resource Graph,
    Classification Registry, and Classification Hierarchy.

    Resources and Classifications are project-scoped. A Resource
    cannot be added to a Project unless its Classification is also
    registered with that Project.

    Relationships are managed by the Project's Resource Graph and
    therefore both endpoint Resources must belong to the Project.
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("Project name must be a string")

        if not name.strip():
            raise ValueError("Project name cannot be empty")

        self._aid = AtlasID.generate()
        self._name = name
        self._metadata = dict(metadata or {})

        # --------------------------------------------------------------
        # Resource context
        # --------------------------------------------------------------

        self._resources = AtlasResourceRegistry()

        self._graph = AtlasResourceGraph(
            self._resources
        )

        # --------------------------------------------------------------
        # Classification context
        # --------------------------------------------------------------

        self._classifications = AtlasClassificationRegistry()

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
        """
        Alias for the Project ID.

        Kept for consistency with other Atlas domain objects.
        """
        return self._aid

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the Project name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Project name must be a string")

        if not value.strip():
            raise ValueError("Project name cannot be empty")

        self._name = value

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Return Project metadata.

        A copy is returned so callers cannot replace the internal
        metadata dictionary accidentally.
        """
        return dict(self._metadata)

    # ------------------------------------------------------------------
    # Resource Registry
    # ------------------------------------------------------------------

    @property
    def resources(self) -> AtlasResourceRegistry:
        """
        Return the Resource Registry owned by this Project.
        """
        return self._resources

    @property
    def resource_registry(self) -> AtlasResourceRegistry:
        """
        Alias for the Project Resource Registry.
        """
        return self._resources

    # ------------------------------------------------------------------
    # Resource Graph
    # ------------------------------------------------------------------

    @property
    def graph(self) -> AtlasResourceGraph:
        """
        Return the Resource Graph owned by this Project.
        """
        return self._graph

    @property
    def resource_graph(self) -> AtlasResourceGraph:
        """
        Alias for the Project Resource Graph.
        """
        return self._graph

    # ------------------------------------------------------------------
    # Classification Registry
    # ------------------------------------------------------------------

    @property
    def classifications(self) -> AtlasClassificationRegistry:
        """
        Return the Classification Registry owned by this Project.
        """
        return self._classifications

    @property
    def classification_registry(
        self,
    ) -> AtlasClassificationRegistry:
        """
        Alias for the Project Classification Registry.
        """
        return self._classifications

    # ------------------------------------------------------------------
    # Classification Hierarchy
    # ------------------------------------------------------------------

    @property
    def classification_hierarchy(
        self,
    ) -> AtlasClassificationHierarchy:
        """
        Return the Classification Hierarchy owned by this Project.
        """
        return self._classification_hierarchy

    # ------------------------------------------------------------------
    # Classification Management
    # ------------------------------------------------------------------

    def add_classification(
        self,
        classification: AtlasClassification,
    ) -> AtlasClassification:
        """
        Register a Classification with this Project.

        The Classification is registered in both the canonical
        Classification Registry and the Classification Hierarchy.

        Parent Classifications must already be registered with this
        Project.

        Returns
        -------
        AtlasClassification
            The registered Classification.

        Raises
        ------
        ValueError
            If the Classification already exists.

            If the Classification has a parent that is not registered
            with this Project.
        """
        classification_id = classification.id

        if self._classifications.contains(classification_id):
            raise ValueError(
                f"Classification already registered: "
                f"{classification_id}"
            )

        # Register in the hierarchy first. This validates the parent
        # relationship before the canonical registry is changed.
        self._classification_hierarchy.add(
            classification
        )

        try:
            self._classifications.register(
                classification
            )
        except Exception:
            # Keep both contexts transactionally consistent.
            self._classification_hierarchy.remove(
                classification_id
            )
            raise

        return classification

    def get_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        """
        Return a Project Classification by ID.

        Returns None when not registered.
        """
        return self._classifications.get(
            classification_id
        )

    def require_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification:
        """
        Return a required Project Classification.

        Raises KeyError when the Classification is not registered.
        """
        return self._classifications.require(
            classification_id
        )

    def remove_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        """
        Remove a Classification from this Project.

        A Classification cannot be removed when:

            - it has registered child Classifications
            - it is currently used by a registered Resource

        The Classification is removed from both the hierarchy and
        canonical registry only after all integrity checks pass.

        Returns
        -------
        AtlasClassification | None
            The removed Classification, or None when it is not
            registered.
        """
        classification = self._classifications.get(
            classification_id
        )

        if classification is None:
            return None

        # A classification with children cannot be removed.
        children = self._classification_hierarchy.children(
            classification
        )

        if children:
            raise ValueError(
                "Cannot remove Classification with children: "
                f"{classification_id}"
            )

        # A classification used by a Resource cannot be removed.
        for resource in self._resources:
            if resource.classification.id == classification_id:
                raise ValueError(
                    "Cannot remove Classification used by "
                    f"Resource: {classification_id}"
                )

        # Remove from hierarchy first, then canonical registry.
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
            # This should not normally occur, but preserve consistency
            # if the registry operation unexpectedly fails.
            self._classification_hierarchy.add(
                classification
            )
            raise

    # ------------------------------------------------------------------
    # Resource Management
    # ------------------------------------------------------------------

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

        Raises
        ------
        ValueError
            If the Resource's Classification is not registered or the
            Resource is already registered.
        """
        classification_id = resource.classification.id

        if not self._classifications.contains(
            classification_id
        ):
            raise ValueError(
                "Resource classification is not registered "
                f"with this Project: {classification_id}"
            )

        return self._resources.register(
            resource
        )

    def get_resource(
        self,
        aid: AtlasID,
    ) -> AtlasResource | None:
        """
        Return a Resource by AtlasID.

        Returns None when the Resource is not registered.
        """
        return self._resources.get(aid)

    def require_resource(
        self,
        aid: AtlasID,
    ) -> AtlasResource:
        """
        Return a required Resource.

        Raises KeyError when the Resource is not registered.
        """
        return self._resources.require(aid)

    def remove_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource | None:
        """
        Remove a Resource from this Project.

        Any Relationships involving the Resource are removed from
        the Project Graph first.

        Returns
        -------
        AtlasResource | None
            The removed Resource, or None if it is not registered.
        """
        registered = self._resources.get(
            resource.aid
        )

        if registered is None:
            return None

        # Remove relationships involving the Resource so the graph
        # never retains references to an unregistered Resource.
        relationships = self._graph.for_resource(
            registered
        )

        for relationship in relationships:
            self._graph.remove_relationship(
                relationship
            )

        return self._resources.unregister(
            registered.aid
        )

    # ------------------------------------------------------------------
    # Resource Queries
    # ------------------------------------------------------------------

    @property
    def resource_count(self) -> int:
        """Return the number of Resources in this Project."""
        return self._resources.count

    def resources_for_classification(
        self,
        classification_id: str,
    ) -> list[AtlasResource]:
        """
        Return Resources belonging to a Classification.

        The query is Project-scoped and uses Classification ID
        identity rather than object identity.
        """
        if not isinstance(classification_id, str):
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
        """
        Add a Relationship to this Project.

        Both endpoint Resources must already belong to this Project.

        Returns
        -------
        AtlasRelationship
            The registered Relationship.
        """
        self._graph.add_relationship(
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
        return self._graph.remove_relationship(
            relationship
        )

    @property
    def relationship_count(self) -> int:
        """
        Return the number of Relationships in this Project.
        """
        return self._graph.count

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of Resources in the Project.
        """
        return self._resources.count

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "AtlasProject("
            f"aid={self.aid}, "
            f"name={self.name!r}, "
            f"classifications={self._classifications.count}, "
            f"resources={self._resources.count}, "
            f"relationships={self._graph.count}"
            ")"
        )
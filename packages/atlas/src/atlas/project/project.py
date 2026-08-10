"""
Atlas Project

Defines the top-level project context that owns Atlas Resources,
Relationships, Classifications, and Classification Hierarchy.

Specification:
ENG-009 / ENG-011 / ENG-019
"""

from __future__ import annotations

from atlas.classification.classification import AtlasClassification
from atlas.classification.hierarchy import AtlasClassificationHierarchy
from atlas.classification.registry import AtlasClassificationRegistry
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


class AtlasProject:
    """
    Top-level container for an Atlas project.

    An AtlasProject owns:

        - Project identity
        - Project name
        - Project metadata
        - Classification Registry
        - Classification Hierarchy
        - Resource Registry
        - Resource Graph

    The Classification Registry owns classification registrations.

    The Classification Hierarchy manages parent/child relationships
    between registered classifications.

    The Resource Registry owns Resources.

    The Resource Graph manages Relationships between Resources.

    The project acts as the integration boundary between these
    subsystems.
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

        # --------------------------------------------------------------
        # Classification Context
        # --------------------------------------------------------------

        self._classifications = AtlasClassificationRegistry()
        self._classification_hierarchy = (
            AtlasClassificationHierarchy()
        )

        # --------------------------------------------------------------
        # Resource Context
        # --------------------------------------------------------------

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
    # Classification Registry
    # ------------------------------------------------------------------

    @property
    def classifications(self) -> AtlasClassificationRegistry:
        """
        Return the Classification Registry owned by this Project.
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
        Register a Classification with the Project.

        Registration occurs in both the Classification Registry and
        Classification Hierarchy.

        Child classifications require their parent to already be
        registered with the Project.

        Raises
        ------
        ValueError
            If the Classification is already registered.

        ValueError
            If the Classification parent is not registered.
        """

        if self._classifications.contains(
            classification.id
        ):
            raise ValueError(
                "Classification already registered: "
                f"{classification.id}"
            )

        # Validate and register in the hierarchy first.
        #
        # This ensures that a child can only be introduced when
        # its parent already belongs to this Project.
        self._classification_hierarchy.add(
            classification
        )

        try:
            self._classifications.register(
                classification
            )
        except Exception:
            # Keep the hierarchy and registry synchronized if the
            # registry unexpectedly rejects the classification.
            self._classification_hierarchy.remove(
                classification.id
            )
            raise

        return classification

    def remove_classification(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        """
        Remove a Classification from the Project.

        A Classification with registered children cannot be removed.

        Returns
        -------
        AtlasClassification | None
            The removed Classification, or None if it was not
            registered.
        """

        classification = self._classifications.get(
            classification_id
        )

        if classification is None:
            return None

        # The hierarchy enforces the child-integrity rule.
        self._classification_hierarchy.remove(
            classification_id
        )

        return self._classifications.remove(
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

    # ------------------------------------------------------------------
    # Resource Management
    # ------------------------------------------------------------------

    def add_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource:
        """
        Register a Resource with the Project.

        Returns the Resource that was registered.
        """
        self._registry.register(resource)

        return resource

    def remove_resource(
        self,
        resource: AtlasResource,
    ) -> AtlasResource | None:
        """
        Remove a Resource from the Project.

        Returns the removed Resource, or None if it was not registered.
        """
        if not self._registry.contains(resource.aid):
            return None

        self._registry.unregister(resource.aid)

        return resource

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
    # Relationship Management
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> AtlasRelationship:
        """
        Add a Relationship to the Project's Resource Graph.

        Returns the Relationship that was added.
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
        Remove a Relationship from the Project's Resource Graph.
        """
        return self._graph.remove_relationship(
            relationship
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
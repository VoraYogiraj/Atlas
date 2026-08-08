"""
Atlas Resource

Defines the base engineering entity used throughout Atlas.

Specifications:
    ENG-001 — Atlas Resource
    ENG-003 — Resource Classification
    ENG-004 — Resource Properties
    ENG-005 — Resource Relationships
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID

if TYPE_CHECKING:
    from atlas.properties.property import AtlasProperty
    from atlas.relationships.relationship import AtlasRelationship


class AtlasResource:
    """
    Base class for every Atlas Resource.

    Every engineering entity in Atlas inherits from this class.

    A Resource has:
        - Atlas identity
        - Classification
        - Properties
        - Relationships
        - Lifecycle state
        - Metadata

    Specialized concerns such as geometry, rendering, persistence,
    and AI behavior do not belong in this base class.
    """

    def __init__(
        self,
        *,
        classification: AtlasClassification,
        name: str | None = None,
    ) -> None:
        self._id = AtlasID.generate()

        self._classification = classification
        self._name = name

        self._properties: dict[str, AtlasProperty] = {}
        self._relationships: list[AtlasRelationship] = []

        self._metadata: dict[str, object] = {}

        # Temporary primitive representation.
        # This will be replaced by AtlasLifecycle.
        self._lifecycle = "created"

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def aid(self) -> AtlasID:
        """Return the immutable Atlas Resource identity."""
        return self._id

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    @property
    def classification(self) -> AtlasClassification:
        """Return the Resource classification."""
        return self._classification

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------

    @property
    def name(self) -> str | None:
        """Return the Resource name."""
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        """Set the Resource name."""
        self._name = value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def properties(self) -> dict[str, AtlasProperty]:
        """Return the Resource's properties."""
        return self._properties

    def set_property(self, property: AtlasProperty) -> None:
        """
        Add or replace a Resource property.

        Properties are indexed by their Atlas property ID.
        """
        self._properties[property.id] = property

    def get_property(self, property_id: str) -> AtlasProperty | None:
        """
        Retrieve a property by its ID.
        """
        return self._properties.get(property_id)

    def remove_property(self, property_id: str) -> AtlasProperty | None:
        """
        Remove and return a property by its ID.

        Returns None when the property does not exist.
        """
        return self._properties.pop(property_id, None)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    @property
    def relationships(self) -> list[AtlasRelationship]:
        """Return the Resource's relationships."""
        return self._relationships

    def add_relationship(self, relationship: AtlasRelationship) -> None:
        """Add a relationship to the Resource."""
        self._relationships.append(relationship)

    def remove_relationship(self, relationship: AtlasRelationship) -> None:
        """Remove a relationship from the Resource."""
        self._relationships.remove(relationship)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, object]:
        """Return Resource metadata."""
        return self._metadata

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @property
    def lifecycle(self) -> str:
        """
        Return the current lifecycle state.

        This is temporarily represented as a string.
        AtlasLifecycle will replace this in the next step.
        """
        return self._lifecycle

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"classification='{self.classification.name}')"
        )
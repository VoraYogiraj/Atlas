"""
Atlas Resource

Defines the base engineering entity used throughout Atlas.

Specifications:
ENG-001 — Atlas Resource
ENG-003 — Resource Classification
ENG-004 — Resource Properties
ENG-005 — Resource Relationships
ENG-007 — Resource Lifecycle
ENG-024 — Semantic Tags
ENG-025 — Resource Categories
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.semantic_tags.tag import AtlasSemanticTag

if TYPE_CHECKING:
    from atlas.properties.property import AtlasProperty
    from atlas.relationships.relationship import AtlasRelationship


class AtlasResource:
    """
    Base class for every Atlas Resource.

    Every engineering entity in Atlas inherits from this class.
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

        # ENG-024 — Semantic Tags
        self._tags: dict[str, AtlasSemanticTag] = {}

        # ENG-025 — Resource Categories
        self._categories: dict[str, AtlasCategory] = {}

        self._lifecycle = AtlasLifecycle.CREATED

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
    def name(
        self,
        value: str | None,
    ) -> None:
        """Set the Resource name."""
        self._name = value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def properties(self) -> dict[str, AtlasProperty]:
        """Return the Resource's properties."""
        return self._properties

    def set_property(
        self,
        property: AtlasProperty,
    ) -> None:
        """Add or replace a Resource property."""
        self._properties[property.id] = property

    def get_property(
        self,
        property_id: str,
    ) -> AtlasProperty | None:
        """Retrieve a property by its ID."""
        return self._properties.get(
            property_id
        )

    def remove_property(
        self,
        property_id: str,
    ) -> AtlasProperty | None:
        """Remove and return a property by its ID."""
        return self._properties.pop(
            property_id,
            None,
        )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    @property
    def relationships(self) -> list[AtlasRelationship]:
        """Return the Resource's relationships."""
        return self._relationships

    def add_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> None:
        """Add a relationship to the Resource."""
        self._relationships.append(
            relationship
        )

    def remove_relationship(
        self,
        relationship: AtlasRelationship,
    ) -> None:
        """Remove a relationship from the Resource."""
        self._relationships.remove(
            relationship
        )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, object]:
        """Return Resource metadata."""
        return self._metadata

    # ------------------------------------------------------------------
    # Semantic Tags
    # ------------------------------------------------------------------

    @property
    def tags(self) -> list[AtlasSemanticTag]:
        """
        Return the Resource's semantic tags.

        Tags are returned in insertion order.
        """
        return list(
            self._tags.values()
        )

    def add_tag(
        self,
        tag: AtlasSemanticTag,
    ) -> AtlasSemanticTag:
        """
        Add a semantic tag to the Resource.

        Raises
        ------
        TypeError
            If tag is not an AtlasSemanticTag.

        ValueError
            If a tag with the same ID is already attached.
        """
        if not isinstance(
            tag,
            AtlasSemanticTag,
        ):
            raise TypeError(
                "tag must be an AtlasSemanticTag"
            )

        if tag.id in self._tags:
            raise ValueError(
                f"Semantic tag already exists: {tag.id}"
            )

        self._tags[tag.id] = tag

        return tag

    def get_tag(
        self,
        tag_id: str,
    ) -> AtlasSemanticTag | None:
        """
        Return a semantic tag by ID.

        Returns None when the tag is not attached.

        Raises
        ------
        TypeError
            If tag_id is not a string.
        """
        if not isinstance(
            tag_id,
            str,
        ):
            raise TypeError(
                "tag_id must be a string"
            )

        return self._tags.get(
            tag_id
        )

    def has_tag(
        self,
        tag_id: str,
    ) -> bool:
        """
        Return True if the Resource has a semantic tag.

        Raises
        ------
        TypeError
            If tag_id is not a string.
        """
        if not isinstance(
            tag_id,
            str,
        ):
            raise TypeError(
                "tag_id must be a string"
            )

        return tag_id in self._tags

    def remove_tag(
        self,
        tag_id: str,
    ) -> AtlasSemanticTag | None:
        """
        Remove and return a semantic tag.

        Returns None when the tag is not attached.

        Raises
        ------
        TypeError
            If tag_id is not a string.
        """
        if not isinstance(
            tag_id,
            str,
        ):
            raise TypeError(
                "tag_id must be a string"
            )

        return self._tags.pop(
            tag_id,
            None,
        )

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    @property
    def categories(self) -> list[AtlasCategory]:
        """
        Return the Resource's categories.

        Categories are returned in insertion order.
        """
        return list(
            self._categories.values()
        )

    def add_category(
        self,
        category: AtlasCategory,
    ) -> AtlasCategory:
        """
        Add a category to the Resource.

        Raises
        ------
        TypeError
            If category is not an AtlasCategory.

        ValueError
            If a category with the same ID is already attached.
        """
        if not isinstance(
            category,
            AtlasCategory,
        ):
            raise TypeError(
                "category must be an AtlasCategory"
            )

        if category.id in self._categories:
            raise ValueError(
                f"Category already exists: {category.id}"
            )

        self._categories[category.id] = category

        return category

    def get_category(
        self,
        category_id: str,
    ) -> AtlasCategory | None:
        """
        Return a category by ID.

        Returns None when the category is not attached.

        Raises
        ------
        TypeError
            If category_id is not a string.
        """
        if not isinstance(
            category_id,
            str,
        ):
            raise TypeError(
                "category_id must be a string"
            )

        return self._categories.get(
            category_id
        )

    def has_category(
        self,
        category_id: str,
    ) -> bool:
        """
        Return True if the Resource has the specified category.

        Raises
        ------
        TypeError
            If category_id is not a string.
        """
        if not isinstance(
            category_id,
            str,
        ):
            raise TypeError(
                "category_id must be a string"
            )

        return category_id in self._categories

    def remove_category(
        self,
        category_id: str,
    ) -> AtlasCategory | None:
        """
        Remove and return a category.

        Returns None when the category is not attached.

        Raises
        ------
        TypeError
            If category_id is not a string.
        """
        if not isinstance(
            category_id,
            str,
        ):
            raise TypeError(
                "category_id must be a string"
            )

        return self._categories.pop(
            category_id,
            None,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @property
    def lifecycle(self) -> AtlasLifecycle:
        """Return the current lifecycle state."""
        return self._lifecycle

    def transition_to(
        self,
        target: AtlasLifecycle,
    ) -> None:
        """
        Transition the Resource to another lifecycle state.

        Raises
        ------
        ValueError
            If the requested lifecycle transition is not allowed.
        """
        if not self._lifecycle.can_transition_to(
            target
        ):
            raise ValueError(
                f"Invalid lifecycle transition: "
                f"{self._lifecycle.value} -> {target.value}"
            )

        self._lifecycle = target

    def activate(self) -> None:
        """Activate the Resource."""
        self.transition_to(
            AtlasLifecycle.ACTIVE
        )

    def archive(self) -> None:
        """Archive the Resource."""
        self.transition_to(
            AtlasLifecycle.ARCHIVED
        )

    def delete(self) -> None:
        """Mark the Resource as deleted."""
        self.transition_to(
            AtlasLifecycle.DELETED
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"classification='{self.classification.name}', "
            f"lifecycle='{self.lifecycle.value}')"
        )
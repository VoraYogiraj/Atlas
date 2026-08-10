"""
Atlas Classification Hierarchy

Provides collection and lookup management for
Atlas Classifications.

Specification:
ENG-017 — Classification Hierarchy
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.classification.classification import AtlasClassification


class AtlasClassificationHierarchy:
    """
    Collection of Atlas Classifications.

    The hierarchy owns classification registrations, while the
    AtlasClassification objects themselves remain immutable.

    Classification ancestry is defined by each classification's
    ``parent`` relationship.
    """

    def __init__(self) -> None:
        self._classifications: dict[
            str,
            AtlasClassification,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def add(
        self,
        classification: AtlasClassification,
    ) -> AtlasClassification:
        """
        Add a Classification to the hierarchy.

        Classification IDs must be unique.

        Raises
        ------
        ValueError
            If a Classification with the same ID already exists.
        """
        if classification.id in self._classifications:
            raise ValueError(
                "Classification already exists in hierarchy: "
                f"{classification.id}"
            )

        self._classifications[
            classification.id
        ] = classification

        return classification

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        """
        Return a Classification by ID.

        Returns None if the Classification is not registered.
        """
        return self._classifications.get(
            classification_id
        )

    def contains(
        self,
        classification_id: str,
    ) -> bool:
        """
        Return True if a Classification ID is registered.
        """
        return classification_id in self._classifications

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def remove(
        self,
        classification_id: str,
    ) -> AtlasClassification | None:
        """
        Remove and return a Classification.

        Returns None if the Classification is not registered.
        """
        return self._classifications.pop(
            classification_id,
            None,
        )

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """
        Return the number of registered Classifications.
        """
        return len(self._classifications)

    def __len__(self) -> int:
        """
        Return the number of registered Classifications.
        """
        return len(self._classifications)

    def __iter__(
        self,
    ) -> Iterator[AtlasClassification]:
        """
        Iterate over registered Classifications.

        Classifications are returned in insertion order.
        """
        return iter(
            self._classifications.values()
        )

    def clear(self) -> None:
        """
        Remove all Classifications from the hierarchy.
        """
        self._classifications.clear()
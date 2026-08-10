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
    Collection and integrity manager for Atlas Classifications.

    The hierarchy owns classification registrations.

    AtlasClassification objects remain immutable and define their own
    parent relationship.

    The hierarchy is responsible for ensuring that registered
    classifications form a coherent parent/child structure.
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

        Root classifications may be added without a parent.

        Child classifications require their direct parent to already
        be registered.

        Raises
        ------
        ValueError
            If the classification ID already exists.

        ValueError
            If the classification has a parent that is not registered.
        """
        if classification.id in self._classifications:
            raise ValueError(
                "Classification already exists in hierarchy: "
                f"{classification.id}"
            )

        parent = classification.parent

        if (
            parent is not None
            and parent.id not in self._classifications
        ):
            raise ValueError(
                "Classification parent is not registered: "
                f"{parent.id}"
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

        A Classification cannot be removed while another registered
        Classification declares it as its parent.

        Returns None if the Classification is not registered.

        Raises
        ------
        ValueError
            If the Classification has registered children.
        """
        classification = self._classifications.get(
            classification_id
        )

        if classification is None:
            return None

        for registered in self._classifications.values():
            if registered.parent is None:
                continue

            if registered.parent.id == classification_id:
                raise ValueError(
                    "Cannot remove classification with "
                    f"registered children: {classification_id}"
                )

        return self._classifications.pop(
            classification_id
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
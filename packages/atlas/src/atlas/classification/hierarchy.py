"""
Atlas Classification Hierarchy

Provides collection, integrity, and query management
for Atlas Classifications.

Specification:
ENG-017 — Classification Hierarchy
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.classification.classification import AtlasClassification


class AtlasClassificationHierarchy:
    """
    Collection and integrity manager for Atlas Classifications.

    AtlasClassification objects remain immutable and define their
    own parent relationship.

    This hierarchy is responsible for:

        - Classification registration
        - Classification lookup
        - Parent integrity
        - Safe removal
        - Hierarchy queries
        - Collection management
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
            If the classification has an unregistered parent.
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
    # Validation
    # ------------------------------------------------------------------

    def _validate_registered(
        self,
        classification: AtlasClassification,
    ) -> None:
        """
        Ensure that a Classification belongs to this hierarchy.

        Raises
        ------
        ValueError
            If the Classification is not registered.
        """
        registered = self._classifications.get(
            classification.id
        )

        if registered is None:
            raise ValueError(
                "Classification does not belong to hierarchy: "
                f"{classification.id}"
            )

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
    # Hierarchy Queries
    # ------------------------------------------------------------------

    def roots(self) -> list[AtlasClassification]:
        """
        Return all registered root Classifications.

        Roots are returned in registration order.
        """
        return [
            classification
            for classification in self._classifications.values()
            if classification.parent is None
        ]

    def children(
        self,
        classification: AtlasClassification,
    ) -> list[AtlasClassification]:
        """
        Return the direct children of a Classification.

        Grandchildren and deeper descendants are not included.

        Children are returned in registration order.
        """
        self._validate_registered(classification)

        classification_id = classification.id

        return [
            registered
            for registered in self._classifications.values()
            if (
                registered.parent is not None
                and registered.parent.id == classification_id
            )
        ]

    def parent(
        self,
        classification: AtlasClassification,
    ) -> AtlasClassification | None:
        """
        Return the direct parent of a Classification.

        Returns None for root Classifications.
        """
        self._validate_registered(classification)

        parent = classification.parent

        if parent is None:
            return None

        return self._classifications.get(parent.id)

    def ancestors(
        self,
        classification: AtlasClassification,
    ) -> list[AtlasClassification]:
        """
        Return all ancestors of a Classification.

        Ancestors are returned from nearest parent to root.

        Example
        -------
        Wall
            parent -> Building
            parent -> Physical Resource

        returns:

            [Building, Physical Resource]
        """
        self._validate_registered(classification)

        result: list[AtlasClassification] = []

        current = classification.parent

        while current is not None:
            registered = self._classifications.get(
                current.id
            )

            if registered is None:
                raise ValueError(
                    "Classification parent is not registered: "
                    f"{current.id}"
                )

            result.append(registered)
            current = registered.parent

        return result

    def descendants(
        self,
        classification: AtlasClassification,
    ) -> list[AtlasClassification]:
        """
        Return all descendants of a Classification.

        Descendants are returned in depth-first registration order.

        Direct children are returned before their descendants.

        Example
        -------
        Building
            ├── Wall
            │   └── Door
            └── Window

        returns:

            [Wall, Door, Window]
        """
        self._validate_registered(classification)

        result: list[AtlasClassification] = []

        def visit(
            current: AtlasClassification,
        ) -> None:
            for child in self.children(current):
                result.append(child)
                visit(child)

        visit(classification)

        return result

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
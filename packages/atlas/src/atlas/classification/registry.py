"""
Atlas Classification Registry

Provides canonical registration and lookup of
Atlas Classifications.

Specification:
ENG-018 — Classification Registry
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.classification.classification import AtlasClassification


class AtlasClassificationRegistry:
    """
    Canonical registry of Atlas Classifications.

    The registry owns classification registrations but does not
    modify the immutable AtlasClassification objects.

    Classification IDs are unique within the registry.
    """

    def __init__(self) -> None:
        self._classifications: dict[
            str,
            AtlasClassification,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        classification: AtlasClassification,
    ) -> AtlasClassification:
        """
        Register a Classification.

        Raises
        ------
        ValueError
            If a Classification with the same ID is already registered.
        """
        if classification.id in self._classifications:
            raise ValueError(
                "Classification already registered: "
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

    def require(
        self,
        classification_id: str,
    ) -> AtlasClassification:
        """
        Return a registered Classification.

        Raises
        ------
        KeyError
            If the Classification is not registered.
        """
        classification = self._classifications.get(
            classification_id
        )

        if classification is None:
            raise KeyError(
                f"Classification is not registered: "
                f"{classification_id}"
            )

        return classification

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

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

        Classifications are returned in registration order.
        """
        return iter(
            self._classifications.values()
        )

    def clear(self) -> None:
        """
        Remove all Classifications from the registry.
        """
        self._classifications.clear()
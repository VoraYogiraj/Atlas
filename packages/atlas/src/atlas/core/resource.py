"""
Atlas Resource

Defines the base engineering entity used throughout Atlas.

Specification:
    ENG-001 through ENG-010
"""

from __future__ import annotations

from typing import Any

from atlas.core.aid import AtlasID


class AtlasResource:
    """
    Base class for every Atlas Resource.

    Every engineering entity in Atlas inherits from this class.
    """

    def __init__(
        self,
        *,
        classification: str,
        name: str | None = None,
    ) -> None:

        self._id = AtlasID.generate()

        self._classification = classification

        self._name = name

        self._properties: dict[str, Any] = {}

        self._relationships: list[Any] = []

        self._metadata: dict[str, Any] = {}

        self._lifecycle = "created"

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def aid(self) -> AtlasID:
        """Return the Atlas ID."""
        return self._id

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    @property
    def classification(self) -> str:
        return self._classification

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        self._name = value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def properties(self) -> dict[str, Any]:
        return self._properties

    def set_property(self, key: str, value: Any) -> None:
        self._properties[key] = value

    def get_property(self, key: str) -> Any:
        return self._properties.get(key)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    @property
    def relationships(self) -> list[Any]:
        return self._relationships

    def add_relationship(self, relationship: Any) -> None:
        self._relationships.append(relationship)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @property
    def lifecycle(self) -> str:
        return self._lifecycle

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aid={self.aid}, "
            f"classification='{self.classification}')"
        )
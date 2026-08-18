"""
Atlas Resource Registry

Provides controlled registration and lookup of Atlas Resources.

The Registry is an explicit container owned by a higher-level Atlas
context such as a Project. It is not a global singleton.

Specification:
ENG-008 — Resource Registry
ENG-021 — Resource Classification Queries
"""

from __future__ import annotations

from collections.abc import Iterator

from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource


class AtlasResourceRegistry:
    """
    Registry of Atlas Resources.

    Resources are indexed by their immutable AtlasID.

    The Registry provides:
        - registration
        - lookup
        - existence checks
        - classification queries
        - removal
        - iteration
        - count
    """

    def __init__(self) -> None:
        self._resources: dict[AtlasID, AtlasResource] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        resource: AtlasResource,
    ) -> None:
        """
        Register a Resource.

        Raises
        ------
        TypeError
            If resource is not an AtlasResource.

        ValueError
            If a Resource with the same AtlasID is already registered.
        """
        if not isinstance(resource, AtlasResource):
            raise TypeError(
                "resource must be an AtlasResource"
            )

        if resource.aid in self._resources:
            raise ValueError(
                f"Resource already registered: {resource.aid}"
            )

        self._resources[resource.aid] = resource

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        aid: AtlasID,
    ) -> AtlasResource | None:
        """
        Return a Resource by AtlasID.

        Returns None when the Resource is not registered.
        """
        return self._resources.get(aid)

    def require(
        self,
        aid: AtlasID,
    ) -> AtlasResource:
        """
        Return a Resource by AtlasID.

        Raises
        ------
        KeyError
            If the Resource is not registered.
        """
        try:
            return self._resources[aid]
        except KeyError:
            raise KeyError(
                f"Resource not found: {aid}"
            ) from None

    # ------------------------------------------------------------------
    # Classification Queries
    # ------------------------------------------------------------------

    def for_classification(
        self,
        classification_id: str,
    ) -> list[AtlasResource]:
        """
        Return all Resources belonging to a classification.

        Resources are returned in registration order.

        Classification matching is performed by classification ID,
        not by classification object identity.

        Parameters
        ----------
        classification_id:
            ID of the Resource classification.

        Raises
        ------
        ValueError
            If classification_id is empty or whitespace.
        """
        if not classification_id.strip():
            raise ValueError(
                "Classification ID cannot be empty"
            )

        return [
            resource
            for resource in self._resources.values()
            if resource.classification.id == classification_id
        ]

    # ------------------------------------------------------------------
    # Existence
    # ------------------------------------------------------------------

    def contains(
        self,
        aid: AtlasID,
    ) -> bool:
        """Return True if a Resource is registered."""
        return aid in self._resources

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def unregister(
        self,
        aid: AtlasID,
    ) -> AtlasResource | None:
        """
        Remove and return a Resource.

        Returns None when the Resource is not registered.
        """
        return self._resources.pop(aid, None)

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Return the number of registered Resources."""
        return len(self._resources)

    def __len__(self) -> int:
        """Return the number of registered Resources."""
        return len(self._resources)

    def __iter__(
        self,
    ) -> Iterator[AtlasResource]:
        """Iterate over registered Resources."""
        return iter(self._resources.values())

    def clear(self) -> None:
        """Remove all registered Resources."""
        self._resources.clear()
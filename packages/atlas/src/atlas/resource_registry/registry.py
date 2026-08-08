"""
Atlas Resource Registry

Provides controlled registration and lookup of Atlas Resources.

The Registry is an explicit container owned by a higher-level Atlas
context such as a Project. It is not a global singleton.

Specification:
    ENG-008 — Resource Registry
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
        - removal
        - iteration
        - count
    """

    def __init__(self) -> None:
        self._resources: dict[AtlasID, AtlasResource] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, resource: AtlasResource) -> None:
        """
        Register a Resource.

        Raises
        ------
        ValueError
            If a Resource with the same AtlasID is already registered.
        """
        if resource.aid in self._resources:
            raise ValueError(
                f"Resource already registered: {resource.aid}"
            )

        self._resources[resource.aid] = resource

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, aid: AtlasID) -> AtlasResource | None:
        """
        Return a Resource by AtlasID.

        Returns None when the Resource is not registered.
        """
        return self._resources.get(aid)

    def require(self, aid: AtlasID) -> AtlasResource:
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
            raise KeyError(f"Resource not found: {aid}") from None

    # ------------------------------------------------------------------
    # Existence
    # ------------------------------------------------------------------

    def contains(self, aid: AtlasID) -> bool:
        """Return True if a Resource is registered."""
        return aid in self._resources

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def unregister(self, aid: AtlasID) -> AtlasResource | None:
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

    def __iter__(self) -> Iterator[AtlasResource]:
        """Iterate over registered Resources."""
        return iter(self._resources.values())

    def clear(self) -> None:
        """Remove all registered Resources."""
        self._resources.clear()
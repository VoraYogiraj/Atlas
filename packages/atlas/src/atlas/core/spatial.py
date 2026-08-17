"""
Atlas Spatial State

ENG-053 — Atlas Resource Move

Canonical spatial state associated with Atlas Resources.

Spatial state is intentionally separate from AtlasResource.
Resources are identified by AtlasID and their spatial state is maintained
in a project-scoped registry.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from atlas.core.aid import AtlasID


@dataclass(frozen=True, slots=True)
class AtlasSpatialPosition:
    """
    Absolute 3D position associated with an Atlas Resource.
    """

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        for axis, value in (
            ("x", self.x),
            ("y", self.y),
            ("z", self.z),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(
                    f"{axis} must be a numeric value"
                )

            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{axis} must be finite"
                )

    def as_mapping(self) -> dict[str, float]:
        """Return a read-safe mapping representation."""
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }


class AtlasSpatialStateRegistry:
    """
    Project-scoped canonical spatial state registry.

    This registry never owns AtlasResource objects. It stores spatial state
    keyed exclusively by canonical AtlasID.
    """

    def __init__(self) -> None:
        self._positions: dict[AtlasID, AtlasSpatialPosition] = {}

    def set_position(
        self,
        resource_id: AtlasID,
        position: AtlasSpatialPosition,
    ) -> None:
        """Set the absolute position for a Resource."""
        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        if not isinstance(position, AtlasSpatialPosition):
            raise TypeError(
                "position must be an AtlasSpatialPosition"
            )

        self._positions[resource_id] = position

    def get_position(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialPosition | None:
        """Return a Resource position, or None when none is stored."""
        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return self._positions.get(resource_id)

    def require_position(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialPosition:
        """Return a required Resource position."""
        position = self.get_position(resource_id)

        if position is None:
            raise KeyError(
                f"No spatial state registered for Resource: {resource_id}"
            )

        return position

    def remove(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialPosition | None:
        """Remove spatial state associated with a Resource."""
        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return self._positions.pop(
            resource_id,
            None,
        )

    def contains(
        self,
        resource_id: AtlasID,
    ) -> bool:
        """Return whether spatial state exists for the Resource."""
        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return resource_id in self._positions

    @property
    def count(self) -> int:
        """Return the number of stored spatial states."""
        return len(self._positions)
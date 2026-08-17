"""
Atlas Spatial State

ENG-053 — Atlas Resource Move
ENG-054 — Atlas Resource Rotate
ENG-055 — Atlas Resource Scale

Canonical spatial state associated with Atlas Resources.

Spatial state is intentionally separate from AtlasResource and is
maintained in a Project-owned registry keyed by AtlasID.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from atlas.core.aid import AtlasID


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------


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
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{axis} must be a numeric value"
                )

            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{axis} must be finite"
                )

    def as_mapping(self) -> dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasSpatialRotation:
    """
    Absolute 3-component rotation associated with an Atlas Resource.

    ENG-054 represents rotation as three Euler components.
    The values are intentionally stored without imposing a unit
    conversion or normalization policy.
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
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{axis} must be a numeric value"
                )

            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{axis} must be finite"
                )

    def as_mapping(self) -> dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }


# ---------------------------------------------------------------------------
# Scale
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasSpatialScale:
    """
    Absolute positive 3-component scale associated with an Atlas Resource.

    ENG-055 represents scale as three independent positive finite
    numeric components.

    Scale is absolute, not multiplicative and not additive.
    Zero and negative values are invalid.
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
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{axis} must be a numeric value"
                )

            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{axis} must be finite"
                )

            if float(value) <= 0.0:
                raise ValueError(
                    f"{axis} must be greater than zero"
                )

    def as_mapping(self) -> dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }


# ---------------------------------------------------------------------------
# Spatial State Registry
# ---------------------------------------------------------------------------


class AtlasSpatialStateRegistry:
    """
    Project-scoped canonical spatial state registry.

    The registry stores only spatial state and never owns AtlasResource
    objects. AtlasID remains the canonical engineering identity.

    ENG-053 owns position.
    ENG-054 owns rotation.
    ENG-055 owns scale.
    """

    def __init__(self) -> None:
        self._positions: dict[
            AtlasID,
            AtlasSpatialPosition,
        ] = {}

        self._rotations: dict[
            AtlasID,
            AtlasSpatialRotation,
        ] = {}

        self._scales: dict[
            AtlasID,
            AtlasSpatialScale,
        ] = {}

    # ------------------------------------------------------------------
    # Position
    # ------------------------------------------------------------------

    def set_position(
        self,
        resource_id: AtlasID,
        position: AtlasSpatialPosition,
    ) -> None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        if not isinstance(
            position,
            AtlasSpatialPosition,
        ):
            raise TypeError(
                "position must be an AtlasSpatialPosition"
            )

        self._positions[resource_id] = position

    def get_position(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialPosition | None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return self._positions.get(
            resource_id
        )

    def require_position(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialPosition:
        position = self.get_position(
            resource_id
        )

        if position is None:
            raise KeyError(
                "No spatial position registered for Resource: "
                f"{resource_id}"
            )

        return position

    # ------------------------------------------------------------------
    # Rotation
    # ------------------------------------------------------------------

    def set_rotation(
        self,
        resource_id: AtlasID,
        rotation: AtlasSpatialRotation,
    ) -> None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        if not isinstance(
            rotation,
            AtlasSpatialRotation,
        ):
            raise TypeError(
                "rotation must be an AtlasSpatialRotation"
            )

        self._rotations[resource_id] = rotation

    def get_rotation(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialRotation | None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return self._rotations.get(
            resource_id
        )

    def require_rotation(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialRotation:
        rotation = self.get_rotation(
            resource_id
        )

        if rotation is None:
            raise KeyError(
                "No spatial rotation registered for Resource: "
                f"{resource_id}"
            )

        return rotation

    # ------------------------------------------------------------------
    # Scale
    # ------------------------------------------------------------------

    def set_scale(
        self,
        resource_id: AtlasID,
        scale: AtlasSpatialScale,
    ) -> None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        if not isinstance(
            scale,
            AtlasSpatialScale,
        ):
            raise TypeError(
                "scale must be an AtlasSpatialScale"
            )

        self._scales[resource_id] = scale

    def get_scale(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialScale | None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return self._scales.get(
            resource_id
        )

    def require_scale(
        self,
        resource_id: AtlasID,
    ) -> AtlasSpatialScale:
        scale = self.get_scale(
            resource_id
        )

        if scale is None:
            raise KeyError(
                "No spatial scale registered for Resource: "
                f"{resource_id}"
            )

        return scale

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def remove(
        self,
        resource_id: AtlasID,
    ) -> None:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        self._positions.pop(
            resource_id,
            None,
        )

        self._rotations.pop(
            resource_id,
            None,
        )

        self._scales.pop(
            resource_id,
            None,
        )

    def contains(
        self,
        resource_id: AtlasID,
    ) -> bool:
        if not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        return (
            resource_id in self._positions
            or resource_id in self._rotations
            or resource_id in self._scales
        )

    @property
    def count(self) -> int:
        """
        Return the number of Resources with any spatial state.
        """
        return len(
            set(self._positions)
            | set(self._rotations)
            | set(self._scales)
        )


__all__ = [
    "AtlasSpatialPosition",
    "AtlasSpatialRotation",
    "AtlasSpatialScale",
    "AtlasSpatialStateRegistry",
]
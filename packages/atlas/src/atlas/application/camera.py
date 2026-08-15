"""ENG-047 — Atlas Camera."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias


Vector3: TypeAlias = tuple[float, float, float]


def _non_empty_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty or whitespace")
    return value


def _vector3(value: object, name: str) -> Vector3:
    if isinstance(value, str) or not isinstance(value, Iterable):
        raise TypeError(f"{name} must be a three-component vector")

    components = tuple(value)
    if len(components) != 3:
        raise ValueError(f"{name} must contain exactly three components")

    if any(
        not isinstance(component, (int, float))
        or isinstance(component, bool)
        for component in components
    ):
        raise TypeError(f"{name} components must be numeric")

    return (
        float(components[0]),
        float(components[1]),
        float(components[2]),
    )


def _number(value: object, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    return float(value)


def _positive_number(value: object, name: str) -> float:
    number = _number(value, name)
    if number <= 0.0:
        raise ValueError(f"{name} must be greater than zero")
    return number


def _field_of_view(value: object) -> float:
    field_of_view = _number(value, "field_of_view_degrees")
    if not 0.0 < field_of_view < 180.0:
        raise ValueError(
            "field_of_view_degrees must be greater than 0 and less than 180"
        )
    return field_of_view


def _projection(value: object) -> str:
    projection = _non_empty_text(value, "projection")
    if projection not in {"perspective", "orthographic"}:
        raise ValueError(
            "projection must be 'perspective' or 'orthographic'"
        )
    return projection


def _clipping_planes(
    near_clip: object,
    far_clip: object,
) -> tuple[float, float]:
    near = _positive_number(near_clip, "near_clip")
    far = _positive_number(far_clip, "far_clip")
    if far <= near:
        raise ValueError("far_clip must be greater than near_clip")
    return near, far


class AtlasCamera:
    """
    Renderer-independent viewpoint presentation state.

    The Camera does not own a Scene, Workspace, Panel, or engineering model.
    Navigation and input behavior belong to ENG-048.
    """

    def __init__(
        self,
        *,
        camera_id: str,
        name: str,
        position: Vector3 = (0.0, 0.0, 10.0),
        target: Vector3 = (0.0, 0.0, 0.0),
        up: Vector3 = (0.0, 1.0, 0.0),
        projection: str = "perspective",
        field_of_view_degrees: float = 60.0,
        orthographic_scale: float = 10.0,
        near_clip: float = 0.1,
        far_clip: float = 10000.0,
    ) -> None:
        self._camera_id = _non_empty_text(camera_id, "camera_id")
        self._name = _non_empty_text(name, "name")

        # Validate every input before committing any observable state.
        validated_position = _vector3(position, "position")
        validated_target = _vector3(target, "target")
        validated_up = _vector3(up, "up")
        validated_projection = _projection(projection)
        validated_field_of_view = _field_of_view(field_of_view_degrees)
        validated_orthographic_scale = _positive_number(
            orthographic_scale,
            "orthographic_scale",
        )
        validated_near_clip, validated_far_clip = _clipping_planes(
            near_clip,
            far_clip,
        )

        self._position = validated_position
        self._target = validated_target
        self._up = validated_up
        self._projection = validated_projection
        self._field_of_view_degrees = validated_field_of_view
        self._orthographic_scale = validated_orthographic_scale
        self._near_clip = validated_near_clip
        self._far_clip = validated_far_clip

    @property
    def camera_id(self) -> str:
        """Return the stable presentation identity."""
        return self._camera_id

    @property
    def name(self) -> str:
        """Return the presentation name."""
        return self._name

    @property
    def position(self) -> Vector3:
        return self._position

    @property
    def target(self) -> Vector3:
        return self._target

    @property
    def up(self) -> Vector3:
        return self._up

    @property
    def projection(self) -> str:
        return self._projection

    @property
    def field_of_view_degrees(self) -> float:
        return self._field_of_view_degrees

    @property
    def orthographic_scale(self) -> float:
        return self._orthographic_scale

    @property
    def near_clip(self) -> float:
        return self._near_clip

    @property
    def far_clip(self) -> float:
        return self._far_clip

    def set_position(self, position: Vector3) -> None:
        """Replace the Camera position without defining navigation policy."""
        self._position = _vector3(position, "position")

    def set_target(self, target: Vector3) -> None:
        """Replace the Camera target without defining navigation policy."""
        self._target = _vector3(target, "target")

    def set_up(self, up: Vector3) -> None:
        """Replace the Camera up vector."""
        self._up = _vector3(up, "up")

    def set_projection(self, projection: str) -> None:
        """Set perspective or orthographic projection state."""
        self._projection = _projection(projection)

    def set_field_of_view_degrees(self, value: float) -> None:
        """Set validated perspective field-of-view state."""
        self._field_of_view_degrees = _field_of_view(value)

    def set_orthographic_scale(self, value: float) -> None:
        """Set validated orthographic projection scale."""
        self._orthographic_scale = _positive_number(
            value,
            "orthographic_scale",
        )

    def set_clipping_planes(
        self,
        near_clip: float,
        far_clip: float,
    ) -> None:
        """Atomically replace the validated clipping-plane pair."""
        near, far = _clipping_planes(near_clip, far_clip)
        self._near_clip = near
        self._far_clip = far

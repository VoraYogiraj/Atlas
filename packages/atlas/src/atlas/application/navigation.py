"""
ENG-048 — Atlas Navigation.

Renderer-independent navigation controller for AtlasCamera.

Navigation owns camera manipulation behavior. It does not own or redefine
camera, scene, resource, relationship, renderer, input, or selection state.
"""

from __future__ import annotations

import math
from typing import Final

from atlas.application.camera import AtlasCamera, Vector3


_EPSILON: Final[float] = 1e-12


def _number(value: object, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    return float(value)


def _vector_subtract(
    left: Vector3,
    right: Vector3,
) -> Vector3:
    return (
        left[0] - right[0],
        left[1] - right[1],
        left[2] - right[2],
    )


def _vector_add(
    left: Vector3,
    right: Vector3,
) -> Vector3:
    return (
        left[0] + right[0],
        left[1] + right[1],
        left[2] + right[2],
    )


def _vector_scale(
    vector: Vector3,
    scalar: float,
) -> Vector3:
    return (
        vector[0] * scalar,
        vector[1] * scalar,
        vector[2] * scalar,
    )


def _vector_length(vector: Vector3) -> float:
    return math.sqrt(
        vector[0] ** 2
        + vector[1] ** 2
        + vector[2] ** 2
    )


def _rotate_y(
    vector: Vector3,
    angle_radians: float,
) -> Vector3:
    cosine = math.cos(angle_radians)
    sine = math.sin(angle_radians)

    return (
        cosine * vector[0] + sine * vector[2],
        vector[1],
        -sine * vector[0] + cosine * vector[2],
    )


def _rotate_x(
    vector: Vector3,
    angle_radians: float,
) -> Vector3:
    cosine = math.cos(angle_radians)
    sine = math.sin(angle_radians)

    return (
        vector[0],
        cosine * vector[1] + sine * vector[2],
        -sine * vector[1] + cosine * vector[2],
    )


class AtlasNavigation:
    """
    Renderer-independent navigation controller for an AtlasCamera.

    AtlasNavigation manipulates the supplied AtlasCamera through its public
    state API. It does not own a Scene, Workspace, Renderer, Selection system,
    engineering Resource, or Relationship graph.
    """

    def __init__(
        self,
        *,
        camera: AtlasCamera,
    ) -> None:
        if not isinstance(camera, AtlasCamera):
            raise TypeError("camera must be an AtlasCamera")

        self._camera = camera

        self._initial_position = camera.position
        self._initial_target = camera.target
        self._initial_up = camera.up
        self._initial_projection = camera.projection
        self._initial_field_of_view_degrees = (
            camera.field_of_view_degrees
        )
        self._initial_orthographic_scale = camera.orthographic_scale
        self._initial_near_clip = camera.near_clip
        self._initial_far_clip = camera.far_clip

    @property
    def camera(self) -> AtlasCamera:
        """Return the Camera controlled by this Navigation instance."""
        return self._camera

    def orbit(
        self,
        *,
        delta_yaw_degrees: float,
        delta_pitch_degrees: float,
    ) -> None:
        """
        Orbit the camera around its target.

        Positive yaw rotates the camera around the world Y axis.
        Positive pitch rotates the camera upward around the X axis.

        The target remains unchanged and the camera-target distance is
        preserved.
        """
        yaw = _number(delta_yaw_degrees, "delta_yaw_degrees")
        pitch = _number(delta_pitch_degrees, "delta_pitch_degrees")

        offset = _vector_subtract(
            self._camera.position,
            self._camera.target,
        )

        yaw_radians = math.radians(yaw)
        pitch_radians = math.radians(pitch)

        rotated = _rotate_y(
            offset,
            yaw_radians,
        )

        rotated = _rotate_x(
            rotated,
            pitch_radians,
        )

        new_position = _vector_add(
            self._camera.target,
            rotated,
        )

        self._camera.set_position(new_position)

    def pan(
        self,
        *,
        delta_x: float,
        delta_y: float,
    ) -> None:
        """
        Pan the camera and target by the same world-space displacement.

        The relative camera-to-target vector is preserved.
        """
        x = _number(delta_x, "delta_x")
        y = _number(delta_y, "delta_y")

        displacement: Vector3 = (
            x,
            y,
            0.0,
        )

        new_position = _vector_add(
            self._camera.position,
            displacement,
        )

        new_target = _vector_add(
            self._camera.target,
            displacement,
        )

        self._camera.set_position(new_position)
        self._camera.set_target(new_target)

    def zoom(
        self,
        *,
        delta: float,
    ) -> None:
        """
        Zoom the Camera according to its projection mode.

        Perspective:
            Positive delta moves the camera toward its target.
            Negative delta moves it away.

        Orthographic:
            Positive delta decreases orthographic scale.
            Negative delta increases it.
        """
        value = _number(delta, "delta")

        if value == 0.0:
            return

        if self._camera.projection == "orthographic":
            new_scale = (
                self._camera.orthographic_scale - value
            )

            if new_scale <= 0.0:
                raise ValueError(
                    "zoom would produce a non-positive "
                    "orthographic scale"
                )

            self._camera.set_orthographic_scale(
                new_scale,
            )
            return

        offset = _vector_subtract(
            self._camera.position,
            self._camera.target,
        )

        distance = _vector_length(offset)

        new_distance = distance - value

        if new_distance <= _EPSILON:
            raise ValueError(
                "zoom would produce a non-positive "
                "camera distance"
            )

        direction = _vector_scale(
            offset,
            1.0 / distance,
        )

        new_position = _vector_add(
            self._camera.target,
            _vector_scale(
                direction,
                new_distance,
            ),
        )

        self._camera.set_position(new_position)

    def reset(self) -> None:
        """Restore the Camera to its initial navigation viewpoint."""
        self._camera.set_position(
            self._initial_position,
        )
        self._camera.set_target(
            self._initial_target,
        )
        self._camera.set_up(
            self._initial_up,
        )
        self._camera.set_projection(
            self._initial_projection,
        )
        self._camera.set_field_of_view_degrees(
            self._initial_field_of_view_degrees,
        )
        self._camera.set_orthographic_scale(
            self._initial_orthographic_scale,
        )
        self._camera.set_clipping_planes(
            self._initial_near_clip,
            self._initial_far_clip,
        )
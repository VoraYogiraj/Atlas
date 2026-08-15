"""
ENG-048 — Atlas Navigation tests.

RED-phase contract tests for the renderer-independent navigation controller.
"""

from __future__ import annotations

import math

import pytest

from atlas.application.camera import AtlasCamera
from atlas.application.navigation import AtlasNavigation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_camera(
    *,
    camera_id: str = "camera-1",
    name: str = "Main Camera",
    position: tuple[float, float, float] = (0.0, 0.0, 10.0),
    target: tuple[float, float, float] = (0.0, 0.0, 0.0),
    up: tuple[float, float, float] = (0.0, 1.0, 0.0),
    projection: str = "perspective",
    field_of_view_degrees: float = 60.0,
    orthographic_scale: float = 10.0,
    near_clip: float = 0.1,
    far_clip: float = 10000.0,
) -> AtlasCamera:
    return AtlasCamera(
        camera_id=camera_id,
        name=name,
        position=position,
        target=target,
        up=up,
        projection=projection,
        field_of_view_degrees=field_of_view_degrees,
        orthographic_scale=orthographic_scale,
        near_clip=near_clip,
        far_clip=far_clip,
    )


def assert_vector_close(
    actual: tuple[float, float, float],
    expected: tuple[float, float, float],
    *,
    abs_tol: float = 1e-9,
) -> None:
    assert len(actual) == 3
    assert len(expected) == 3

    for actual_component, expected_component in zip(
        actual,
        expected,
        strict=True,
    ):
        assert math.isclose(
            actual_component,
            expected_component,
            abs_tol=abs_tol,
            rel_tol=0.0,
        )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_navigation_constructs_with_camera() -> None:
    camera = make_camera()

    navigation = AtlasNavigation(camera=camera)

    assert navigation.camera is camera


def test_navigation_requires_atlas_camera() -> None:
    with pytest.raises(TypeError):
        AtlasNavigation(camera=object())  # type: ignore[arg-type]


def test_navigation_does_not_create_a_replacement_camera() -> None:
    camera = make_camera()

    navigation = AtlasNavigation(camera=camera)

    assert navigation.camera is camera
    assert navigation.camera.camera_id == "camera-1"


# ---------------------------------------------------------------------------
# Camera ownership / boundaries
# ---------------------------------------------------------------------------


def test_navigation_does_not_own_scene_state() -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    assert not hasattr(navigation, "scene")
    assert not hasattr(navigation, "scene_id")


def test_navigation_does_not_own_renderer_state() -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    assert not hasattr(navigation, "renderer")
    assert not hasattr(navigation, "viewport")


def test_navigation_does_not_own_selection_state() -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    assert not hasattr(navigation, "selected_node_id")
    assert not hasattr(navigation, "selection")


# ---------------------------------------------------------------------------
# Orbit
# ---------------------------------------------------------------------------


def test_orbit_zero_delta_does_not_change_camera() -> None:
    camera = make_camera()

    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position
    before_target = camera.target
    before_up = camera.up

    navigation.orbit(
        delta_yaw_degrees=0.0,
        delta_pitch_degrees=0.0,
    )

    assert camera.position == before_position
    assert camera.target == before_target
    assert camera.up == before_up


def test_orbit_yaw_rotates_camera_around_target() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.orbit(
        delta_yaw_degrees=90.0,
        delta_pitch_degrees=0.0,
    )

    assert_vector_close(
        camera.position,
        (10.0, 0.0, 0.0),
    )
    assert camera.target == (0.0, 0.0, 0.0)


def test_orbit_negative_yaw_rotates_in_opposite_direction() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.orbit(
        delta_yaw_degrees=-90.0,
        delta_pitch_degrees=0.0,
    )

    assert_vector_close(
        camera.position,
        (-10.0, 0.0, 0.0),
    )


def test_orbit_pitch_changes_camera_elevation() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.orbit(
        delta_yaw_degrees=0.0,
        delta_pitch_degrees=90.0,
    )

    assert_vector_close(
        camera.position,
        (0.0, 10.0, 0.0),
    )
    assert camera.target == (0.0, 0.0, 0.0)


def test_orbit_preserves_camera_target() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(2.0, 3.0, 4.0),
    )

    navigation = AtlasNavigation(camera=camera)

    original_target = camera.target

    navigation.orbit(
        delta_yaw_degrees=45.0,
        delta_pitch_degrees=15.0,
    )

    assert camera.target == original_target


def test_orbit_preserves_camera_distance_from_target() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.orbit(
        delta_yaw_degrees=37.0,
        delta_pitch_degrees=23.0,
    )

    distance = math.sqrt(
        sum(
            component * component
            for component in (
                camera.position[0] - camera.target[0],
                camera.position[1] - camera.target[1],
                camera.position[2] - camera.target[2],
            )
        )
    )

    assert math.isclose(
        distance,
        10.0,
        abs_tol=1e-9,
        rel_tol=0.0,
    )


@pytest.mark.parametrize(
    ("yaw", "pitch"),
    [
        ("90", 0.0),
        (90.0, "0"),
        (None, 0.0),
        (0.0, None),
        (True, 0.0),
        (0.0, False),
    ],
)
def test_orbit_rejects_non_numeric_deltas(
    yaw: object,
    pitch: object,
) -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position
    before_target = camera.target

    with pytest.raises(TypeError):
        navigation.orbit(
            delta_yaw_degrees=yaw,  # type: ignore[arg-type]
            delta_pitch_degrees=pitch,  # type: ignore[arg-type]
        )

    assert camera.position == before_position
    assert camera.target == before_target


# ---------------------------------------------------------------------------
# Pan
# ---------------------------------------------------------------------------


def test_pan_zero_delta_does_not_change_camera() -> None:
    camera = make_camera()

    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position
    before_target = camera.target

    navigation.pan(
        delta_x=0.0,
        delta_y=0.0,
    )

    assert camera.position == before_position
    assert camera.target == before_target


def test_pan_moves_camera_and_target_by_same_displacement() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.pan(
        delta_x=2.0,
        delta_y=3.0,
    )

    assert camera.position == (2.0, 3.0, 10.0)
    assert camera.target == (2.0, 3.0, 0.0)


def test_pan_preserves_camera_to_target_vector() -> None:
    camera = make_camera(
        position=(1.0, 2.0, 10.0),
        target=(1.0, 2.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    before_vector = tuple(
        position - target
        for position, target in zip(
            camera.position,
            camera.target,
            strict=True,
        )
    )

    navigation.pan(
        delta_x=-4.0,
        delta_y=7.0,
    )

    after_vector = tuple(
        position - target
        for position, target in zip(
            camera.position,
            camera.target,
            strict=True,
        )
    )

    assert_vector_close(after_vector, before_vector)


@pytest.mark.parametrize(
    ("delta_x", "delta_y"),
    [
        ("1", 0.0),
        (0.0, "1"),
        (None, 0.0),
        (0.0, None),
        (True, 0.0),
        (0.0, False),
    ],
)
def test_pan_rejects_non_numeric_deltas(
    delta_x: object,
    delta_y: object,
) -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position
    before_target = camera.target

    with pytest.raises(TypeError):
        navigation.pan(
            delta_x=delta_x,  # type: ignore[arg-type]
            delta_y=delta_y,  # type: ignore[arg-type]
        )

    assert camera.position == before_position
    assert camera.target == before_target


# ---------------------------------------------------------------------------
# Zoom
# ---------------------------------------------------------------------------


def test_zoom_zero_delta_does_not_change_perspective_camera() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position

    navigation.zoom(delta=0.0)

    assert camera.position == before_position


def test_zoom_perspective_moves_camera_toward_target_for_positive_delta() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
        projection="perspective",
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.zoom(delta=2.0)

    assert_vector_close(
        camera.position,
        (0.0, 0.0, 8.0),
    )
    assert camera.target == (0.0, 0.0, 0.0)


def test_zoom_perspective_moves_camera_away_from_target_for_negative_delta() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
        projection="perspective",
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.zoom(delta=-2.0)

    assert_vector_close(
        camera.position,
        (0.0, 0.0, 12.0),
    )


def test_zoom_orthographic_changes_scale() -> None:
    camera = make_camera(
        projection="orthographic",
        orthographic_scale=10.0,
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.zoom(delta=2.0)

    assert camera.orthographic_scale == 8.0


def test_zoom_orthographic_negative_delta_increases_scale() -> None:
    camera = make_camera(
        projection="orthographic",
        orthographic_scale=10.0,
    )

    navigation = AtlasNavigation(camera=camera)

    navigation.zoom(delta=-2.0)

    assert camera.orthographic_scale == 12.0


def test_zoom_does_not_change_target() -> None:
    camera = make_camera(
        target=(1.0, 2.0, 3.0),
    )

    navigation = AtlasNavigation(camera=camera)

    original_target = camera.target

    navigation.zoom(delta=2.0)

    assert camera.target == original_target


@pytest.mark.parametrize(
    "delta",
    [
        "1",
        None,
        True,
        False,
    ],
)
def test_zoom_rejects_non_numeric_delta(delta: object) -> None:
    camera = make_camera()
    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position
    before_scale = camera.orthographic_scale

    with pytest.raises(TypeError):
        navigation.zoom(delta=delta)  # type: ignore[arg-type]

    assert camera.position == before_position
    assert camera.orthographic_scale == before_scale


def test_zoom_cannot_produce_invalid_perspective_distance() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 1.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    before_position = camera.position

    with pytest.raises(ValueError):
        navigation.zoom(delta=2.0)

    assert camera.position == before_position


def test_zoom_cannot_produce_non_positive_orthographic_scale() -> None:
    camera = make_camera(
        projection="orthographic",
        orthographic_scale=1.0,
    )

    navigation = AtlasNavigation(camera=camera)

    before_scale = camera.orthographic_scale

    with pytest.raises(ValueError):
        navigation.zoom(delta=2.0)

    assert camera.orthographic_scale == before_scale


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_restores_initial_perspective_camera_state() -> None:
    camera = make_camera(
        position=(0.0, 0.0, 10.0),
        target=(0.0, 0.0, 0.0),
    )

    navigation = AtlasNavigation(camera=camera)

    initial_position = camera.position
    initial_target = camera.target
    initial_up = camera.up
    initial_projection = camera.projection
    initial_fov = camera.field_of_view_degrees
    initial_scale = camera.orthographic_scale

    navigation.orbit(
        delta_yaw_degrees=45.0,
        delta_pitch_degrees=20.0,
    )
    navigation.pan(
        delta_x=3.0,
        delta_y=4.0,
    )
    navigation.zoom(delta=2.0)

    navigation.reset()

    assert camera.position == initial_position
    assert camera.target == initial_target
    assert camera.up == initial_up
    assert camera.projection == initial_projection
    assert camera.field_of_view_degrees == initial_fov
    assert camera.orthographic_scale == initial_scale


def test_reset_restores_initial_orthographic_camera_state() -> None:
    camera = make_camera(
        projection="orthographic",
        orthographic_scale=25.0,
    )

    navigation = AtlasNavigation(camera=camera)

    initial_position = camera.position
    initial_target = camera.target
    initial_scale = camera.orthographic_scale

    navigation.pan(
        delta_x=5.0,
        delta_y=-3.0,
    )
    navigation.zoom(delta=4.0)

    navigation.reset()

    assert camera.position == initial_position
    assert camera.target == initial_target
    assert camera.orthographic_scale == initial_scale


def test_reset_is_idempotent() -> None:
    camera = make_camera()

    navigation = AtlasNavigation(camera=camera)

    navigation.reset()
    first_reset_state = (
        camera.position,
        camera.target,
        camera.up,
        camera.orthographic_scale,
    )

    navigation.reset()
    second_reset_state = (
        camera.position,
        camera.target,
        camera.up,
        camera.orthographic_scale,
    )

    assert second_reset_state == first_reset_state


# ---------------------------------------------------------------------------
# Camera mutation boundary
# ---------------------------------------------------------------------------


def test_navigation_operations_mutate_the_supplied_camera_only() -> None:
    camera = make_camera()
    other_camera = make_camera(camera_id="camera-2")

    navigation = AtlasNavigation(camera=camera)

    other_position = other_camera.position
    other_target = other_camera.target

    navigation.pan(
        delta_x=2.0,
        delta_y=3.0,
    )

    assert other_camera.position == other_position
    assert other_camera.target == other_target


def test_navigation_does_not_change_camera_projection_during_pan() -> None:
    camera = make_camera(projection="perspective")
    navigation = AtlasNavigation(camera=camera)

    navigation.pan(
        delta_x=2.0,
        delta_y=3.0,
    )

    assert camera.projection == "perspective"


def test_navigation_does_not_change_camera_projection_during_orbit() -> None:
    camera = make_camera(projection="orthographic")
    navigation = AtlasNavigation(camera=camera)

    navigation.orbit(
        delta_yaw_degrees=30.0,
        delta_pitch_degrees=15.0,
    )

    assert camera.projection == "orthographic"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def test_navigation_is_exported_from_application_package() -> None:
    from atlas.application import AtlasNavigation

    assert AtlasNavigation is not None


def test_navigation_has_stable_public_class_name() -> None:
    assert AtlasNavigation.__name__ == "AtlasNavigation"
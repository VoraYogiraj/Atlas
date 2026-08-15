"""ENG-047 — Atlas Camera RED contract tests."""

from __future__ import annotations

import pytest


def _camera(**overrides):
    from atlas.application.camera import AtlasCamera

    values = {
        "camera_id": "main-camera",
        "name": "Main Camera",
    }
    values.update(overrides)
    return AtlasCamera(**values)


def _project():
    from atlas.project.project import AtlasProject

    return AtlasProject("Camera Project")


# ---------------------------------------------------------------------------
# Type, identity, and defaults
# ---------------------------------------------------------------------------


def test_camera_type_exists() -> None:
    from atlas.application.camera import AtlasCamera

    assert AtlasCamera is not None


def test_camera_exposes_identity_and_name() -> None:
    camera = _camera(camera_id="overview", name="Overview")

    assert camera.camera_id == "overview"
    assert camera.name == "Overview"


def test_camera_identity_is_not_atlas_identity() -> None:
    from atlas.core.aid import AtlasID

    assert not isinstance(_camera().camera_id, AtlasID)


@pytest.mark.parametrize("camera_id", ["", "   ", None, 1])
def test_camera_rejects_invalid_identity(camera_id: object) -> None:
    from atlas.application.camera import AtlasCamera

    with pytest.raises((TypeError, ValueError)):
        AtlasCamera(camera_id=camera_id, name="Camera")  # type: ignore[arg-type]


@pytest.mark.parametrize("name", ["", "   ", None, 1])
def test_camera_rejects_invalid_name(name: object) -> None:
    from atlas.application.camera import AtlasCamera

    with pytest.raises((TypeError, ValueError)):
        AtlasCamera(camera_id="main", name=name)  # type: ignore[arg-type]


def test_camera_has_exact_viewpoint_defaults() -> None:
    camera = _camera()

    assert camera.position == (0.0, 0.0, 10.0)
    assert camera.target == (0.0, 0.0, 0.0)
    assert camera.up == (0.0, 1.0, 0.0)


def test_camera_has_exact_projection_defaults() -> None:
    camera = _camera()

    assert camera.projection == "perspective"
    assert camera.field_of_view_degrees == 60.0
    assert camera.orthographic_scale == 10.0
    assert camera.near_clip == 0.1
    assert camera.far_clip == 10000.0


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("position", (1.0, 2.0)),
        ("target", "invalid"),
        ("up", (1.0, 2.0, "z")),
    ],
)
def test_camera_rejects_invalid_constructor_vectors(
    field: str,
    value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _camera(**{field: value})  # type: ignore[arg-type]


@pytest.mark.parametrize("projection", ["", "parallel", None, 1])
def test_camera_rejects_invalid_constructor_projection(
    projection: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _camera(projection=projection)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, 180, 181, "60", None])
def test_camera_rejects_invalid_constructor_field_of_view(
    value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _camera(field_of_view_degrees=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, "10", None])
def test_camera_rejects_invalid_constructor_orthographic_scale(
    value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _camera(orthographic_scale=value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "near_clip,far_clip",
    [(0, 1), (-1, 1), (1, 1), (2, 1), ("0.1", 10), (0.1, None)],
)
def test_camera_rejects_invalid_constructor_clipping_pair(
    near_clip: object,
    far_clip: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _camera(
            near_clip=near_clip,  # type: ignore[arg-type]
            far_clip=far_clip,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Direct, validated viewpoint state mutation
# ---------------------------------------------------------------------------


def test_camera_can_set_viewpoint_state() -> None:
    camera = _camera()

    camera.set_position((1.0, 2.0, 3.0))
    camera.set_target((4.0, 5.0, 6.0))
    camera.set_up((0.0, 0.0, 1.0))

    assert camera.position == (1.0, 2.0, 3.0)
    assert camera.target == (4.0, 5.0, 6.0)
    assert camera.up == (0.0, 0.0, 1.0)


@pytest.mark.parametrize("method", ["set_position", "set_target", "set_up"])
def test_camera_rejects_invalid_viewpoint_mutation_atomically(
    method: str,
) -> None:
    camera = _camera()
    before = getattr(camera, method.removeprefix("set_"))

    with pytest.raises((TypeError, ValueError)):
        getattr(camera, method)((1.0, 2.0))

    assert getattr(camera, method.removeprefix("set_")) == before


def test_camera_can_switch_projection() -> None:
    camera = _camera()

    camera.set_projection("orthographic")
    assert camera.projection == "orthographic"

    camera.set_projection("perspective")
    assert camera.projection == "perspective"


def test_camera_rejects_invalid_projection_atomically() -> None:
    camera = _camera()

    with pytest.raises((TypeError, ValueError)):
        camera.set_projection("parallel")

    assert camera.projection == "perspective"


def test_camera_can_set_projection_scalars() -> None:
    camera = _camera()

    camera.set_field_of_view_degrees(75.0)
    camera.set_orthographic_scale(25.0)

    assert camera.field_of_view_degrees == 75.0
    assert camera.orthographic_scale == 25.0


@pytest.mark.parametrize("method,value", [
    ("set_field_of_view_degrees", 0),
    ("set_field_of_view_degrees", 180),
    ("set_orthographic_scale", 0),
    ("set_orthographic_scale", -1),
])
def test_camera_rejects_invalid_projection_scalars_atomically(
    method: str,
    value: object,
) -> None:
    camera = _camera()
    property_name = {
        "set_field_of_view_degrees": "field_of_view_degrees",
        "set_orthographic_scale": "orthographic_scale",
    }[method]
    before = getattr(camera, property_name)

    with pytest.raises((TypeError, ValueError)):
        getattr(camera, method)(value)

    assert getattr(camera, property_name) == before


def test_camera_can_set_valid_clipping_planes() -> None:
    camera = _camera()

    camera.set_clipping_planes(0.5, 500.0)

    assert camera.near_clip == 0.5
    assert camera.far_clip == 500.0


@pytest.mark.parametrize("near_clip,far_clip", [(0, 1), (2, 1), (1, 1)])
def test_camera_rejects_invalid_clipping_planes_atomically(
    near_clip: object,
    far_clip: object,
) -> None:
    camera = _camera()
    before = (camera.near_clip, camera.far_clip)

    with pytest.raises((TypeError, ValueError)):
        camera.set_clipping_planes(near_clip, far_clip)  # type: ignore[arg-type]

    assert (camera.near_clip, camera.far_clip) == before


# ---------------------------------------------------------------------------
# Architecture boundaries
# ---------------------------------------------------------------------------


def test_camera_is_not_an_engineering_resource() -> None:
    from atlas.core.resource import AtlasResource

    assert not isinstance(_camera(), AtlasResource)


def test_camera_does_not_own_engineering_state() -> None:
    camera = _camera()

    for name in (
        "project",
        "resource",
        "resource_registry",
        "resource_graph",
        "relationships",
        "classification",
        "classification_registry",
    ):
        assert not hasattr(camera, name)


def test_camera_operations_do_not_mutate_project_state() -> None:
    project = _project()
    before = (project.resource_count, project.relationship_count)
    camera = _camera()

    camera.set_position((1.0, 2.0, 3.0))
    camera.set_projection("orthographic")
    camera.set_clipping_planes(0.5, 500.0)

    assert (project.resource_count, project.relationship_count) == before


def test_camera_is_independent_of_scene_workspace_and_panel() -> None:
    camera = _camera()

    for name in ("scene", "workspace", "panel", "scene_nodes"):
        assert not hasattr(camera, name)


def test_camera_is_renderer_independent() -> None:
    camera = _camera()

    for name in ("renderer", "engine", "mesh", "matrix", "gpu"):
        assert not hasattr(camera, name)


def test_camera_does_not_implement_navigation_or_interaction() -> None:
    camera = _camera()

    for name in (
        "orbit",
        "pan",
        "zoom",
        "fly",
        "pick",
        "raycast",
        "select",
        "handle_input",
    ):
        assert not hasattr(camera, name)


def test_camera_public_export_exists() -> None:
    from atlas import application

    assert hasattr(application, "AtlasCamera")

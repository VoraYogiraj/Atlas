"""ENG-051 — Atlas Basic Editing RED contract.

RED PHASE ONLY.
These tests intentionally target the ENG-051 public contract before
production implementation exists.

Do not weaken these tests to make the suite pass. Resolve the API/semantic
decisions in the ENG-051 specification first, then implement the minimum
capability required by this contract.
"""

from __future__ import annotations

import pytest

from atlas.application.basic_editing import AtlasBasicEditing
from atlas.application.scene import AtlasScene, AtlasSceneNode


@pytest.fixture
def scene() -> AtlasScene:
    value = AtlasScene(scene_id="scene-1", name="Test Scene")
    value.add_node(AtlasSceneNode(node_id="node-1", name="Test Node"))
    return value


@pytest.fixture
def editing() -> AtlasBasicEditing:
    return AtlasBasicEditing()


# ---------------------------------------------------------------------------
# Construction / public API
# ---------------------------------------------------------------------------

def test_basic_editing_is_constructible() -> None:
    value = AtlasBasicEditing()
    assert isinstance(value, AtlasBasicEditing)


def test_basic_editing_is_deterministic_on_construction() -> None:
    assert AtlasBasicEditing() == AtlasBasicEditing()


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

def test_translate_x_changes_only_position_x(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.translate(scene, "node-1", axis="x", value=5.0)
    assert node.position == (5.0, 0.0, 0.0)
    assert node.rotation == (0.0, 0.0, 0.0)
    assert node.scale == (1.0, 1.0, 1.0)


def test_translate_y_changes_only_position_y(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.translate(scene, "node-1", axis="y", value=5.0)
    assert node.position == (0.0, 5.0, 0.0)


def test_translate_z_changes_only_position_z(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.translate(scene, "node-1", axis="z", value=5.0)
    assert node.position == (0.0, 0.0, 5.0)


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------

def test_rotate_x_changes_only_rotation_x(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.rotate(scene, "node-1", axis="x", value=10.0)
    assert node.rotation == (10.0, 0.0, 0.0)
    assert node.position == (0.0, 0.0, 0.0)
    assert node.scale == (1.0, 1.0, 1.0)


def test_rotate_y_changes_only_rotation_y(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.rotate(scene, "node-1", axis="y", value=10.0)
    assert node.rotation == (0.0, 10.0, 0.0)


def test_rotate_z_changes_only_rotation_z(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.rotate(scene, "node-1", axis="z", value=10.0)
    assert node.rotation == (0.0, 0.0, 10.0)


# ---------------------------------------------------------------------------
# Scale
# ---------------------------------------------------------------------------

def test_scale_x_changes_only_scale_x(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.scale(scene, "node-1", axis="x", value=2.0)
    assert node.scale == (2.0, 1.0, 1.0)


def test_scale_y_changes_only_scale_y(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.scale(scene, "node-1", axis="y", value=2.0)
    assert node.scale == (1.0, 2.0, 1.0)


def test_scale_z_changes_only_scale_z(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    editing.scale(scene, "node-1", axis="z", value=2.0)
    assert node.scale == (1.0, 1.0, 2.0)


# ---------------------------------------------------------------------------
# Validation / atomicity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("axis", ["X", "Y", "Z", "", "w", None])
def test_invalid_axis_is_rejected_atomically(
    scene: AtlasScene,
    editing: AtlasBasicEditing,
    axis: object,
) -> None:
    node = scene.get_node("node-1")
    before = (node.position, node.rotation, node.scale)

    with pytest.raises((TypeError, ValueError)):
        editing.translate(scene, "node-1", axis=axis, value=5.0)

    assert (node.position, node.rotation, node.scale) == before


def test_unknown_node_is_rejected_without_mutation(
    scene: AtlasScene,
    editing: AtlasBasicEditing,
) -> None:
    with pytest.raises(KeyError):
        editing.translate(scene, "missing", axis="x", value=5.0)


@pytest.mark.parametrize("value", [True, "5", None, object()])
def test_invalid_transform_value_is_rejected_atomically(
    scene: AtlasScene,
    editing: AtlasBasicEditing,
    value: object,
) -> None:
    node = scene.get_node("node-1")
    before = (node.position, node.rotation, node.scale)

    with pytest.raises((TypeError, ValueError)):
        editing.translate(scene, "node-1", axis="x", value=value)

    assert (node.position, node.rotation, node.scale) == before


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_same_initial_state_and_operation_produce_same_result() -> None:
    left = AtlasScene(scene_id="scene-1", name="Test Scene")
    right = AtlasScene(scene_id="scene-2", name="Test Scene")
    left.add_node(AtlasSceneNode(node_id="node-1", name="Test Node"))
    right.add_node(AtlasSceneNode(node_id="node-1", name="Test Node"))

    AtlasBasicEditing().translate(left, "node-1", axis="x", value=5.0)
    AtlasBasicEditing().translate(right, "node-1", axis="x", value=5.0)

    assert left.get_node("node-1").position == right.get_node("node-1").position


# ---------------------------------------------------------------------------
# Isolation
# ---------------------------------------------------------------------------

def test_editing_does_not_change_scene_selection(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    scene.set_selected_node("node-1")
    editing.translate(scene, "node-1", axis="x", value=5.0)
    assert scene.selected_node_id == "node-1"


def test_editing_changes_scene_node_state_only(scene: AtlasScene, editing: AtlasBasicEditing) -> None:
    node = scene.get_node("node-1")
    before = (node.name, node.resource_id, node.parent_node_id, node.visible, node.order)

    editing.translate(scene, "node-1", axis="x", value=5.0)

    after = (node.name, node.resource_id, node.parent_node_id, node.visible, node.order)
    assert after == before


# ---------------------------------------------------------------------------
# Public export
# ---------------------------------------------------------------------------

def test_basic_editing_is_publicly_exported() -> None:
    from atlas.application import AtlasBasicEditing as Exported

    assert Exported is AtlasBasicEditing

"""ENG-046 conformance tests for AtlasScene."""

from __future__ import annotations

import pytest


def node(**overrides):
    from atlas.application.scene import AtlasSceneNode

    values = {"node_id": "node", "name": "Node"}
    values.update(overrides)
    return AtlasSceneNode(**values)


def scene():
    from atlas.application.scene import AtlasScene

    return AtlasScene(scene_id="main", name="Main Scene")


@pytest.mark.parametrize("value", ["", "   ", None, 1])
def test_scene_rejects_invalid_identity(value: object) -> None:
    from atlas.application.scene import AtlasScene

    with pytest.raises((TypeError, ValueError)):
        AtlasScene(scene_id=value, name="Scene")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "   ", None, 1])
def test_scene_rejects_invalid_name(value: object) -> None:
    from atlas.application.scene import AtlasScene

    with pytest.raises((TypeError, ValueError)):
        AtlasScene(scene_id="main", name=value)  # type: ignore[arg-type]


def test_scene_defaults() -> None:
    value = scene()

    assert value.scene_id == "main"
    assert value.name == "Main Scene"
    assert value.lifecycle == "created"
    assert value.nodes == ()
    assert value.root_nodes == ()
    assert value.is_loading is False
    assert value.error is None
    assert value.selected_node_id is None


@pytest.mark.parametrize("value", ["", "   ", None, 1])
def test_node_rejects_invalid_identity(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        node(node_id=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "   ", None, 1])
def test_node_rejects_invalid_name(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        node(name=value)  # type: ignore[arg-type]


def test_node_defaults_and_optional_resource_reference() -> None:
    value = node()

    assert value.resource_id is None
    assert value.parent_node_id is None
    assert value.position == (0.0, 0.0, 0.0)
    assert value.rotation == (0.0, 0.0, 0.0)
    assert value.scale == (1.0, 1.0, 1.0)
    assert value.visible is True
    assert value.order == 0


@pytest.mark.parametrize("value", ["id", 1])
def test_node_rejects_invalid_resource_identity(value: object) -> None:
    with pytest.raises(TypeError):
        node(resource_id=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["position", "rotation", "scale"])
@pytest.mark.parametrize("value", [(1.0, 2.0), "bad", (1.0, 2.0, "x")])
def test_node_rejects_invalid_vectors(field: str, value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        node(**{field: value})  # type: ignore[arg-type]


def test_node_rejects_invalid_visibility_and_order() -> None:
    with pytest.raises(TypeError):
        node(visible=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        node(order="1")  # type: ignore[arg-type]


def test_multiple_nodes_may_reference_one_resource() -> None:
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()
    value = scene()
    first = node(node_id="first", name="First", resource_id=resource_id)
    second = node(node_id="second", name="Second", resource_id=resource_id)

    value.add_node(first)
    value.add_node(second)

    assert value.nodes == (first, second)


def test_node_ids_are_unique_and_lookup_is_typed() -> None:
    value = scene()
    value.add_node(node())

    with pytest.raises(ValueError):
        value.add_node(node())
    with pytest.raises(TypeError):
        value.get_node(1)  # type: ignore[arg-type]
    with pytest.raises(KeyError):
        value.get_node("missing")


def test_construction_parent_must_exist_on_registration() -> None:
    value = scene()

    with pytest.raises(ValueError):
        value.add_node(node(parent_node_id="missing"))


def test_hierarchy_roots_and_ordering() -> None:
    value = scene()
    parent = node(node_id="parent", name="Parent", order=10)
    child = node(node_id="child", name="Child", parent_node_id="parent", order=0)
    first = node(node_id="first", name="First", order=0)
    value.add_node(parent)
    value.add_node(child)
    value.add_node(first)

    assert [item.node_id for item in value.nodes] == ["child", "first", "parent"]
    assert value.root_nodes == (first, parent)


def test_parent_mutation_rejects_unknown_self_and_cycles() -> None:
    value = scene()
    for node_id in ("a", "b", "c"):
        value.add_node(node(node_id=node_id, name=node_id))
    with pytest.raises(KeyError):
        value.set_parent("a", "missing")
    with pytest.raises(ValueError):
        value.set_parent("a", "a")
    value.set_parent("b", "a")
    value.set_parent("c", "b")
    with pytest.raises(ValueError):
        value.set_parent("a", "c")
    value.set_parent("b", None)
    assert value.get_node("b").parent_node_id is None


def test_node_removal_rejects_children_and_preserves_resources() -> None:
    value = scene()
    value.add_node(node(node_id="parent", name="Parent"))
    value.add_node(node(node_id="child", name="Child", parent_node_id="parent"))
    with pytest.raises(ValueError):
        value.remove_node("parent")
    assert value.remove_node("child").node_id == "child"


def test_selection_loading_and_error_contract() -> None:
    value = scene()
    value.add_node(node())
    value.set_selected_node("node")
    assert value.selected_node_id == "node"
    value.set_selected_node(None)
    value.set_loading(True)
    value.set_error("Load failed")
    assert value.is_loading is True
    assert value.error == "Load failed"
    with pytest.raises(ValueError):
        value.set_error("   ")
    value.set_error(None)
    assert value.error is None


def test_exact_lifecycle_includes_reactivation_and_disposal() -> None:
    value = scene()
    with pytest.raises(RuntimeError):
        value.activate()
    value.initialize()
    value.activate()
    value.deactivate()
    value.activate()
    value.deactivate()
    value.dispose()
    assert value.lifecycle == "disposed"
    with pytest.raises(RuntimeError):
        value.activate()


def test_scene_and_node_do_not_become_engineering_or_renderer_objects() -> None:
    from atlas.core.resource import AtlasResource

    value = scene()
    item = node()
    assert not isinstance(value, AtlasResource)
    assert not isinstance(item, AtlasResource)
    for name in ("project", "resource_registry", "resource_graph", "classification_registry", "renderer", "camera", "navigation", "gizmo"):
        assert not hasattr(value, name)
    for name in ("resource", "classification", "relationships", "mesh", "renderer"):
        assert not hasattr(item, name)


def test_public_exports() -> None:
    from atlas import application

    assert hasattr(application, "AtlasScene")
    assert hasattr(application, "AtlasSceneNode")

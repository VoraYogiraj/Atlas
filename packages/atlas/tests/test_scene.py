"""
ENG-046 — Atlas Scene

RED-phase tests for the framework-independent 3D Workspace Scene contract.

The Scene is presentation state.  It maps canonical Atlas resource identity to
spatial nodes; it must not create a second engineering graph, registry, or
classification model.
"""

from __future__ import annotations

import pytest


def _project():
    from atlas.project.project import AtlasProject

    return AtlasProject("Scene Project")


def _application():
    from atlas.application import AtlasApplication

    return AtlasApplication(_project())


def _scene(scene_id: str = "main", name: str = "Main Scene"):
    from atlas.application.scene import AtlasScene

    return AtlasScene(scene_id=scene_id, name=name)


def _node(
    node_id: str = "equipment-1",
    resource_id=None,
):
    from atlas.application.scene import AtlasSceneNode
    from atlas.core.aid import AtlasID

    return AtlasSceneNode(
        node_id=node_id,
        resource_id=resource_id or AtlasID.generate(),
    )


# ---------------------------------------------------------------------------
# Scene and node identity
# ---------------------------------------------------------------------------


def test_scene_type_exists() -> None:
    from atlas.application.scene import AtlasScene

    assert AtlasScene is not None


def test_scene_node_type_exists() -> None:
    from atlas.application.scene import AtlasSceneNode

    assert AtlasSceneNode is not None


def test_scene_has_stable_presentation_identity() -> None:
    scene = _scene("plant-3d", "Plant 3D")

    assert scene.scene_id == "plant-3d"


def test_scene_identity_is_not_atlas_identity() -> None:
    from atlas.core.aid import AtlasID

    assert not isinstance(_scene().scene_id, AtlasID)


def test_scene_name_is_available() -> None:
    assert _scene(name="Equipment Layout").name == "Equipment Layout"


@pytest.mark.parametrize("scene_id", ["", 42, None])
def test_scene_rejects_invalid_identity(scene_id: object) -> None:
    from atlas.application.scene import AtlasScene

    with pytest.raises((TypeError, ValueError)):
        AtlasScene(scene_id=scene_id, name="Scene")  # type: ignore[arg-type]


@pytest.mark.parametrize("name", ["", 42, None])
def test_scene_rejects_invalid_name(name: object) -> None:
    from atlas.application.scene import AtlasScene

    with pytest.raises((TypeError, ValueError)):
        AtlasScene(scene_id="main", name=name)  # type: ignore[arg-type]


def test_scene_node_has_stable_node_identity() -> None:
    assert _node("pump-node").node_id == "pump-node"


def test_scene_node_references_canonical_resource_identity() -> None:
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()

    assert _node(resource_id=resource_id).resource_id == resource_id


def test_scene_node_identity_is_not_atlas_identity() -> None:
    from atlas.core.aid import AtlasID

    assert not isinstance(_node().node_id, AtlasID)


@pytest.mark.parametrize("node_id", ["", 42, None])
def test_scene_node_rejects_invalid_node_identity(node_id: object) -> None:
    from atlas.application.scene import AtlasSceneNode
    from atlas.core.aid import AtlasID

    with pytest.raises((TypeError, ValueError)):
        AtlasSceneNode(node_id=node_id, resource_id=AtlasID.generate())  # type: ignore[arg-type]


@pytest.mark.parametrize("resource_id", ["resource", 42, None])
def test_scene_node_requires_atlas_id_reference(resource_id: object) -> None:
    from atlas.application.scene import AtlasSceneNode

    with pytest.raises(TypeError):
        AtlasSceneNode(node_id="node", resource_id=resource_id)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Lifecycle and presentation state
# ---------------------------------------------------------------------------


def test_scene_has_predictable_lifecycle() -> None:
    assert _scene().lifecycle == "created"


def test_scene_can_initialize_activate_deactivate_and_dispose() -> None:
    scene = _scene()

    scene.initialize()
    scene.activate()
    scene.deactivate()
    scene.dispose()

    assert scene.lifecycle == "disposed"


def test_scene_cannot_activate_before_initialization() -> None:
    with pytest.raises(RuntimeError):
        _scene().activate()


def test_scene_is_visible_by_default_and_visibility_is_reversible() -> None:
    scene = _scene()

    assert scene.visible is True
    scene.set_visible(False)
    scene.set_visible(True)

    assert scene.visible is True


def test_scene_supports_loading_state() -> None:
    scene = _scene()

    assert scene.is_loading is False
    scene.set_loading(True)

    assert scene.is_loading is True


def test_scene_supports_clearable_error_state() -> None:
    scene = _scene()

    scene.set_error("Renderer unavailable")
    assert scene.error == "Renderer unavailable"
    scene.set_error(None)

    assert scene.error is None


# ---------------------------------------------------------------------------
# Node registration, lookup, ordering, and removal
# ---------------------------------------------------------------------------


def test_scene_starts_empty() -> None:
    scene = _scene()

    assert scene.nodes == ()
    assert scene.root_nodes == ()
    assert scene.is_empty is True


def test_scene_can_register_node_and_lookup_by_node_identity() -> None:
    scene = _scene()
    node = _node("pump")

    scene.add_node(node)

    assert scene.get_node("pump") is node
    assert scene.nodes == (node,)
    assert scene.is_empty is False


def test_scene_rejects_duplicate_node_identity() -> None:
    scene = _scene()
    scene.add_node(_node("pump"))

    with pytest.raises(ValueError):
        scene.add_node(_node("pump"))


def test_scene_rejects_duplicate_resource_mapping() -> None:
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()
    scene = _scene()
    scene.add_node(_node("first", resource_id))

    with pytest.raises(ValueError):
        scene.add_node(_node("second", resource_id))


def test_scene_lookup_unknown_node_is_explicit() -> None:
    with pytest.raises(KeyError):
        _scene().get_node("missing")


def test_scene_can_lookup_node_by_resource_identity() -> None:
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()
    node = _node("pump", resource_id)
    scene = _scene()
    scene.add_node(node)

    assert scene.get_node_for_resource(resource_id) is node


def test_scene_unknown_resource_mapping_is_explicit() -> None:
    from atlas.core.aid import AtlasID

    with pytest.raises(KeyError):
        _scene().get_node_for_resource(AtlasID.generate())


def test_scene_nodes_are_deterministically_ordered() -> None:
    scene = _scene()
    for node_id in ("zeta", "alpha", "middle"):
        scene.add_node(_node(node_id))

    assert [node.node_id for node in scene.nodes] == [
        "alpha",
        "middle",
        "zeta",
    ]


def test_scene_can_remove_node() -> None:
    scene = _scene()
    node = _node("pump")
    scene.add_node(node)

    assert scene.remove_node("pump") is node
    assert scene.nodes == ()


def test_scene_removal_rejects_node_with_children() -> None:
    scene = _scene()
    scene.add_node(_node("parent"))
    scene.add_node(_node("child"))
    scene.set_parent("child", "parent")

    with pytest.raises(ValueError):
        scene.remove_node("parent")


# ---------------------------------------------------------------------------
# Spatial hierarchy
# ---------------------------------------------------------------------------


def test_node_defaults_to_root_without_parent() -> None:
    assert _node().parent_id is None


def test_scene_can_assign_parent_and_expose_children() -> None:
    scene = _scene()
    parent = _node("area")
    child = _node("pump")
    scene.add_node(parent)
    scene.add_node(child)

    scene.set_parent("pump", "area")

    assert child.parent_id == "area"
    assert scene.children_of("area") == (child,)
    assert scene.root_nodes == (parent,)


def test_scene_can_clear_parent_to_restore_root() -> None:
    scene = _scene()
    scene.add_node(_node("area"))
    child = _node("pump")
    scene.add_node(child)
    scene.set_parent("pump", "area")

    scene.set_parent("pump", None)

    assert child.parent_id is None
    assert [node.node_id for node in scene.root_nodes] == ["area", "pump"]


def test_scene_rejects_unknown_parent() -> None:
    scene = _scene()
    scene.add_node(_node("pump"))

    with pytest.raises(KeyError):
        scene.set_parent("pump", "missing")


def test_scene_rejects_self_parent() -> None:
    scene = _scene()
    scene.add_node(_node("pump"))

    with pytest.raises(ValueError):
        scene.set_parent("pump", "pump")


def test_scene_rejects_hierarchy_cycles() -> None:
    scene = _scene()
    for node_id in ("a", "b", "c"):
        scene.add_node(_node(node_id))
    scene.set_parent("b", "a")
    scene.set_parent("c", "b")

    with pytest.raises(ValueError):
        scene.set_parent("a", "c")


# ---------------------------------------------------------------------------
# Spatial presentation state
# ---------------------------------------------------------------------------


def test_scene_node_has_identity_transform_defaults() -> None:
    node = _node()

    assert node.position == (0.0, 0.0, 0.0)
    assert node.rotation == (0.0, 0.0, 0.0)
    assert node.scale == (1.0, 1.0, 1.0)


def test_scene_node_supports_spatial_transform_updates() -> None:
    node = _node()

    node.set_position((1.0, 2.0, 3.0))
    node.set_rotation((0.0, 90.0, 0.0))
    node.set_scale((2.0, 2.0, 2.0))

    assert node.position == (1.0, 2.0, 3.0)
    assert node.rotation == (0.0, 90.0, 0.0)
    assert node.scale == (2.0, 2.0, 2.0)


@pytest.mark.parametrize("transform", [(1.0, 2.0), "invalid", (1.0, 2.0, "x")])
def test_scene_node_rejects_invalid_transform_vectors(transform: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _node().set_position(transform)  # type: ignore[arg-type]


def test_scene_node_visibility_is_presentation_state() -> None:
    node = _node()

    assert node.visible is True
    node.set_visible(False)

    assert node.visible is False


# ---------------------------------------------------------------------------
# Scene selection and application/workspace boundaries
# ---------------------------------------------------------------------------


def test_scene_selection_is_node_identity_based() -> None:
    scene = _scene()
    scene.add_node(_node("pump"))

    scene.set_selected_node("pump")

    assert scene.selected_node_id == "pump"


def test_scene_selection_can_be_cleared() -> None:
    scene = _scene()
    scene.add_node(_node("pump"))
    scene.set_selected_node("pump")

    scene.set_selected_node(None)

    assert scene.selected_node_id is None


def test_scene_rejects_selection_of_unknown_node() -> None:
    with pytest.raises(KeyError):
        _scene().set_selected_node("missing")


def test_scene_can_be_hosted_by_workspace() -> None:
    from atlas.application.workspace import AtlasWorkspace

    scene = _scene()
    workspace = AtlasWorkspace(application=_application())

    workspace.set_scene(scene)

    assert workspace.scene is scene


def test_workspace_can_clear_scene() -> None:
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()
    workspace.set_scene(_scene())
    workspace.set_scene(None)

    assert workspace.scene is None


def test_workspace_rejects_invalid_scene() -> None:
    from atlas.application.workspace import AtlasWorkspace

    with pytest.raises(TypeError):
        AtlasWorkspace().set_scene("not a scene")  # type: ignore[arg-type]


def test_scene_remains_independent_of_renderer() -> None:
    scene = _scene()
    node = _node()

    assert not hasattr(scene, "renderer")
    assert not hasattr(scene, "engine")
    assert not hasattr(node, "renderer")
    assert not hasattr(node, "mesh")


# ---------------------------------------------------------------------------
# Engineering-state isolation and public API
# ---------------------------------------------------------------------------


def test_scene_and_node_are_not_engineering_resources() -> None:
    from atlas.core.resource import AtlasResource

    assert not isinstance(_scene(), AtlasResource)
    assert not isinstance(_node(), AtlasResource)


def test_scene_does_not_own_project_engineering_graph_or_registry() -> None:
    scene = _scene()

    for name in (
        "project",
        "resource_registry",
        "resource_graph",
        "relationship_registry",
        "classification_registry",
    ):
        assert not hasattr(scene, name)


def test_scene_node_does_not_copy_resource_or_classification() -> None:
    node = _node()

    for name in ("resource", "atlas_resource", "classification", "relationships"):
        assert not hasattr(node, name)


def test_scene_operations_do_not_mutate_project_state() -> None:
    project = _project()
    before = (project.resource_count, project.relationship_count)
    scene = _scene()
    node = _node()

    scene.add_node(node)
    node.set_position((1.0, 2.0, 3.0))
    node.set_visible(False)
    scene.set_selected_node(node.node_id)

    assert (project.resource_count, project.relationship_count) == before


def test_scene_public_exports_exist() -> None:
    from atlas import application

    assert hasattr(application, "AtlasScene")
    assert hasattr(application, "AtlasSceneNode")

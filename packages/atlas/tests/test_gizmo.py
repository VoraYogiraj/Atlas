"""
ENG-050 — Atlas Gizmo

RED-phase contract tests.

These tests define the renderer-independent Gizmo contract before the
implementation exists.
"""

from __future__ import annotations

import pytest

from atlas.application.gizmo import AtlasGizmo


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestGizmoConstruction:
    def test_default_state(self) -> None:
        gizmo = AtlasGizmo()

        assert gizmo.mode == "translate"
        assert gizmo.active_axis is None
        assert gizmo.node_id is None
        assert gizmo.is_active is False

    def test_construction_requires_no_scene(self) -> None:
        gizmo = AtlasGizmo()

        assert gizmo is not None


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------


class TestGizmoModes:
    @pytest.mark.parametrize("mode", ["translate", "rotate", "scale"])
    def test_valid_modes(self, mode: str) -> None:
        gizmo = AtlasGizmo()

        gizmo.set_mode(mode=mode)

        assert gizmo.mode == mode

    @pytest.mark.parametrize(
        "mode",
        [
            "",
            " ",
            "invalid",
            "Translate",
            "ROTATE",
            "move",
        ],
    )
    def test_invalid_mode_rejected(self, mode: str) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(ValueError):
            gizmo.set_mode(mode=mode)

    @pytest.mark.parametrize("mode", [None, 1, 1.0, True, object()])
    def test_invalid_mode_type_rejected(self, mode: object) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(TypeError):
            gizmo.set_mode(mode=mode)  # type: ignore[arg-type]

    def test_mode_change_does_not_activate(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.set_mode(mode="rotate")

        assert gizmo.mode == "rotate"
        assert gizmo.is_active is False
        assert gizmo.node_id is None


# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------


class TestGizmoAxes:
    @pytest.mark.parametrize("axis", [None, "x", "y", "z"])
    def test_valid_axes(self, axis: str | None) -> None:
        gizmo = AtlasGizmo()

        gizmo.set_axis(axis=axis)

        assert gizmo.active_axis == axis

    @pytest.mark.parametrize(
        "axis",
        [
            "",
            " ",
            "X",
            "xy",
            "xz",
            "yz",
            "xyz",
            "invalid",
        ],
    )
    def test_invalid_axis_rejected(self, axis: str) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(ValueError):
            gizmo.set_axis(axis=axis)

    @pytest.mark.parametrize("axis", [1, 1.0, True, object()])
    def test_invalid_axis_type_rejected(self, axis: object) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(TypeError):
            gizmo.set_axis(axis=axis)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Attachment
# ---------------------------------------------------------------------------


class TestGizmoAttachment:
    def test_attach_node(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")

        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False

    @pytest.mark.parametrize(
        "node_id",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
        ],
    )
    def test_empty_or_whitespace_node_id_rejected(self, node_id: str) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(ValueError):
            gizmo.attach(node_id=node_id)

    @pytest.mark.parametrize(
        "node_id",
        [
            None,
            1,
            1.0,
            True,
            object(),
        ],
    )
    def test_invalid_node_id_type_rejected(self, node_id: object) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(TypeError):
            gizmo.attach(node_id=node_id)  # type: ignore[arg-type]

    def test_attach_does_not_require_scene(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")

        assert gizmo.node_id == "wall-node"

    def test_attach_stores_identity_only(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")

        assert gizmo.node_id == "wall-node"

        assert not hasattr(gizmo, "scene")
        assert not hasattr(gizmo, "scene_node")


# ---------------------------------------------------------------------------
# Detachment
# ---------------------------------------------------------------------------


class TestGizmoDetachment:
    def test_detach(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")
        gizmo.detach()

        assert gizmo.node_id is None
        assert gizmo.is_active is False

    def test_detach_is_idempotent_when_inactive(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.detach()
        gizmo.detach()

        assert gizmo.node_id is None
        assert gizmo.is_active is False


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestGizmoLifecycle:
    def test_begin_requires_attachment(self) -> None:
        gizmo = AtlasGizmo()

        with pytest.raises(RuntimeError):
            gizmo.begin()

        assert gizmo.is_active is False

    def test_begin_activates_attached_gizmo(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")

        gizmo.begin()

        assert gizmo.is_active is True
        assert gizmo.node_id == "wall-node"

    def test_begin_twice_rejected(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.begin()

        with pytest.raises(RuntimeError):
            gizmo.begin()

        assert gizmo.is_active is True
        assert gizmo.node_id == "wall-node"

    def test_end_requires_active_gizmo(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")

        with pytest.raises(RuntimeError):
            gizmo.end()

        assert gizmo.is_active is False
        assert gizmo.node_id == "wall-node"

    def test_end_deactivates_gizmo(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.begin()

        gizmo.end()

        assert gizmo.is_active is False
        assert gizmo.node_id == "wall-node"

    def test_cancel_requires_active_gizmo(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")

        with pytest.raises(RuntimeError):
            gizmo.cancel()

        assert gizmo.is_active is False
        assert gizmo.node_id == "wall-node"

    def test_cancel_deactivates_gizmo(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.begin()

        gizmo.cancel()

        assert gizmo.is_active is False
        assert gizmo.node_id == "wall-node"

    def test_attach_while_active_rejected(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.begin()

        with pytest.raises(RuntimeError):
            gizmo.attach(node_id="column-node")

        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is True

    def test_detach_while_active_rejected(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.begin()

        with pytest.raises(RuntimeError):
            gizmo.detach()

        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is True


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestGizmoAtomicity:
    def test_invalid_mode_preserves_state(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.set_mode(mode="rotate")
        gizmo.set_axis(axis="z")

        with pytest.raises(ValueError):
            gizmo.set_mode(mode="invalid")

        assert gizmo.mode == "rotate"
        assert gizmo.active_axis == "z"
        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False

    def test_invalid_axis_preserves_state(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.set_mode(mode="rotate")
        gizmo.set_axis(axis="z")

        with pytest.raises(ValueError):
            gizmo.set_axis(axis="xy")

        assert gizmo.mode == "rotate"
        assert gizmo.active_axis == "z"
        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False

    def test_invalid_node_id_preserves_state(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")
        gizmo.set_mode(mode="scale")
        gizmo.set_axis(axis="y")

        with pytest.raises(ValueError):
            gizmo.attach(node_id=" ")

        assert gizmo.mode == "scale"
        assert gizmo.active_axis == "y"
        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False

    def test_invalid_node_type_preserves_state(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")

        with pytest.raises(TypeError):
            gizmo.attach(node_id=123)  # type: ignore[arg-type]

        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False

    def test_invalid_lifecycle_transition_preserves_state(self) -> None:
        gizmo = AtlasGizmo()
        gizmo.attach(node_id="wall-node")

        with pytest.raises(RuntimeError):
            gizmo.end()

        assert gizmo.node_id == "wall-node"
        assert gizmo.is_active is False


# ---------------------------------------------------------------------------
# Single target
# ---------------------------------------------------------------------------


class TestGizmoSingleTarget:
    def test_one_target_at_a_time(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")

        with pytest.raises(RuntimeError):
            gizmo.attach(node_id="column-node")

        assert gizmo.node_id == "wall-node"

    def test_new_target_allowed_after_detach(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")
        gizmo.detach()
        gizmo.attach(node_id="column-node")

        assert gizmo.node_id == "column-node"
        assert gizmo.is_active is False


# ---------------------------------------------------------------------------
# Scene / selection / engineering isolation
# ---------------------------------------------------------------------------


class TestGizmoIsolation:
    def test_no_scene_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "scene")

    def test_no_selection_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "selection")
        assert not hasattr(gizmo, "selection_state")

    def test_no_resource_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "resource")

    def test_no_relationship_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "relationship")

    def test_no_graph_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "graph")

    def test_no_project_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "project")

    def test_no_renderer_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "renderer")

    def test_no_raycasting_ownership(self) -> None:
        gizmo = AtlasGizmo()

        assert not hasattr(gizmo, "raycaster")

    def test_does_not_store_scene_node_object(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.attach(node_id="wall-node")

        assert gizmo.node_id == "wall-node"

        for attribute in ("scene_node", "node", "_node"):
            assert not hasattr(gizmo, attribute)


# ---------------------------------------------------------------------------
# Transformation boundary
# ---------------------------------------------------------------------------


class TestGizmoTransformationBoundary:
    def test_gizmo_has_no_transform_operation(self) -> None:
        gizmo = AtlasGizmo()

        forbidden = (
            "translate",
            "rotate",
            "scale",
            "set_position",
            "set_rotation",
            "set_scale",
        )

        for name in forbidden:
            assert not hasattr(gizmo, name)

    def test_mode_is_intent_only(self) -> None:
        gizmo = AtlasGizmo()

        gizmo.set_mode(mode="translate")
        gizmo.set_axis(axis="x")

        assert gizmo.mode == "translate"
        assert gizmo.active_axis == "x"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestGizmoDeterminism:
    def test_identical_operation_sequences_produce_same_state(self) -> None:
        first = AtlasGizmo()
        second = AtlasGizmo()

        for gizmo in (first, second):
            gizmo.set_mode(mode="rotate")
            gizmo.set_axis(axis="z")
            gizmo.attach(node_id="wall-node")
            gizmo.begin()
            gizmo.end()

        assert first.mode == second.mode
        assert first.active_axis == second.active_axis
        assert first.node_id == second.node_id
        assert first.is_active == second.is_active


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class TestGizmoPublicAPI:
    def test_module_export(self) -> None:
        from atlas.application.gizmo import AtlasGizmo as ImportedGizmo

        assert ImportedGizmo is AtlasGizmo

    def test_application_export(self) -> None:
        from atlas.application import AtlasGizmo as ImportedGizmo

        assert ImportedGizmo is AtlasGizmo
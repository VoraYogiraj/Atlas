"""
ENG-049 — Atlas Selection RED Tests

ENG-039 established AtlasResourceSelection as an identity-only value object:

    AtlasResourceSelection(resource_id=AtlasID(...))

ENG-049 must preserve that constructor contract while introducing the
workspace selection state required for:

- empty selection,
- resource selection,
- scene-node selection,
- clearing,
- replacement,
- atomicity,
- single selection,
- identity separation.

The existing AtlasResourceSelection class must not be weakened merely to
represent empty workspace selection.
"""

from __future__ import annotations

import importlib
import sys

import pytest

from atlas.application import AtlasResourceSelection
from atlas.core.aid import AtlasID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_resource_id() -> AtlasID:
    return AtlasID.generate()


def make_second_resource_id() -> AtlasID:
    return AtlasID.generate()


# ===========================================================================
# ENG-039 compatibility contract
# ===========================================================================


class TestExistingAtlasResourceSelectionContract:
    """
    These tests protect the existing ENG-039 API.

    ENG-049 must not break these semantics.
    """

    def test_resource_id_is_required(self) -> None:
        resource_id = make_resource_id()

        selection = AtlasResourceSelection(
            resource_id=resource_id,
        )

        assert selection.resource_id == resource_id

    def test_missing_resource_id_is_rejected(self) -> None:
        with pytest.raises(TypeError):
            AtlasResourceSelection()  # type: ignore[call-arg]

    def test_resource_id_must_be_atlas_id(self) -> None:
        with pytest.raises(
            TypeError,
            match="resource_id must be an AtlasID",
        ):
            AtlasResourceSelection(
                resource_id="resource-001",  # type: ignore[arg-type]
            )

    def test_resource_id_identity_is_preserved(self) -> None:
        resource_id = make_resource_id()

        selection = AtlasResourceSelection(
            resource_id=resource_id,
        )

        assert selection.resource_id is resource_id

    def test_existing_class_remains_identity_only(self) -> None:
        selection = AtlasResourceSelection(
            resource_id=make_resource_id(),
        )

        assert hasattr(selection, "resource_id")

        # ENG-039 value object must not silently become a Scene/renderer
        # selection container.
        assert not hasattr(selection, "scene")
        assert not hasattr(selection, "renderer")
        assert not hasattr(selection, "resource")
        assert not hasattr(selection, "relationships")


# ===========================================================================
# ENG-049 selection-state construction
# ===========================================================================


class TestAtlasSelectionStateConstruction:
    """
    ENG-049 requires an application-level selection state capable of being
    empty.

    The exact class name/API should be resolved by implementation against
    the existing architecture. These tests intentionally describe the
    required capability rather than weakening AtlasResourceSelection.
    """

    def test_empty_selection_is_valid(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False

    def test_empty_selection_does_not_require_resource_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert selection.resource_id is None

    def test_empty_selection_is_distinct_from_resource_value_object(
        self,
    ) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()

        resource_selection = AtlasResourceSelection(
            resource_id=resource_id,
        )

        empty_selection = AtlasSelectionState()

        assert resource_selection.resource_id == resource_id
        assert empty_selection.resource_id is None


# ===========================================================================
# Resource selection
# ===========================================================================


class TestResourceSelectionState:
    def test_select_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        assert selection.resource_id == resource_id
        assert selection.node_id is None
        assert selection.is_selected is True

    def test_select_resource_accepts_atlas_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        assert isinstance(selection.resource_id, AtlasID)

    def test_select_resource_rejects_invalid_resource_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        with pytest.raises(TypeError):
            selection.select_resource(
                resource_id="invalid",  # type: ignore[arg-type]
            )

    def test_select_resource_replaces_existing_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        first = make_resource_id()
        second = make_second_resource_id()

        selection = AtlasSelectionState()

        selection.select_resource(resource_id=first)
        selection.select_resource(resource_id=second)

        assert selection.resource_id == second
        assert selection.node_id is None
        assert selection.is_selected is True


# ===========================================================================
# Node selection
# ===========================================================================


class TestNodeSelectionState:
    def test_select_node_without_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
        )

        assert selection.node_id == "node-001"
        assert selection.resource_id is None
        assert selection.is_selected is True

    def test_select_node_with_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
            resource_id=resource_id,
        )

        assert selection.node_id == "node-001"
        assert selection.resource_id == resource_id
        assert selection.is_selected is True

    def test_select_node_replaces_previous_node(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        first = make_resource_id()
        second = make_second_resource_id()

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
            resource_id=first,
        )

        selection.select_node(
            node_id="node-002",
            resource_id=second,
        )

        assert selection.node_id == "node-002"
        assert selection.resource_id == second
        assert selection.is_selected is True

    def test_select_node_rejects_non_string_node_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        with pytest.raises(TypeError):
            selection.select_node(
                node_id=123,  # type: ignore[arg-type]
            )

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
    def test_select_node_rejects_empty_or_whitespace_node_id(
        self,
        node_id: str,
    ) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        with pytest.raises(ValueError):
            selection.select_node(
                node_id=node_id,
            )

    def test_select_node_rejects_invalid_resource_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        with pytest.raises(TypeError):
            selection.select_node(
                node_id="node-001",
                resource_id="invalid",  # type: ignore[arg-type]
            )


# ===========================================================================
# Clearing
# ===========================================================================


class TestSelectionClearing:
    def test_clear_empty_selection_is_valid(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.clear()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False

    def test_clear_resource_selection(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=make_resource_id(),
        )

        selection.clear()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False

    def test_clear_node_selection(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
        )

        selection.clear()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False

    def test_clear_combined_selection(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
            resource_id=make_resource_id(),
        )

        selection.clear()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False

    def test_clear_is_idempotent(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.clear()
        selection.clear()
        selection.clear()

        assert selection.resource_id is None
        assert selection.node_id is None
        assert selection.is_selected is False


# ===========================================================================
# Replacement / single-selection invariant
# ===========================================================================


class TestSingleSelectionInvariant:
    def test_resource_replaces_previous_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        first = make_resource_id()
        second = make_second_resource_id()

        selection = AtlasSelectionState()

        selection.select_resource(resource_id=first)
        selection.select_resource(resource_id=second)

        assert selection.resource_id == second
        assert selection.node_id is None

    def test_node_replaces_resource_selection(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()

        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        selection.select_node(
            node_id="node-001",
        )

        assert selection.resource_id is None
        assert selection.node_id == "node-001"
        assert selection.is_selected is True

    def test_resource_replaces_node_selection(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
        )

        selection.select_resource(
            resource_id=resource_id,
        )

        assert selection.resource_id == resource_id
        assert selection.node_id is None
        assert selection.is_selected is True

    def test_only_one_selection_is_active(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        first = make_resource_id()
        second = make_second_resource_id()

        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=first,
        )

        selection.select_node(
            node_id="node-002",
            resource_id=second,
        )

        assert selection.is_selected is True
        assert selection.resource_id == second
        assert selection.node_id == "node-002"


# ===========================================================================
# Atomicity
# ===========================================================================


class TestSelectionAtomicity:
    def test_invalid_resource_selection_preserves_existing_state(
        self,
    ) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        with pytest.raises(TypeError):
            selection.select_resource(
                resource_id="invalid",  # type: ignore[arg-type]
            )

        assert selection.resource_id == resource_id
        assert selection.node_id is None
        assert selection.is_selected is True

    def test_invalid_node_selection_preserves_existing_state(
        self,
    ) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        with pytest.raises(ValueError):
            selection.select_node(
                node_id="",
            )

        assert selection.resource_id == resource_id
        assert selection.node_id is None
        assert selection.is_selected is True

    def test_invalid_node_resource_id_preserves_existing_state(
        self,
    ) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        with pytest.raises(TypeError):
            selection.select_node(
                node_id="node-002",
                resource_id="invalid",  # type: ignore[arg-type]
            )

        assert selection.resource_id == resource_id
        assert selection.node_id is None
        assert selection.is_selected is True


# ===========================================================================
# Identity separation
# ===========================================================================


class TestIdentitySeparation:
    def test_resource_identity_is_atlas_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        assert isinstance(selection.resource_id, AtlasID)

    def test_node_identity_is_string(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
        )

        assert isinstance(selection.node_id, str)
        assert not isinstance(selection.node_id, AtlasID)

    def test_resource_and_node_identity_are_distinct(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
            resource_id=resource_id,
        )

        assert selection.resource_id == resource_id
        assert selection.node_id == "node-001"
        assert selection.resource_id != selection.node_id

    def test_multiple_nodes_can_reference_same_resource(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()

        first = AtlasSelectionState()
        second = AtlasSelectionState()

        first.select_node(
            node_id="node-001",
            resource_id=resource_id,
        )

        second.select_node(
            node_id="node-002",
            resource_id=resource_id,
        )

        assert first.resource_id == second.resource_id
        assert first.node_id != second.node_id


# ===========================================================================
# Scene independence
# ===========================================================================


class TestSceneIndependence:
    def test_empty_selection_requires_no_scene(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert selection is not None

    def test_resource_selection_requires_no_scene(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=make_resource_id(),
        )

        assert selection.is_selected is True

    def test_node_selection_does_not_require_scene_instance(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_node(
            node_id="node-001",
        )

        assert selection.node_id == "node-001"

    def test_selection_does_not_own_scene(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "scene")


# ===========================================================================
# Renderer independence
# ===========================================================================


class TestRendererIndependence:
    def test_selection_has_no_renderer(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "renderer")

    def test_selection_has_no_three_js_object(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "object3d")
        assert not hasattr(selection, "mesh")
        assert not hasattr(selection, "material")

    def test_selection_has_no_raycaster(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "raycaster")

    def test_three_js_is_not_required(self) -> None:
        assert "three" not in sys.modules


# ===========================================================================
# Engineering isolation
# ===========================================================================


class TestEngineeringIsolation:
    def test_selection_does_not_own_resource_object(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=make_resource_id(),
        )

        assert not hasattr(selection, "resource")

    def test_selection_does_not_own_relationships(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "relationships")

    def test_selection_does_not_own_graph(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "graph")

    def test_selection_does_not_own_project(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        selection = AtlasSelectionState()

        assert not hasattr(selection, "project")

    def test_clear_does_not_mutate_atlas_id(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_id = make_resource_id()
        selection = AtlasSelectionState()

        selection.select_resource(
            resource_id=resource_id,
        )

        selection.clear()

        # AtlasID itself remains intact; only selection state changed.
        assert isinstance(resource_id, AtlasID)


# ===========================================================================
# Determinism
# ===========================================================================


class TestSelectionDeterminism:
    def test_same_operation_sequence_produces_same_state(self) -> None:
        from atlas.application.selection import AtlasSelectionState

        resource_a = make_resource_id()
        resource_b = make_second_resource_id()

        first = AtlasSelectionState()
        second = AtlasSelectionState()

        first.select_resource(resource_id=resource_a)
        second.select_resource(resource_id=resource_a)

        first.select_node(
            node_id="node-001",
            resource_id=resource_b,
        )
        second.select_node(
            node_id="node-001",
            resource_id=resource_b,
        )

        first.clear()
        second.clear()

        assert first.resource_id == second.resource_id
        assert first.node_id == second.node_id
        assert first.is_selected == second.is_selected


# ===========================================================================
# Public exports
# ===========================================================================


class TestPublicExports:
    def test_existing_resource_selection_export_is_preserved(self) -> None:
        from atlas.application import AtlasResourceSelection as exported

        assert exported is AtlasResourceSelection

    def test_new_selection_state_is_publicly_exported(self) -> None:
        from atlas.application import AtlasSelectionState as exported

        from atlas.application.selection import AtlasSelectionState

        assert exported is AtlasSelectionState

    def test_selection_module_exports_both_layers(self) -> None:
        module = importlib.import_module(
            "atlas.application.selection",
        )

        assert module.AtlasResourceSelection is AtlasResourceSelection
        assert hasattr(module, "AtlasSelectionState")

    def test_application_package_does_not_replace_resource_selection(
        self,
    ) -> None:
        import atlas.application as application

        assert application.AtlasResourceSelection is AtlasResourceSelection
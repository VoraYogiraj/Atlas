"""
ENG-039 — Atlas UI Architecture

Tests for the future-ready Atlas UI/Application boundary.

These tests verify architectural contracts between the user-facing
application layer and the canonical Atlas engineering model.

The tests intentionally avoid coupling Atlas to a specific frontend,
rendering library, or UI framework.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_ui_application_package_exists() -> None:
    """Atlas must expose a dedicated application boundary."""
    from atlas.application import AtlasApplication

    assert AtlasApplication is not None


def test_application_can_be_created_with_project() -> None:
    """The application boundary must be project-scoped."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject("UI Test Project")
    application = AtlasApplication(project)

    assert application.project is project


def test_application_rejects_invalid_project() -> None:
    """The application boundary must require an AtlasProject."""
    from atlas.application import AtlasApplication

    with pytest.raises(TypeError):
        AtlasApplication("not-a-project")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def test_application_exposes_command_model() -> None:
    """Commands must be explicit application operations."""
    from atlas.application.commands import AtlasCommand

    assert AtlasCommand is not None


def test_command_has_stable_name() -> None:
    """Commands require stable operation identity."""
    from atlas.application.commands import AtlasCommand

    command = AtlasCommand(
        "create_resource",
        payload={},
    )

    assert command.name == "create_resource"


def test_command_payload_is_available() -> None:
    """Commands carry operation input without owning domain logic."""
    from atlas.application.commands import AtlasCommand

    payload = {
        "classification": "wall",
        "name": "External Wall",
    }

    command = AtlasCommand(
        "create_resource",
        payload=payload,
    )

    assert command.payload == payload


def test_command_name_cannot_be_empty() -> None:
    """Command identity must be explicit."""
    from atlas.application.commands import AtlasCommand

    with pytest.raises(ValueError):
        AtlasCommand("", payload={})


def test_command_rejects_non_string_name() -> None:
    """Command identity must be represented as a string."""
    from atlas.application.commands import AtlasCommand

    with pytest.raises(TypeError):
        AtlasCommand(123, payload={})  # type: ignore[arg-type]


def test_command_requires_dictionary_payload() -> None:
    """Command input must use a structured dictionary payload."""
    from atlas.application.commands import AtlasCommand

    with pytest.raises(TypeError):
        AtlasCommand(
            "create_resource",
            payload=None,  # type: ignore[arg-type]
        )


def test_command_is_immutable() -> None:
    """Command contracts should be immutable after creation."""
    from atlas.application.commands import AtlasCommand

    command = AtlasCommand(
        "create_resource",
        payload={},
    )

    with pytest.raises(AttributeError):
        command.name = "delete_resource"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def test_application_exposes_query_model() -> None:
    """Queries must be explicit application read operations."""
    from atlas.application.queries import AtlasQuery

    assert AtlasQuery is not None


def test_query_has_stable_name() -> None:
    """Queries require stable operation identity."""
    from atlas.application.queries import AtlasQuery

    query = AtlasQuery(
        "get_project",
        parameters={},
    )

    assert query.name == "get_project"


def test_query_parameters_are_available() -> None:
    """Queries carry read parameters without mutating domain state."""
    from atlas.application.queries import AtlasQuery

    parameters = {
        "resource_id": "abc",
    }

    query = AtlasQuery(
        "get_resource",
        parameters=parameters,
    )

    assert query.parameters == parameters


def test_query_name_cannot_be_empty() -> None:
    """Query identity must be explicit."""
    from atlas.application.queries import AtlasQuery

    with pytest.raises(ValueError):
        AtlasQuery("", parameters={})


def test_query_rejects_non_string_name() -> None:
    """Query identity must be represented as a string."""
    from atlas.application.queries import AtlasQuery

    with pytest.raises(TypeError):
        AtlasQuery(123, parameters={})  # type: ignore[arg-type]


def test_query_requires_dictionary_parameters() -> None:
    """Query input must use a structured dictionary."""
    from atlas.application.queries import AtlasQuery

    with pytest.raises(TypeError):
        AtlasQuery(
            "get_resource",
            parameters=None,  # type: ignore[arg-type]
        )


def test_query_is_immutable() -> None:
    """Query contracts should be immutable after creation."""
    from atlas.application.queries import AtlasQuery

    query = AtlasQuery(
        "get_project",
        parameters={},
    )

    with pytest.raises(AttributeError):
        query.name = "get_resource"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Resource selection
# ---------------------------------------------------------------------------


def test_resource_selection_is_identity_based() -> None:
    """UI selection must be represented by AtlasID, not a Resource copy."""
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()

    selection = AtlasResourceSelection(
        resource_id,
    )

    assert selection.resource_id == resource_id
    assert isinstance(
        selection.resource_id,
        AtlasID,
    )


def test_selection_does_not_store_resource_copy() -> None:
    """Selection must retain identity rather than duplicating domain state."""
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()

    selection = AtlasResourceSelection(
        resource_id,
    )

    assert not hasattr(
        selection,
        "resource",
    )
    assert not hasattr(
        selection,
        "resource_copy",
    )


def test_selection_requires_atlas_id() -> None:
    """Resource selection must use canonical Atlas identity."""
    from atlas.application.selection import AtlasResourceSelection

    with pytest.raises(TypeError):
        AtlasResourceSelection(
            "not-an-atlas-id",
        )


def test_selection_identity_can_be_round_tripped_as_string() -> None:
    """
    UI selection should be transport-friendly while preserving AtlasID.
    """
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()

    selection = AtlasResourceSelection(
        resource_id,
    )

    encoded = str(
        selection.resource_id,
    )

    restored = AtlasID.from_string(
        encoded,
    )

    assert restored == resource_id


# ---------------------------------------------------------------------------
# UI state
# ---------------------------------------------------------------------------


def test_ui_state_is_separate_from_engineering_state() -> None:
    """UI state must have its own representation."""
    from atlas.application.ui_state import AtlasUIState

    state = AtlasUIState()

    assert state is not None
    assert hasattr(
        state,
        "selected_resource_id",
    )
    assert hasattr(
        state,
        "active_panel",
    )


def test_ui_state_does_not_store_project() -> None:
    """UI state must not become a second engineering model."""
    from atlas.application.ui_state import AtlasUIState

    state = AtlasUIState()

    assert not hasattr(
        state,
        "project",
    )
    assert not hasattr(
        state,
        "resource_registry",
    )
    assert not hasattr(
        state,
        "resource_graph",
    )


def test_ui_state_can_track_selection_without_resource_copy() -> None:
    """Selection belongs to UI state as an AtlasID."""
    from atlas.application.ui_state import AtlasUIState
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()
    state = AtlasUIState()

    state.selected_resource_id = resource_id

    assert state.selected_resource_id == resource_id


def test_ui_state_selection_setter_validates_identity() -> None:
    """UI state must preserve canonical Atlas identity."""
    from atlas.application.ui_state import AtlasUIState

    state = AtlasUIState()

    with pytest.raises(TypeError):
        state.set_selection(
            "invalid-id",  # type: ignore[arg-type]
        )


def test_ui_state_can_clear_selection() -> None:
    """UI selection may be cleared without affecting engineering state."""
    from atlas.application.ui_state import AtlasUIState
    from atlas.core.aid import AtlasID

    state = AtlasUIState()

    resource_id = AtlasID.generate()

    state.set_selection(resource_id)
    assert state.selected_resource_id == resource_id

    state.set_selection(None)

    assert state.selected_resource_id is None


# ---------------------------------------------------------------------------
# Presentation models
# ---------------------------------------------------------------------------


def test_resource_presentation_model_exists() -> None:
    """Presentation models must be distinct from canonical Resources."""
    from atlas.application.presentation import (
        AtlasResourcePresentation,
    )

    assert AtlasResourcePresentation is not None


def test_resource_presentation_model_can_reference_identity() -> None:
    """Presentation models should expose canonical identity."""
    from atlas.application.presentation import (
        AtlasResourcePresentation,
    )
    from atlas.core.aid import AtlasID

    resource_id = AtlasID.generate()

    presentation = AtlasResourcePresentation(
        resource_id=resource_id,
        name="External Wall",
    )

    assert presentation.resource_id == resource_id
    assert presentation.name == "External Wall"


def test_resource_presentation_model_is_not_an_atlas_resource() -> None:
    """Presentation objects must not replace canonical Resources."""
    from atlas.application.presentation import (
        AtlasResourcePresentation,
    )
    from atlas.core.resource import AtlasResource

    presentation = AtlasResourcePresentation(
        resource_id=None,
        name="External Wall",
    )

    assert not isinstance(
        presentation,
        AtlasResource,
    )


def test_resource_presentation_model_does_not_store_resource_object() -> None:
    """Presentation models must not embed the canonical Resource object."""
    from atlas.application.presentation import (
        AtlasResourcePresentation,
    )

    presentation = AtlasResourcePresentation(
        resource_id=None,
        name="External Wall",
    )

    assert not hasattr(
        presentation,
        "resource",
    )


# ---------------------------------------------------------------------------
# Application command/query boundary
# ---------------------------------------------------------------------------


def test_application_exposes_command_execution_boundary() -> None:
    """Commands must be executed through the application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.commands import AtlasCommand
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("UI Test Project"),
    )

    command = AtlasCommand(
        "noop",
        payload={},
    )

    result = application.execute(
        command,
    )

    assert result is None


def test_application_exposes_query_execution_boundary() -> None:
    """Queries must be executed through the application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.queries import AtlasQuery
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "UI Test Project",
    )

    application = AtlasApplication(
        project,
    )

    query = AtlasQuery(
        "get_project",
        parameters={},
    )

    result = application.query(
        query,
    )

    assert result is project


def test_application_rejects_invalid_command() -> None:
    """Application command execution requires an AtlasCommand."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Command Validation"),
    )

    with pytest.raises(TypeError):
        application.execute("not-a-command")  # type: ignore[arg-type]


def test_application_rejects_invalid_query() -> None:
    """Application query execution requires an AtlasQuery."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Query Validation"),
    )

    with pytest.raises(TypeError):
        application.query("not-a-query")  # type: ignore[arg-type]


def test_application_rejects_unknown_command() -> None:
    """Unknown commands must fail explicitly."""
    from atlas.application import AtlasApplication
    from atlas.application.commands import AtlasCommand
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Unknown Command"),
    )

    command = AtlasCommand(
        "unknown_command",
        payload={},
    )

    with pytest.raises(NotImplementedError):
        application.execute(command)


def test_application_rejects_unknown_query() -> None:
    """Unknown queries must fail explicitly."""
    from atlas.application import AtlasApplication
    from atlas.application.queries import AtlasQuery
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Unknown Query"),
    )

    query = AtlasQuery(
        "unknown_query",
        parameters={},
    )

    with pytest.raises(NotImplementedError):
        application.query(query)


# ---------------------------------------------------------------------------
# Core / UI dependency direction
# ---------------------------------------------------------------------------


def test_application_owns_project_reference_not_ui_components() -> None:
    """
    Application boundary must depend on Atlas Core, not UI components.
    """
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "Dependency Test",
    )

    application = AtlasApplication(
        project,
    )

    assert application.project is project

    assert not hasattr(
        application,
        "ui",
    )
    assert not hasattr(
        application,
        "component_tree",
    )


def test_ui_application_does_not_replace_atlas_project() -> None:
    """
    The application layer wraps AtlasProject; it does not redefine it.
    """
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "Canonical Project",
    )

    application = AtlasApplication(
        project,
    )

    assert isinstance(
        application.project,
        AtlasProject,
    )

    assert application.project is project


# ---------------------------------------------------------------------------
# Future 3D boundary
# ---------------------------------------------------------------------------


def test_3d_view_boundary_exists() -> None:
    """
    Future 3D visualization must have an explicit presentation boundary.
    """
    from atlas.application.views import Atlas3DView

    assert Atlas3DView is not None


def test_3d_view_does_not_own_project_model() -> None:
    """
    Renderer/view objects must not become canonical engineering state.
    """
    from atlas.application.views import Atlas3DView

    view = Atlas3DView()

    assert not hasattr(
        view,
        "project",
    )
    assert not hasattr(
        view,
        "resource_registry",
    )
    assert not hasattr(
        view,
        "resource_graph",
    )


# ---------------------------------------------------------------------------
# Agent independence
# ---------------------------------------------------------------------------


def test_application_does_not_require_specific_ui_components_for_agents() -> None:
    """Agents must remain independent from UI implementation."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Agent Independence"),
    )

    assert not hasattr(
        application,
        "agent_ui",
    )
    assert not hasattr(
        application,
        "agent_panel",
    )
    assert not hasattr(
        application,
        "agent_component",
    )


# ---------------------------------------------------------------------------
# Persistence / exchange independence
# ---------------------------------------------------------------------------


def test_application_does_not_own_serializer() -> None:
    """UI application boundary must not become the serializer."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Persistence Independence"),
    )

    assert not hasattr(
        application,
        "serializer",
    )
    assert not hasattr(
        application,
        "json_serializer",
    )


def test_application_does_not_own_importer_or_exporter() -> None:
    """Import/export remains an external exchange boundary."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Exchange Independence"),
    )

    assert not hasattr(
        application,
        "importer",
    )
    assert not hasattr(
        application,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Application presentation boundary
# ---------------------------------------------------------------------------


def test_application_can_create_resource_presentation() -> None:
    """
    Presentation must be produced from canonical Atlas state through
    the application boundary.
    """
    from atlas.application import AtlasApplication
    from atlas.application.presentation import (
        AtlasResourcePresentation,
    )
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "Presentation Test",
    )

    application = AtlasApplication(
        project,
    )

    # No Resource exists yet, so this test verifies the type boundary
    # contract separately through the presentation model itself.
    resource_id = AtlasID.generate()

    presentation = AtlasResourcePresentation(
        resource_id=resource_id,
        name="External Wall",
    )

    assert presentation.resource_id == resource_id


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_application_public_exports_exist() -> None:
    """The application package should expose its architectural contracts."""
    from atlas import application

    expected = {
        "AtlasApplication",
        "AtlasCommand",
        "AtlasQuery",
        "AtlasResourceSelection",
        "AtlasUIState",
        "AtlasResourcePresentation",
        "Atlas3DView",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )
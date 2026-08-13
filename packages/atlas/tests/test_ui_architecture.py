"""
ENG-039 — Atlas UI Architecture

RED-phase tests for the future-ready UI/Application boundary.

These tests intentionally target architectural contracts that do not yet
exist in the Atlas implementation.
"""

from __future__ import annotations

from uuid import UUID

import pytest


# ---------------------------------------------------------------------------
# Application contracts
# ---------------------------------------------------------------------------


def test_ui_application_package_exists() -> None:
    """Atlas must expose a dedicated application boundary."""
    from atlas.application import AtlasApplication

    assert AtlasApplication is not None


def test_application_can_be_created_with_project() -> None:
    """The application boundary should be project-scoped."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject("UI Test Project")
    application = AtlasApplication(project)

    assert application.project is project


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

    command = AtlasCommand("create_resource", payload={})

    assert command.name == "create_resource"


def test_command_payload_is_available() -> None:
    """Commands carry operation input without owning domain logic."""
    from atlas.application.commands import AtlasCommand

    payload = {"classification": "wall", "name": "External Wall"}
    command = AtlasCommand("create_resource", payload=payload)

    assert command.payload == payload


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

    query = AtlasQuery("get_project", parameters={})

    assert query.name == "get_project"


def test_query_parameters_are_available() -> None:
    """Queries carry read parameters without mutating domain state."""
    from atlas.application.queries import AtlasQuery

    parameters = {"resource_id": "abc"}
    query = AtlasQuery("get_resource", parameters=parameters)

    assert query.parameters == parameters


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def test_resource_selection_is_identity_based() -> None:
    """UI selection must be represented by AtlasID, not a copied Resource."""
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.identity import AtlasID

    resource_id = AtlasID.generate()

    selection = AtlasResourceSelection(resource_id)

    assert selection.resource_id == resource_id
    assert isinstance(selection.resource_id, AtlasID)


def test_selection_does_not_store_resource_copy() -> None:
    """Selection must retain identity rather than duplicating domain state."""
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.identity import AtlasID

    resource_id = AtlasID.generate()
    selection = AtlasResourceSelection(resource_id)

    assert not hasattr(selection, "resource")
    assert not hasattr(selection, "resource_copy")


# ---------------------------------------------------------------------------
# UI state
# ---------------------------------------------------------------------------


def test_ui_state_is_separate_from_engineering_state() -> None:
    """UI state must have its own representation."""
    from atlas.application.ui_state import AtlasUIState

    state = AtlasUIState()

    assert state is not None
    assert hasattr(state, "selected_resource_id")
    assert hasattr(state, "active_panel")


def test_ui_state_does_not_store_project() -> None:
    """UI state must not become a second engineering model."""
    from atlas.application.ui_state import AtlasUIState

    state = AtlasUIState()

    assert not hasattr(state, "project")


def test_ui_state_can_track_selection_without_resource_copy() -> None:
    """Selection belongs to UI state as an AtlasID."""
    from atlas.application.ui_state import AtlasUIState
    from atlas.core.identity import AtlasID

    resource_id = AtlasID.generate()
    state = AtlasUIState()

    state.selected_resource_id = resource_id

    assert state.selected_resource_id == resource_id


# ---------------------------------------------------------------------------
# Presentation models
# ---------------------------------------------------------------------------


def test_resource_presentation_model_exists() -> None:
    """Presentation models must be distinct from canonical Resources."""
    from atlas.application.presentation import AtlasResourcePresentation

    assert AtlasResourcePresentation is not None


def test_resource_presentation_model_can_reference_identity() -> None:
    """Presentation models should expose canonical identity."""
    from atlas.application.presentation import AtlasResourcePresentation
    from atlas.core.identity import AtlasID

    resource_id = AtlasID.generate()

    presentation = AtlasResourcePresentation(
        resource_id=resource_id,
        name="External Wall",
    )

    assert presentation.resource_id == resource_id
    assert presentation.name == "External Wall"


def test_resource_presentation_model_is_not_an_atlas_resource() -> None:
    """Presentation objects must not replace the canonical Resource."""
    from atlas.application.presentation import AtlasResourcePresentation
    from atlas.resource.resource import AtlasResource

    presentation = AtlasResourcePresentation(
        resource_id=None,
        name="External Wall",
    )

    assert not isinstance(presentation, AtlasResource)


# ---------------------------------------------------------------------------
# Application commands and queries
# ---------------------------------------------------------------------------


def test_application_exposes_command_execution_boundary() -> None:
    """Commands must be executed through the application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.commands import AtlasCommand
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("UI Test Project")
    )

    command = AtlasCommand(
        "noop",
        payload={},
    )

    result = application.execute(command)

    assert result is not None


def test_application_exposes_query_execution_boundary() -> None:
    """Queries must be executed through the application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.queries import AtlasQuery
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("UI Test Project")
    )

    query = AtlasQuery(
        "get_project",
        parameters={},
    )

    result = application.query(query)

    assert result is not None


# ---------------------------------------------------------------------------
# Core / UI dependency direction
# ---------------------------------------------------------------------------


def test_application_owns_project_reference_not_ui_components() -> None:
    """Application boundary must depend on Atlas Core, not UI components."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject("Dependency Test")
    application = AtlasApplication(project)

    assert application.project is project
    assert not hasattr(application, "ui")
    assert not hasattr(application, "component_tree")


# ---------------------------------------------------------------------------
# Future 3D boundary
# ---------------------------------------------------------------------------


def test_3d_view_boundary_exists() -> None:
    """Future 3D visualization must have an explicit presentation boundary."""
    from atlas.application.views import Atlas3DView

    assert Atlas3DView is not None


def test_3d_view_does_not_own_project_model() -> None:
    """Renderer/view objects must not become canonical engineering state."""
    from atlas.application.views import Atlas3DView

    view = Atlas3DView()

    assert not hasattr(view, "project")
    assert not hasattr(view, "resource_registry")
    assert not hasattr(view, "resource_graph")


# ---------------------------------------------------------------------------
# Agent independence
# ---------------------------------------------------------------------------


def test_application_does_not_require_specific_ui_components_for_agents() -> None:
    """Agents must remain independent from UI implementation."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Agent Independence")
    )

    assert not hasattr(application, "agent_ui")
    assert not hasattr(application, "agent_panel")
    assert not hasattr(application, "agent_component")


# ---------------------------------------------------------------------------
# Persistence / exchange independence
# ---------------------------------------------------------------------------


def test_application_does_not_own_serializer() -> None:
    """UI application boundary must not become the serializer."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Persistence Independence")
    )

    assert not hasattr(application, "serializer")
    assert not hasattr(application, "json_serializer")


def test_application_does_not_own_importer_or_exporter() -> None:
    """Import/export remains an external exchange boundary."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Exchange Independence")
    )

    assert not hasattr(application, "importer")
    assert not hasattr(application, "exporter")


# ---------------------------------------------------------------------------
# Contract immutability / validation
# ---------------------------------------------------------------------------


def test_command_name_cannot_be_empty() -> None:
    """Command identity must be explicit."""
    from atlas.application.commands import AtlasCommand

    with pytest.raises(ValueError):
        AtlasCommand("", payload={})


def test_query_name_cannot_be_empty() -> None:
    """Query identity must be explicit."""
    from atlas.application.queries import AtlasQuery

    with pytest.raises(ValueError):
        AtlasQuery("", parameters={})


def test_selection_requires_atlas_id() -> None:
    """Resource selection must use canonical Atlas identity."""
    from atlas.application.selection import AtlasResourceSelection

    with pytest.raises(TypeError):
        AtlasResourceSelection("not-an-atlas-id")


# ---------------------------------------------------------------------------
# Architectural identity invariant
# ---------------------------------------------------------------------------


def test_selection_identity_can_be_round_tripped_as_string() -> None:
    """UI selection should be transport-friendly while preserving AtlasID."""
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.identity import AtlasID

    resource_id = AtlasID.generate()

    selection = AtlasResourceSelection(resource_id)

    encoded = str(selection.resource_id)
    restored = AtlasID.from_string(encoded)

    assert restored == resource_id


# ---------------------------------------------------------------------------
# Sanity: canonical domain remains independent
# ---------------------------------------------------------------------------


def test_ui_architecture_does_not_replace_atlas_project() -> None:
    """The application layer wraps AtlasProject; it does not redefine it."""
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    project = AtlasProject("Canonical Project")
    application = AtlasApplication(project)

    assert isinstance(application.project, AtlasProject)
    assert application.project is project
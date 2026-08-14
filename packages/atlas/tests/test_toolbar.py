"""
ENG-044 — Atlas Toolbar

RED/GREEN tests for the Atlas Toolbar capability.

The Toolbar is a presentation and command-delegation surface inside the
ENG-040 UI Application Shell.

These tests intentionally remain framework-independent.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _project():
    from atlas.project.project import AtlasProject

    return AtlasProject("Toolbar Project")


def _application():
    from atlas.application import AtlasApplication

    return AtlasApplication(
        _project(),
    )


def _command(
    name: str = "refresh",
):
    from atlas.application.commands import AtlasCommand

    return AtlasCommand(
        name=name,
        payload={},
    )


# ---------------------------------------------------------------------------
# Toolbar type and identity
# ---------------------------------------------------------------------------


def test_toolbar_type_exists() -> None:
    """Atlas must expose a dedicated Toolbar capability."""
    from atlas.application.toolbar import AtlasToolbar

    assert AtlasToolbar is not None


def test_toolbar_has_stable_identity() -> None:
    """Toolbar identity must be stable and UI-specific."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar.__new__(AtlasToolbar)

    assert toolbar.toolbar_id == "toolbar"


def test_toolbar_is_not_an_atlas_resource() -> None:
    """Toolbar must remain a presentation capability."""
    from atlas.application.toolbar import AtlasToolbar
    from atlas.core.resource import AtlasResource

    toolbar = AtlasToolbar.__new__(AtlasToolbar)

    assert not isinstance(
        toolbar,
        AtlasResource,
    )


def test_toolbar_is_not_an_atlas_project() -> None:
    """Toolbar must not become a Project container."""
    from atlas.application.toolbar import AtlasToolbar
    from atlas.project.project import AtlasProject

    toolbar = AtlasToolbar.__new__(AtlasToolbar)

    assert not isinstance(
        toolbar,
        AtlasProject,
    )


# ---------------------------------------------------------------------------
# Presentation model
# ---------------------------------------------------------------------------


def test_toolbar_presentation_model_exists() -> None:
    """Toolbar must expose a dedicated presentation model."""
    from atlas.application.toolbar import AtlasToolbarPresentation

    assert AtlasToolbarPresentation is not None


def test_toolbar_item_model_exists() -> None:
    """Toolbar must expose a dedicated Toolbar item model."""
    from atlas.application.toolbar import AtlasToolbarItem

    assert AtlasToolbarItem is not None


def test_toolbar_presentation_is_not_application_or_project() -> None:
    """Toolbar presentation must remain UI/application data."""
    from atlas.application.toolbar import AtlasToolbarPresentation
    from atlas.application import AtlasApplication
    from atlas.project.project import AtlasProject

    presentation = AtlasToolbarPresentation(
        items=(),
    )

    assert not isinstance(
        presentation,
        AtlasApplication,
    )

    assert not isinstance(
        presentation,
        AtlasProject,
    )


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_toolbar_requires_atlas_application() -> None:
    """Toolbar must operate through ENG-039 AtlasApplication."""
    from atlas.application.toolbar import AtlasToolbar

    with pytest.raises(TypeError):
        AtlasToolbar(
            application="invalid",  # type: ignore[arg-type]
        )


def test_toolbar_exposes_application_reference() -> None:
    """Toolbar must remain bound to the Application Boundary."""
    from atlas.application.toolbar import AtlasToolbar

    application = _application()

    toolbar = AtlasToolbar(
        application=application,
    )

    assert toolbar.application is application


def test_toolbar_does_not_directly_own_project() -> None:
    """Toolbar must not become an AtlasProject container."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "project",
    )

    assert not hasattr(
        toolbar,
        "atlas_project",
    )


# ---------------------------------------------------------------------------
# AtlasCommand integration
# ---------------------------------------------------------------------------


def test_toolbar_uses_atlas_command() -> None:
    """Toolbar items must wrap or reference the canonical AtlasCommand."""
    from atlas.application.commands import AtlasCommand
    from atlas.application.toolbar import AtlasToolbarItem

    command = _command()

    item = AtlasToolbarItem(
        command=command,
        label="Refresh",
    )

    assert isinstance(
        item.command,
        AtlasCommand,
    )


def test_toolbar_does_not_introduce_second_command_identity() -> None:
    """Toolbar must not replace AtlasCommand with a competing command model."""
    from atlas.application.toolbar import AtlasToolbarItem

    command = _command(
        "inspect",
    )

    item = AtlasToolbarItem(
        command=command,
        label="Inspect",
    )

    assert item.command is command

    assert not hasattr(
        item,
        "toolbar_command",
    )


# ---------------------------------------------------------------------------
# Command presentation
# ---------------------------------------------------------------------------


def test_toolbar_item_has_label() -> None:
    """Toolbar item must expose presentation label."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Refresh",
    )

    assert item.label == "Refresh"


def test_toolbar_item_supports_group() -> None:
    """Toolbar item may belong to a presentation group."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Refresh",
        group="project",
    )

    assert item.group == "project"


def test_toolbar_item_supports_order() -> None:
    """Toolbar item must support deterministic ordering."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Refresh",
        order=10,
    )

    assert item.order == 10


def test_toolbar_item_supports_enabled_state() -> None:
    """Toolbar item must support enabled/disabled presentation."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Inspect",
        enabled=False,
    )

    assert item.enabled is False


def test_toolbar_item_supports_visibility_state() -> None:
    """Toolbar item must support visibility presentation."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Debug",
        visible=False,
    )

    assert item.visible is False


def test_toolbar_item_supports_tooltip() -> None:
    """Toolbar item may expose presentation tooltip text."""
    from atlas.application.toolbar import AtlasToolbarItem

    item = AtlasToolbarItem(
        command=_command(),
        label="Refresh",
        tooltip="Refresh current view",
    )

    assert item.tooltip == "Refresh current view"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_toolbar_can_register_command() -> None:
    """Toolbar must support application command registration."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    item = toolbar.register_command(
        _command("refresh"),
        label="Refresh",
    )

    assert item is not None


def test_toolbar_can_register_multiple_commands() -> None:
    """Toolbar must support multiple commands."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("dashboard"),
        label="Dashboard",
    )

    toolbar.register_command(
        _command("explorer"),
        label="Explorer",
    )

    presentation = toolbar.refresh()

    assert len(presentation.items) == 2


def test_toolbar_registration_preserves_command_identity() -> None:
    """Registered items must preserve the original AtlasCommand."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    command = _command(
        "refresh",
    )

    item = toolbar.register_command(
        command,
        label="Refresh",
    )

    assert item.command is command


# ---------------------------------------------------------------------------
# Deterministic ordering
# ---------------------------------------------------------------------------


def test_toolbar_orders_items_deterministically() -> None:
    """Equivalent registrations must produce deterministic ordering."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("second"),
        label="Second",
        order=20,
    )

    toolbar.register_command(
        _command("first"),
        label="First",
        order=10,
    )

    presentation = toolbar.refresh()

    assert [
        item.label
        for item in presentation.items
    ] == [
        "First",
        "Second",
    ]


def test_toolbar_preserves_group_information() -> None:
    """Presentation must preserve command grouping."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("refresh"),
        label="Refresh",
        group="project",
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].group == "project"


# ---------------------------------------------------------------------------
# Visibility / enabled filtering
# ---------------------------------------------------------------------------


def test_toolbar_can_present_disabled_command() -> None:
    """Disabled commands remain representable."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("inspect"),
        label="Inspect",
        enabled=False,
    )

    presentation = toolbar.refresh()

    assert len(presentation.items) == 1
    assert presentation.items[0].enabled is False


def test_toolbar_can_present_hidden_command() -> None:
    """Hidden commands remain distinguishable from unregistered commands."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("debug"),
        label="Debug",
        visible=False,
    )

    presentation = toolbar.refresh()

    assert len(presentation.items) == 1
    assert presentation.items[0].visible is False


# ---------------------------------------------------------------------------
# Selection-aware commands
# ---------------------------------------------------------------------------


def test_toolbar_supports_selection_identity() -> None:
    """Toolbar selection context must use AtlasID."""
    from atlas.application.toolbar import AtlasToolbar
    from atlas.core.aid import AtlasID

    toolbar = AtlasToolbar(
        application=_application(),
    )

    resource_id = AtlasID.generate()

    toolbar.set_selection(
        resource_id,
    )

    assert toolbar.selected_resource_id == resource_id


def test_toolbar_rejects_invalid_selection_identity() -> None:
    """Toolbar must reject non-AtlasID selection values."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    with pytest.raises(TypeError):
        toolbar.set_selection(
            "not-an-atlas-id",  # type: ignore[arg-type]
        )


def test_toolbar_can_clear_selection() -> None:
    """Toolbar must support clearing selection context."""
    from atlas.application.toolbar import AtlasToolbar
    from atlas.core.aid import AtlasID

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.set_selection(
        AtlasID.generate(),
    )

    toolbar.set_selection(
        None,
    )

    assert toolbar.selected_resource_id is None


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------


def test_toolbar_delegates_command_execution() -> None:
    """
    Toolbar execution must delegate through AtlasApplication.

    The current ENG-039 Application boundary does not implement arbitrary
    command names yet, so the delegated result is NotImplementedError.
    """
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    command = _command(
        "refresh",
    )

    toolbar.register_command(
        command,
        label="Refresh",
    )

    with pytest.raises(NotImplementedError):
        toolbar.execute(
            command,
        )


def test_toolbar_delegates_noop_command() -> None:
    """Toolbar must successfully delegate supported Atlas commands."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    command = _command(
        "noop",
    )

    toolbar.register_command(
        command,
        label="No-op",
    )

    result = toolbar.execute(
        command,
    )

    assert result is None


def test_toolbar_rejects_non_command_execution() -> None:
    """Toolbar must accept only the canonical AtlasCommand."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    with pytest.raises(TypeError):
        toolbar.execute(
            "not-a-command",  # type: ignore[arg-type]
        )


def test_toolbar_does_not_directly_mutate_resource() -> None:
    """Toolbar execution must not bypass the Application Boundary."""
    from atlas.application.toolbar import AtlasToolbar
    from atlas.core.resource import AtlasResource

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "resource",
    )

    assert not hasattr(
        toolbar,
        "atlas_resource",
    )

    assert not issubclass(
        type(toolbar),
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Navigation commands
# ---------------------------------------------------------------------------


def test_toolbar_supports_dashboard_navigation_command() -> None:
    """Toolbar must represent Dashboard navigation."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("open_dashboard"),
        label="Dashboard",
        group="navigation",
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].command.name == (
        "open_dashboard"
    )


def test_toolbar_supports_explorer_navigation_command() -> None:
    """Toolbar must represent Explorer navigation."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("open_explorer"),
        label="Explorer",
        group="navigation",
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].command.name == (
        "open_explorer"
    )


def test_toolbar_supports_inspector_navigation_command() -> None:
    """Toolbar must represent Inspector navigation."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("open_inspector"),
        label="Inspector",
        group="navigation",
        enabled=False,
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].command.name == (
        "open_inspector"
    )

    assert presentation.items[0].enabled is False


# ---------------------------------------------------------------------------
# Explorer command surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command_name",
    [
        "refresh_explorer",
        "search",
        "filter",
        "clear_filter",
        "expand_all",
        "collapse_all",
    ],
)
def test_toolbar_supports_explorer_commands(
    command_name: str,
) -> None:
    """Toolbar must represent the command set anticipated by Explorer."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command(command_name),
        label=command_name.replace(
            "_",
            " ",
        ).title(),
        group="explorer",
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].command.name == (
        command_name
    )


# ---------------------------------------------------------------------------
# Inspector command surface
# ---------------------------------------------------------------------------


def test_toolbar_supports_refresh_inspector_command() -> None:
    """Toolbar must represent Inspector refresh."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("refresh_inspector"),
        label="Refresh Inspector",
        group="inspector",
    )

    presentation = toolbar.refresh()

    assert presentation.items[0].command.name == (
        "refresh_inspector"
    )


# ---------------------------------------------------------------------------
# Empty / loading / error states
# ---------------------------------------------------------------------------


def test_toolbar_supports_empty_state() -> None:
    """Toolbar must support a valid empty-command state."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    presentation = toolbar.refresh()

    assert presentation.items == ()


def test_toolbar_exposes_loading_state() -> None:
    """Toolbar must support transient loading state."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert toolbar.is_loading is False

    toolbar.set_loading(
        True,
    )

    assert toolbar.is_loading is True


def test_toolbar_loading_state_is_ui_state() -> None:
    """Loading state must not be written into Atlas Core."""
    from atlas.application import AtlasApplication
    from atlas.application.toolbar import AtlasToolbar

    project = _project()

    toolbar = AtlasToolbar(
        application=AtlasApplication(
            project,
        ),
    )

    toolbar.set_loading(
        True,
    )

    assert not hasattr(
        project,
        "loading",
    )


def test_toolbar_exposes_error_state() -> None:
    """Toolbar must support explicit error state."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.set_error(
        "Command registration failed",
    )

    assert toolbar.error == (
        "Command registration failed"
    )


# ---------------------------------------------------------------------------
# Workspace integration
# ---------------------------------------------------------------------------


def test_toolbar_is_hostable_by_workspace() -> None:
    """Toolbar must integrate with ENG-040 Workspace."""
    from atlas.application import AtlasApplication
    from atlas.application.panel import AtlasPanel
    from atlas.application.toolbar import AtlasToolbar
    from atlas.application.workspace import AtlasWorkspace

    application = AtlasApplication(
        _project(),
    )

    workspace = AtlasWorkspace(
        application=application,
    )

    toolbar = AtlasToolbar(
        application=application,
    )

    panel = AtlasPanel(
        panel_id=toolbar.toolbar_id,
        name="Toolbar",
    )

    workspace.register_panel(
        panel,
    )

    assert workspace.panel_registry.get(
        "toolbar",
    ) is panel


def test_toolbar_panel_identity_is_toolbar() -> None:
    """Toolbar presentation identity must remain stable."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar.__new__(
        AtlasToolbar,
    )

    assert toolbar.toolbar_id == "toolbar"


# ---------------------------------------------------------------------------
# Read-only behavior
# ---------------------------------------------------------------------------


def test_toolbar_refresh_does_not_mutate_project() -> None:
    """Toolbar refresh must not mutate engineering state."""
    from atlas.application import AtlasApplication
    from atlas.application.toolbar import AtlasToolbar

    project = _project()

    before_resources = project.resource_count
    before_relationships = project.relationship_count

    toolbar = AtlasToolbar(
        application=AtlasApplication(
            project,
        ),
    )

    toolbar.refresh()

    assert project.resource_count == before_resources
    assert project.relationship_count == before_relationships


def test_toolbar_does_not_own_resource_registry() -> None:
    """Toolbar must not own an independent Resource Registry."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "resource_registry",
    )

    assert not hasattr(
        toolbar,
        "toolbar_resource_registry",
    )


def test_toolbar_does_not_own_graph() -> None:
    """Toolbar must not own an independent Resource Graph."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "graph",
    )

    assert not hasattr(
        toolbar,
        "resource_graph",
    )

    assert not hasattr(
        toolbar,
        "toolbar_graph",
    )


def test_toolbar_does_not_own_command_engine() -> None:
    """Toolbar must not introduce a competing command execution engine."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "command_engine",
    )

    assert not hasattr(
        toolbar,
        "toolbar_command_engine",
    )


# ---------------------------------------------------------------------------
# Persistence / exchange isolation
# ---------------------------------------------------------------------------


def test_toolbar_does_not_own_serializer() -> None:
    """Toolbar must not implement serialization."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "serializer",
    )

    assert not hasattr(
        toolbar,
        "json_serializer",
    )


def test_toolbar_does_not_own_persistence() -> None:
    """Toolbar must not implement Save/Load."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "persistence",
    )

    assert not hasattr(
        toolbar,
        "save",
    )

    assert not hasattr(
        toolbar,
        "load",
    )


def test_toolbar_does_not_own_exchange() -> None:
    """Toolbar must not implement Import/Export."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "importer",
    )

    assert not hasattr(
        toolbar,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Agent / AI boundaries
# ---------------------------------------------------------------------------


def test_toolbar_does_not_own_agent_runtime() -> None:
    """Toolbar must not directly execute or own Agents."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "agent_runtime",
    )

    assert not hasattr(
        toolbar,
        "orchestrator",
    )

    assert not hasattr(
        toolbar,
        "coordinator",
    )


def test_toolbar_does_not_treat_ai_as_engineering_truth() -> None:
    """AI-generated actions must remain distinct from engineering truth."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "engineering_facts_from_ai",
    )


# ---------------------------------------------------------------------------
# 3D boundary
# ---------------------------------------------------------------------------


def test_toolbar_does_not_own_3d_engine() -> None:
    """ENG-044 must not implement the Phase 10 3D engine."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    assert not hasattr(
        toolbar,
        "scene",
    )

    assert not hasattr(
        toolbar,
        "camera",
    )

    assert not hasattr(
        toolbar,
        "gizmos",
    )

    assert not hasattr(
        toolbar,
        "renderer",
    )


# ---------------------------------------------------------------------------
# Deterministic presentation
# ---------------------------------------------------------------------------


def test_toolbar_refresh_is_deterministic() -> None:
    """Equivalent Toolbar state must produce equivalent presentation."""
    from atlas.application.toolbar import AtlasToolbar

    toolbar = AtlasToolbar(
        application=_application(),
    )

    toolbar.register_command(
        _command("explorer"),
        label="Explorer",
        order=20,
    )

    toolbar.register_command(
        _command("dashboard"),
        label="Dashboard",
        order=10,
    )

    first = toolbar.refresh()
    second = toolbar.refresh()

    assert first == second


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_toolbar_public_exports_exist() -> None:
    """Toolbar contracts must be publicly accessible."""
    from atlas import application

    expected = {
        "AtlasToolbar",
        "AtlasToolbarItem",
        "AtlasToolbarPresentation",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )
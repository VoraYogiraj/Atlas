"""
ENG-040 — Atlas UI Application Shell

RED-phase architectural tests for the Atlas UI application shell.

These tests define structural and behavioral contracts for:

- Workspace
- Panels
- Panel Registry
- Views
- View Registry
- Workspace State
- Selection context
- Lifecycle
- ENG-039 command/query integration
- Atlas Core separation
- Persistence / Exchange separation
- Agent independence
- Future 3D hosting
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------


def test_workspace_type_exists() -> None:
    """Atlas must expose a dedicated Workspace type."""
    from atlas.application.workspace import AtlasWorkspace

    assert AtlasWorkspace is not None


def test_workspace_can_be_created() -> None:
    """A Workspace must be creatable without becoming Atlas Core."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert workspace is not None


def test_workspace_has_stable_identity() -> None:
    """Workspace identity is distinct from AtlasProject and Resource identity."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert workspace.workspace_id is not None


def test_workspace_identity_is_unique() -> None:
    """Separate Workspaces must have distinct identities."""
    from atlas.application.workspace import AtlasWorkspace

    first = AtlasWorkspace()
    second = AtlasWorkspace()

    assert first.workspace_id != second.workspace_id


# ---------------------------------------------------------------------------
# Panel contract
# ---------------------------------------------------------------------------


def test_panel_type_exists() -> None:
    """Atlas must expose a Panel contract."""
    from atlas.application.panel import AtlasPanel

    assert AtlasPanel is not None


def test_panel_requires_stable_identity() -> None:
    """Panels require a machine-readable identity."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    assert panel.panel_id == "explorer"
    assert panel.name == "Explorer"


def test_panel_supports_description() -> None:
    """Panel metadata may include a human-readable description."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
        description="Navigate Atlas project structure.",
    )

    assert panel.description == (
        "Navigate Atlas project structure."
    )


def test_panel_identity_cannot_be_empty() -> None:
    """Panel identity must be explicit."""
    from atlas.application.panel import AtlasPanel

    with pytest.raises(ValueError):
        AtlasPanel(
            panel_id="",
            name="Explorer",
        )


def test_panel_name_cannot_be_empty() -> None:
    """Panel display identity must be explicit."""
    from atlas.application.panel import AtlasPanel

    with pytest.raises(ValueError):
        AtlasPanel(
            panel_id="explorer",
            name="",
        )


def test_panel_is_not_an_atlas_resource() -> None:
    """A Panel must remain a presentation object."""
    from atlas.application.panel import AtlasPanel
    from atlas.core.resource import AtlasResource

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    assert not isinstance(panel, AtlasResource)


def test_panel_does_not_own_project_model() -> None:
    """Panels must not become canonical engineering containers."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    assert not hasattr(panel, "project")
    assert not hasattr(panel, "resource_registry")
    assert not hasattr(panel, "resource_graph")


# ---------------------------------------------------------------------------
# Panel Registry
# ---------------------------------------------------------------------------


def test_panel_registry_exists() -> None:
    """Workspace must expose a dedicated Panel Registry."""
    from atlas.application.panel_registry import AtlasPanelRegistry

    assert AtlasPanelRegistry is not None


def test_panel_registry_can_be_created() -> None:
    """A Panel Registry should be independently constructible."""
    from atlas.application.panel_registry import AtlasPanelRegistry

    registry = AtlasPanelRegistry()

    assert registry is not None


def test_panel_registry_can_register_panel() -> None:
    """Panels must be explicitly registered."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.panel_registry import AtlasPanelRegistry

    registry = AtlasPanelRegistry()

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    registry.register(panel)

    assert registry.get("explorer") is panel


def test_panel_registry_rejects_duplicate_identity() -> None:
    """Two Panels may not share the same identity."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.panel_registry import AtlasPanelRegistry

    registry = AtlasPanelRegistry()

    first = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    second = AtlasPanel(
        panel_id="explorer",
        name="Another Explorer",
    )

    registry.register(first)

    with pytest.raises(ValueError):
        registry.register(second)


def test_panel_registry_unknown_panel_is_explicit() -> None:
    """Unknown panel identity must not silently produce a fake Panel."""
    from atlas.application.panel_registry import AtlasPanelRegistry

    registry = AtlasPanelRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_panel_registry_can_report_registered_panel_ids() -> None:
    """The registry should expose stable registered identities."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.panel_registry import AtlasPanelRegistry

    registry = AtlasPanelRegistry()

    registry.register(
        AtlasPanel(
            panel_id="explorer",
            name="Explorer",
        )
    )

    registry.register(
        AtlasPanel(
            panel_id="inspector",
            name="Inspector",
        )
    )

    assert set(registry.ids()) == {
        "explorer",
        "inspector",
    }


def test_panel_registry_does_not_replace_resource_registry() -> None:
    """UI registration must remain distinct from engineering registries."""
    from atlas.application.panel_registry import AtlasPanelRegistry
    from atlas.resource_registry.registry import AtlasResourceRegistry

    panel_registry = AtlasPanelRegistry()
    resource_registry = AtlasResourceRegistry()

    assert not isinstance(
        panel_registry,
        AtlasResourceRegistry,
    )
    assert not isinstance(
        resource_registry,
        AtlasPanelRegistry,
    )


# ---------------------------------------------------------------------------
# Panel visibility
# ---------------------------------------------------------------------------


def test_panel_has_visibility_state() -> None:
    """Panels must support explicit visibility state."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    assert panel.visible is True


def test_panel_visibility_can_be_changed() -> None:
    """Visibility is presentation state."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    panel.set_visible(False)

    assert panel.visible is False


def test_panel_visibility_does_not_store_project_state() -> None:
    """Changing visibility must not create engineering ownership."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    panel.set_visible(False)

    assert not hasattr(panel, "project")
    assert not hasattr(panel, "resource_registry")
    assert not hasattr(panel, "resource_graph")


# ---------------------------------------------------------------------------
# View contract
# ---------------------------------------------------------------------------


def test_view_type_exists() -> None:
    """Atlas must expose a dedicated View contract."""
    from atlas.application.view import AtlasView

    assert AtlasView is not None


def test_view_requires_stable_identity() -> None:
    """Views require machine-readable identity."""
    from atlas.application.view import AtlasView

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    assert view.view_id == "project"
    assert view.name == "Project"


def test_view_identity_cannot_be_empty() -> None:
    """View identity must be explicit."""
    from atlas.application.view import AtlasView

    with pytest.raises(ValueError):
        AtlasView(
            view_id="",
            name="Project",
        )


def test_view_name_cannot_be_empty() -> None:
    """View display identity must be explicit."""
    from atlas.application.view import AtlasView

    with pytest.raises(ValueError):
        AtlasView(
            view_id="project",
            name="",
        )


def test_view_does_not_own_project_model() -> None:
    """Views must not become canonical engineering containers."""
    from atlas.application.view import AtlasView

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    assert not hasattr(view, "project")
    assert not hasattr(view, "resource_registry")
    assert not hasattr(view, "resource_graph")


# ---------------------------------------------------------------------------
# View Registry
# ---------------------------------------------------------------------------


def test_view_registry_exists() -> None:
    """Workspace must expose a dedicated View Registry."""
    from atlas.application.view_registry import AtlasViewRegistry

    assert AtlasViewRegistry is not None


def test_view_registry_can_be_created() -> None:
    """A View Registry should be independently constructible."""
    from atlas.application.view_registry import AtlasViewRegistry

    registry = AtlasViewRegistry()

    assert registry is not None


def test_view_registry_can_register_view() -> None:
    """Views must be explicitly registered."""
    from atlas.application.view import AtlasView
    from atlas.application.view_registry import AtlasViewRegistry

    registry = AtlasViewRegistry()

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    registry.register(view)

    assert registry.get("project") is view


def test_view_registry_rejects_duplicate_identity() -> None:
    """Two Views may not share the same identity."""
    from atlas.application.view import AtlasView
    from atlas.application.view_registry import AtlasViewRegistry

    registry = AtlasViewRegistry()

    first = AtlasView(
        view_id="project",
        name="Project",
    )

    second = AtlasView(
        view_id="project",
        name="Another Project",
    )

    registry.register(first)

    with pytest.raises(ValueError):
        registry.register(second)


def test_view_registry_unknown_view_is_explicit() -> None:
    """Unknown View identity must fail explicitly."""
    from atlas.application.view_registry import AtlasViewRegistry

    registry = AtlasViewRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_view_registry_can_report_registered_view_ids() -> None:
    """The registry should expose stable registered View identities."""
    from atlas.application.view import AtlasView
    from atlas.application.view_registry import AtlasViewRegistry

    registry = AtlasViewRegistry()

    registry.register(
        AtlasView(
            view_id="project",
            name="Project",
        )
    )

    registry.register(
        AtlasView(
            view_id="3d",
            name="3D Workspace",
        )
    )

    assert set(registry.ids()) == {
        "project",
        "3d",
    }


# ---------------------------------------------------------------------------
# Workspace construction and ownership
# ---------------------------------------------------------------------------


def test_workspace_has_panel_registry() -> None:
    """Workspace owns the UI Panel Registry."""
    from atlas.application.panel_registry import AtlasPanelRegistry
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert isinstance(
        workspace.panel_registry,
        AtlasPanelRegistry,
    )


def test_workspace_has_view_registry() -> None:
    """Workspace owns the UI View Registry."""
    from atlas.application.view_registry import AtlasViewRegistry
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert isinstance(
        workspace.view_registry,
        AtlasViewRegistry,
    )


def test_workspace_does_not_own_resource_registry() -> None:
    """Workspace must not replace the canonical Resource Registry."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "resource_registry",
    )


def test_workspace_does_not_own_resource_graph() -> None:
    """Workspace must not maintain a competing Resource Graph."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "resource_graph",
    )


# ---------------------------------------------------------------------------
# Workspace panel operations
# ---------------------------------------------------------------------------


def test_workspace_can_register_panel() -> None:
    """Workspace should provide a panel registration boundary."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(panel)

    assert (
        workspace.panel_registry.get("explorer")
        is panel
    )


def test_workspace_can_set_active_panel() -> None:
    """Active panel must refer to a registered Panel."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(panel)
    workspace.set_active_panel("explorer")

    assert workspace.active_panel_id == "explorer"


def test_workspace_rejects_unknown_active_panel() -> None:
    """An unregistered Panel must not become active."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    with pytest.raises(KeyError):
        workspace.set_active_panel("unknown")


def test_workspace_can_clear_active_panel() -> None:
    """The active Panel may be cleared."""
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    panel = AtlasPanel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(panel)
    workspace.set_active_panel("explorer")
    workspace.set_active_panel(None)

    assert workspace.active_panel_id is None


# ---------------------------------------------------------------------------
# Workspace view operations
# ---------------------------------------------------------------------------


def test_workspace_can_register_view() -> None:
    """Workspace should provide a View registration boundary."""
    from atlas.application.view import AtlasView
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    workspace.register_view(view)

    assert (
        workspace.view_registry.get("project")
        is view
    )


def test_workspace_can_set_active_view() -> None:
    """Active View must refer to a registered View."""
    from atlas.application.view import AtlasView
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    workspace.register_view(view)
    workspace.set_active_view("project")

    assert workspace.active_view_id == "project"


def test_workspace_rejects_unknown_active_view() -> None:
    """An unregistered View must not become active."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    with pytest.raises(KeyError):
        workspace.set_active_view("unknown")


def test_workspace_can_clear_active_view() -> None:
    """The active View may be cleared."""
    from atlas.application.view import AtlasView
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    workspace.register_view(view)
    workspace.set_active_view("project")
    workspace.set_active_view(None)

    assert workspace.active_view_id is None


# ---------------------------------------------------------------------------
# Selection context
# ---------------------------------------------------------------------------


def test_workspace_can_store_identity_based_selection() -> None:
    """Workspace selection must be represented by AtlasID."""
    from atlas.application.workspace import AtlasWorkspace
    from atlas.core.aid import AtlasID

    workspace = AtlasWorkspace()
    resource_id = AtlasID.generate()

    workspace.set_selected_resource(resource_id)

    assert workspace.selected_resource_id == resource_id


def test_workspace_can_clear_selection() -> None:
    """Workspace selection may be cleared."""
    from atlas.application.workspace import AtlasWorkspace
    from atlas.core.aid import AtlasID

    workspace = AtlasWorkspace()

    workspace.set_selected_resource(
        AtlasID.generate(),
    )

    workspace.set_selected_resource(None)

    assert workspace.selected_resource_id is None


def test_workspace_rejects_non_atlas_id_selection() -> None:
    """Workspace selection must preserve canonical Atlas identity."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    with pytest.raises(TypeError):
        workspace.set_selected_resource(
            "invalid-id",  # type: ignore[arg-type]
        )


def test_workspace_does_not_store_selected_resource_copy() -> None:
    """Selection must not become a duplicate Resource object."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "selected_resource",
    )
    assert not hasattr(
        workspace,
        "selected_resource_object",
    )


# ---------------------------------------------------------------------------
# UI state isolation
# ---------------------------------------------------------------------------


def test_workspace_does_not_own_atlas_project_as_ui_state() -> None:
    """Workspace must not silently become the project container."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "project_model",
    )


def test_workspace_does_not_own_agent_runtime() -> None:
    """Agent Runtime remains an Atlas application/core capability."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "agent_runtime",
    )


# ---------------------------------------------------------------------------
# Application boundary integration
# ---------------------------------------------------------------------------


def test_workspace_can_use_atlas_application() -> None:
    """Workspace may be bound to the ENG-039 application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    project = AtlasProject("Shell Integration")

    application = AtlasApplication(project)
    workspace = AtlasWorkspace(
        application=application,
    )

    assert workspace.application is application
    assert workspace.application.project is project


def test_workspace_rejects_invalid_application() -> None:
    """Workspace application context must use ENG-039."""
    from atlas.application.workspace import AtlasWorkspace

    with pytest.raises(TypeError):
        AtlasWorkspace(
            application="invalid",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Command integration
# ---------------------------------------------------------------------------


def test_workspace_can_dispatch_command() -> None:
    """Workspace actions must pass through ENG-039 commands."""
    from atlas.application import AtlasApplication
    from atlas.application.commands import AtlasCommand
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Command Integration"),
    )

    workspace = AtlasWorkspace(
        application=application,
    )

    command = AtlasCommand(
        "noop",
        payload={},
    )

    result = workspace.execute(command)

    assert result is None


# ---------------------------------------------------------------------------
# Query integration
# ---------------------------------------------------------------------------


def test_workspace_can_dispatch_query() -> None:
    """Workspace reads must pass through ENG-039 queries."""
    from atlas.application import AtlasApplication
    from atlas.application.queries import AtlasQuery
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "Query Integration",
    )

    application = AtlasApplication(project)

    workspace = AtlasWorkspace(
        application=application,
    )

    query = AtlasQuery(
        "get_project",
        parameters={},
    )

    result = workspace.query(query)

    assert result is project


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def test_workspace_has_initial_lifecycle_state() -> None:
    """Workspace lifecycle must start in a predictable state."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert workspace.lifecycle == "created"


def test_workspace_can_initialize() -> None:
    """Workspace initialization must be explicit."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    workspace.initialize()

    assert workspace.lifecycle == "initialized"


def test_workspace_can_activate_after_initialization() -> None:
    """Workspace activation follows initialization."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    workspace.initialize()
    workspace.activate()

    assert workspace.lifecycle == "active"


def test_workspace_cannot_activate_before_initialization() -> None:
    """Lifecycle order must remain deterministic."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    with pytest.raises(RuntimeError):
        workspace.activate()


def test_workspace_can_deactivate() -> None:
    """Active Workspace can be deactivated."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    workspace.initialize()
    workspace.activate()
    workspace.deactivate()

    assert workspace.lifecycle == "inactive"


def test_workspace_can_dispose() -> None:
    """Workspace can release its own UI resources."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    workspace.initialize()
    workspace.activate()
    workspace.deactivate()
    workspace.dispose()

    assert workspace.lifecycle == "disposed"


def test_workspace_disposal_does_not_delete_atlas_project() -> None:
    """Disposing UI must not dispose engineering state."""
    from atlas.application import AtlasApplication
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    project = AtlasProject(
        "Lifecycle Project",
    )

    application = AtlasApplication(project)

    workspace = AtlasWorkspace(
        application=application,
    )

    workspace.initialize()
    workspace.activate()
    workspace.deactivate()
    workspace.dispose()

    assert application.project is project


# ---------------------------------------------------------------------------
# Persistence / Exchange separation
# ---------------------------------------------------------------------------


def test_workspace_does_not_own_project_persistence() -> None:
    """Workspace must not become the persistence layer."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "persistence",
    )
    assert not hasattr(
        workspace,
        "serializer",
    )


def test_workspace_does_not_own_import_export() -> None:
    """Workspace must not become the exchange layer."""
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    assert not hasattr(
        workspace,
        "importer",
    )
    assert not hasattr(
        workspace,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Future 3D boundary
# ---------------------------------------------------------------------------


def test_workspace_can_host_future_3d_view() -> None:
    """The shell must be able to host a future 3D View."""
    from atlas.application.view import AtlasView
    from atlas.application.workspace import AtlasWorkspace

    workspace = AtlasWorkspace()

    view = AtlasView(
        view_id="3d",
        name="3D Workspace",
    )

    workspace.register_view(view)
    workspace.set_active_view("3d")

    assert workspace.active_view_id == "3d"


def test_3d_view_identity_remains_presentation_identity() -> None:
    """A future 3D View must not become an engineering Resource."""
    from atlas.application.view import AtlasView
    from atlas.application.workspace import AtlasWorkspace
    from atlas.core.resource import AtlasResource

    workspace = AtlasWorkspace()

    view = AtlasView(
        view_id="3d",
        name="3D Workspace",
    )

    workspace.register_view(view)

    assert not isinstance(
        workspace.view_registry.get("3d"),
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Agent independence
# ---------------------------------------------------------------------------


def test_panel_does_not_require_agent_component() -> None:
    """Panels must remain independent from specific Agent UI components."""
    from atlas.application.panel import AtlasPanel

    panel = AtlasPanel(
        panel_id="agents",
        name="Agents",
    )

    assert not hasattr(panel, "agent")
    assert not hasattr(panel, "agent_runtime")
    assert not hasattr(panel, "agent_component")


def test_view_does_not_require_agent_component() -> None:
    """Views must remain independent from specific Agent UI components."""
    from atlas.application.view import AtlasView

    view = AtlasView(
        view_id="project",
        name="Project",
    )

    assert not hasattr(view, "agent")
    assert not hasattr(view, "agent_runtime")
    assert not hasattr(view, "agent_component")


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_ui_shell_public_exports_exist() -> None:
    """The application package should expose the shell contracts."""
    from atlas import application

    expected = {
        "AtlasWorkspace",
        "AtlasPanel",
        "AtlasPanelRegistry",
        "AtlasView",
        "AtlasViewRegistry",
    }

    for name in expected:
        assert hasattr(application, name)
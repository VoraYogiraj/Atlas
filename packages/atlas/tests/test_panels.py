"""
ENG-045 — Atlas Panels

RED/GREEN tests for the Atlas Panel capability.

Panels are reusable UI/application containers hosted by AtlasWorkspace.

These tests intentionally remain framework-independent and preserve the
existing ENG-040 Workspace / Panel Registry architecture.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _project():
    from atlas.project.project import AtlasProject

    return AtlasProject("Panels Project")


def _application():
    from atlas.application import AtlasApplication

    return AtlasApplication(
        _project(),
    )


def _panel(
    panel_id: str = "test-panel",
    name: str = "Test Panel",
):
    from atlas.application.panel import AtlasPanel

    return AtlasPanel(
        panel_id=panel_id,
        name=name,
    )


def _workspace():
    from atlas.application import AtlasApplication
    from atlas.application.workspace import AtlasWorkspace

    return AtlasWorkspace(
        application=AtlasApplication(
            _project(),
        ),
    )


# ---------------------------------------------------------------------------
# Panel type and identity
# ---------------------------------------------------------------------------


def test_panel_type_exists() -> None:
    """Atlas must expose the canonical Panel type."""
    from atlas.application.panel import AtlasPanel

    assert AtlasPanel is not None


def test_panel_has_stable_identity() -> None:
    """Every Panel must expose its stable UI/application identity."""
    panel = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    assert panel.panel_id == "explorer"


def test_panel_identity_is_not_atlas_id() -> None:
    """Panel identity must remain separate from engineering identity."""
    from atlas.core.aid import AtlasID

    panel = _panel()

    assert not isinstance(
        panel.panel_id,
        AtlasID,
    )


def test_panel_is_not_an_atlas_resource() -> None:
    """Panel must remain a UI/application object."""
    from atlas.application.panel import AtlasPanel
    from atlas.core.resource import AtlasResource

    panel = _panel()

    assert isinstance(
        panel,
        AtlasPanel,
    )

    assert not isinstance(
        panel,
        AtlasResource,
    )


def test_panel_is_not_an_atlas_project() -> None:
    """Panel must not become a Project container."""
    from atlas.application.panel import AtlasPanel
    from atlas.project.project import AtlasProject

    panel = _panel()

    assert isinstance(
        panel,
        AtlasPanel,
    )

    assert not isinstance(
        panel,
        AtlasProject,
    )


# ---------------------------------------------------------------------------
# Panel presentation state
# ---------------------------------------------------------------------------


def test_panel_name_is_available() -> None:
    """Panel must expose a presentation name."""
    panel = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    assert panel.name == "Dashboard"


def test_panel_supports_visibility_state() -> None:
    """Panel must support transient visibility state."""
    panel = _panel()

    assert panel.visible is True

    panel.set_visible(False)

    assert panel.visible is False


def test_panel_supports_enabled_state() -> None:
    """Panel must support transient enabled state."""
    panel = _panel()

    assert panel.enabled is True

    panel.set_enabled(False)

    assert panel.enabled is False


def test_panel_supports_active_state() -> None:
    """Panel must support transient active state."""
    panel = _panel()

    assert panel.active is False

    panel.set_active(True)

    assert panel.active is True


def test_panel_can_be_shown_again() -> None:
    """Visibility state must be reversible."""
    panel = _panel()

    panel.set_visible(False)
    panel.set_visible(True)

    assert panel.visible is True


def test_panel_can_be_enabled_again() -> None:
    """Enabled state must be reversible."""
    panel = _panel()

    panel.set_enabled(False)
    panel.set_enabled(True)

    assert panel.enabled is True


def test_panel_can_become_inactive() -> None:
    """Active state must be reversible."""
    panel = _panel()

    panel.set_active(True)
    panel.set_active(False)

    assert panel.active is False


# ---------------------------------------------------------------------------
# Panel ordering
# ---------------------------------------------------------------------------


def test_panel_supports_order() -> None:
    """Panel presentation must support deterministic ordering."""
    panel = _panel()

    assert isinstance(
        panel.order,
        int,
    )


def test_panel_order_can_be_changed() -> None:
    """Panel ordering must be configurable."""
    panel = _panel()

    panel.set_order(20)

    assert panel.order == 20


def test_panel_order_rejects_non_integer() -> None:
    """Panel ordering must remain deterministic and typed."""
    panel = _panel()

    with pytest.raises(TypeError):
        panel.set_order(
            "20",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Panel lifecycle
# ---------------------------------------------------------------------------


def test_panel_has_lifecycle_state() -> None:
    """Panel must expose a UI lifecycle state."""
    panel = _panel()

    assert panel.lifecycle is not None


def test_panel_lifecycle_is_not_resource_lifecycle() -> None:
    """Panel lifecycle must remain distinct from AtlasLifecycle."""
    from atlas.lifecycle.lifecycle import AtlasLifecycle

    panel = _panel()

    assert not isinstance(
        panel.lifecycle,
        AtlasLifecycle,
    )


# ---------------------------------------------------------------------------
# Panel Registry integration
# ---------------------------------------------------------------------------


def test_panel_can_be_registered() -> None:
    """Panel registration must be compatible with ENG-040."""
    workspace = _workspace()
    panel = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(
        panel,
    )

    assert workspace.panel_registry.get(
        "explorer",
    ) is panel


def test_panel_registry_exists() -> None:
    """Workspace must expose the canonical Panel Registry."""
    workspace = _workspace()

    assert workspace.panel_registry is not None


def test_panel_registry_is_canonical_workspace_registry() -> None:
    """Panel Registry must belong to the Workspace."""
    from atlas.application.panel_registry import AtlasPanelRegistry

    workspace = _workspace()

    assert isinstance(
        workspace.panel_registry,
        AtlasPanelRegistry,
    )


def test_panel_lookup_uses_panel_id() -> None:
    """Panel lookup must use stable panel identity."""
    workspace = _workspace()

    panel = _panel(
        panel_id="inspector",
        name="Inspector",
    )

    workspace.register_panel(
        panel,
    )

    assert workspace.panel_registry.get(
        "inspector",
    ) is panel


def test_panel_lookup_unknown_id_raises_key_error() -> None:
    """Missing Panel lookup must fail explicitly."""
    workspace = _workspace()

    with pytest.raises(KeyError):
        workspace.panel_registry.get(
            "missing-panel",
        )


def test_workspace_does_not_own_second_panel_registry() -> None:
    """Workspace must not maintain competing Panel Registries."""
    workspace = _workspace()

    assert not hasattr(
        workspace,
        "secondary_panel_registry",
    )

    assert not hasattr(
        workspace,
        "alternate_panel_registry",
    )


def test_panel_does_not_own_panel_registry() -> None:
    """Individual Panels must not own a second Panel Registry."""
    panel = _panel()

    assert not hasattr(
        panel,
        "panel_registry",
    )

    assert not hasattr(
        panel,
        "child_panel_registry",
    )


# ---------------------------------------------------------------------------
# Workspace active panel
# ---------------------------------------------------------------------------


def test_workspace_supports_active_panel_identity() -> None:
    """Workspace must expose the identity of the active Panel."""
    workspace = _workspace()

    dashboard = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    explorer = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(
        dashboard,
    )

    workspace.register_panel(
        explorer,
    )

    workspace.set_active_panel(
        "explorer",
    )

    assert workspace.active_panel_id == "explorer"


def test_workspace_can_activate_another_panel() -> None:
    """Active Panel must be switchable."""
    workspace = _workspace()

    dashboard = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    explorer = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    workspace.register_panel(
        dashboard,
    )

    workspace.register_panel(
        explorer,
    )

    workspace.set_active_panel(
        "dashboard",
    )

    assert workspace.active_panel_id == "dashboard"

    workspace.set_active_panel(
        "explorer",
    )

    assert workspace.active_panel_id == "explorer"


def test_active_panel_identity_is_not_resource_identity() -> None:
    """Active Panel identity must not be represented as an AtlasID."""
    from atlas.core.aid import AtlasID

    workspace = _workspace()

    panel = _panel(
        panel_id="inspector",
        name="Inspector",
    )

    workspace.register_panel(
        panel,
    )

    workspace.set_active_panel(
        "inspector",
    )

    assert not isinstance(
        workspace.active_panel_id,
        AtlasID,
    )


def test_workspace_can_clear_active_panel() -> None:
    """Workspace must support an inactive/no-active-panel state."""
    workspace = _workspace()

    panel = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    workspace.register_panel(
        panel,
    )

    workspace.set_active_panel(
        "dashboard",
    )

    workspace.set_active_panel(
        None,
    )

    assert workspace.active_panel_id is None


def test_workspace_rejects_unknown_active_panel() -> None:
    """Unknown Panel IDs must not silently become active."""
    workspace = _workspace()

    with pytest.raises(KeyError):
        workspace.set_active_panel(
            "missing-panel",
        )


# ---------------------------------------------------------------------------
# Deterministic panel ordering
# ---------------------------------------------------------------------------


def test_workspace_panel_order_is_deterministic() -> None:
    """Equivalent Panel registrations must produce stable ordering."""
    workspace = _workspace()

    explorer = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    dashboard = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    inspector = _panel(
        panel_id="inspector",
        name="Inspector",
    )

    explorer.set_order(20)
    dashboard.set_order(10)
    inspector.set_order(30)

    workspace.register_panel(
        explorer,
    )

    workspace.register_panel(
        dashboard,
    )

    workspace.register_panel(
        inspector,
    )

    ordered = workspace.panels

    assert [
        panel.panel_id
        for panel in ordered
    ] == [
        "dashboard",
        "explorer",
        "inspector",
    ]


def test_equivalent_panel_state_produces_equivalent_order() -> None:
    """Equivalent Workspace state must produce equivalent Panel ordering."""
    workspace_a = _workspace()
    workspace_b = _workspace()

    for workspace in (
        workspace_a,
        workspace_b,
    ):
        dashboard = _panel(
            panel_id="dashboard",
            name="Dashboard",
        )

        explorer = _panel(
            panel_id="explorer",
            name="Explorer",
        )

        dashboard.set_order(10)
        explorer.set_order(20)

        workspace.register_panel(
            explorer,
        )

        workspace.register_panel(
            dashboard,
        )

    assert [
        panel.panel_id
        for panel in workspace_a.panels
    ] == [
        panel.panel_id
        for panel in workspace_b.panels
    ]


# ---------------------------------------------------------------------------
# Capability hosting
# ---------------------------------------------------------------------------


def test_dashboard_can_be_hosted_by_panel() -> None:
    """Dashboard must be hostable by the Panel architecture."""
    from atlas.application.dashboard import AtlasDashboard

    application = _application()

    dashboard = AtlasDashboard(
        application=application,
    )

    panel = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    assert dashboard is not None
    assert panel.panel_id == "dashboard"


def test_explorer_can_be_hosted_by_panel() -> None:
    """Explorer must be hostable by the Panel architecture."""
    from atlas.application.explorer import AtlasExplorer

    application = _application()

    explorer = AtlasExplorer(
        application=application,
    )

    panel = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    assert explorer is not None
    assert panel.panel_id == "explorer"


def test_inspector_can_be_hosted_by_panel() -> None:
    """Inspector must be hostable by the Panel architecture."""
    from atlas.application.inspector import AtlasInspector

    application = _application()

    inspector = AtlasInspector(
        application=application,
    )

    panel = _panel(
        panel_id="inspector",
        name="Inspector",
    )

    assert inspector is not None
    assert panel.panel_id == "inspector"


# ---------------------------------------------------------------------------
# Selection context
# ---------------------------------------------------------------------------


def test_workspace_selection_is_atlas_id_based() -> None:
    """Panel architecture must preserve AtlasID selection context."""
    from atlas.core.aid import AtlasID

    workspace = _workspace()

    resource_id = AtlasID.generate()

    workspace.set_selected_resource(
        resource_id,
    )

    assert workspace.selected_resource_id == resource_id


def test_panel_does_not_store_resource_as_selection() -> None:
    """Panel must not copy canonical Resource objects into UI state."""
    from atlas.core.resource import AtlasResource

    panel = _panel()

    assert not hasattr(
        panel,
        "resource",
    )

    assert not hasattr(
        panel,
        "selected_resource",
    )

    assert not isinstance(
        getattr(
            panel,
            "selected_resource_id",
            None,
        ),
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Loading / error / empty states
# ---------------------------------------------------------------------------


def test_panel_supports_loading_state() -> None:
    """Panel must expose transient loading state."""
    panel = _panel()

    assert panel.is_loading is False

    panel.set_loading(
        True,
    )

    assert panel.is_loading is True


def test_panel_loading_state_is_ui_state() -> None:
    """Panel loading state must not be engineering state."""
    from atlas.core.resource import AtlasResource

    panel = _panel()

    panel.set_loading(
        True,
    )

    assert not hasattr(
        panel,
        "engineering_state",
    )

    assert not isinstance(
        panel,
        AtlasResource,
    )


def test_panel_supports_error_state() -> None:
    """Panel must expose explicit transient error state."""
    panel = _panel()

    panel.set_error(
        "Panel presentation failed",
    )

    assert panel.error == (
        "Panel presentation failed"
    )


def test_panel_supports_clearing_error_state() -> None:
    """Panel error state must be clearable."""
    panel = _panel()

    panel.set_error(
        "Panel presentation failed",
    )

    panel.set_error(
        None,
    )

    assert panel.error is None


def test_workspace_supports_empty_panel_state() -> None:
    """Workspace must support having no registered Panels."""
    workspace = _workspace()

    assert workspace.panels == ()


# ---------------------------------------------------------------------------
# Read-only behavior
# ---------------------------------------------------------------------------


def test_panel_visibility_does_not_change_project_state() -> None:
    """Showing/hiding a Panel must not mutate engineering state."""
    workspace = _workspace()

    project = workspace.application.project

    resources_before = project.resource_count
    relationships_before = project.relationship_count

    panel = _panel()

    workspace.register_panel(
        panel,
    )

    panel.set_visible(False)
    panel.set_visible(True)

    assert project.resource_count == resources_before
    assert project.relationship_count == relationships_before


def test_panel_activation_does_not_change_project_state() -> None:
    """Activating a Panel must not mutate engineering state."""
    workspace = _workspace()

    project = workspace.application.project

    resources_before = project.resource_count
    relationships_before = project.relationship_count

    panel = _panel(
        panel_id="dashboard",
        name="Dashboard",
    )

    workspace.register_panel(
        panel,
    )

    workspace.set_active_panel(
        "dashboard",
    )

    assert project.resource_count == resources_before
    assert project.relationship_count == relationships_before


# ---------------------------------------------------------------------------
# Engineering state isolation
# ---------------------------------------------------------------------------


def test_panel_does_not_own_resource_registry() -> None:
    """Panel must not own an independent Resource Registry."""
    panel = _panel()

    assert not hasattr(
        panel,
        "resource_registry",
    )

    assert not hasattr(
        panel,
        "panel_resource_registry",
    )


def test_panel_does_not_own_resource_graph() -> None:
    """Panel must not own an independent Resource Graph."""
    panel = _panel()

    assert not hasattr(
        panel,
        "graph",
    )

    assert not hasattr(
        panel,
        "resource_graph",
    )

    assert not hasattr(
        panel,
        "panel_graph",
    )


def test_panel_does_not_own_classification_hierarchy() -> None:
    """Panel must not create another classification hierarchy."""
    panel = _panel()

    assert not hasattr(
        panel,
        "classification_hierarchy",
    )

    assert not hasattr(
        panel,
        "panel_classification_hierarchy",
    )


def test_panel_does_not_own_project() -> None:
    """Panel must not become a Project container."""
    panel = _panel()

    assert not hasattr(
        panel,
        "project",
    )

    assert not hasattr(
        panel,
        "atlas_project",
    )


# ---------------------------------------------------------------------------
# Command boundary
# ---------------------------------------------------------------------------


def test_panel_does_not_own_command_engine() -> None:
    """Panel system must reuse Atlas Application commands."""
    panel = _panel()

    assert not hasattr(
        panel,
        "command_engine",
    )

    assert not hasattr(
        panel,
        "panel_command_engine",
    )


def test_panel_does_not_define_second_command_model() -> None:
    """Panel must not introduce a competing command representation."""
    panel = _panel()

    assert not hasattr(
        panel,
        "commands",
    )

    assert not hasattr(
        panel,
        "panel_commands",
    )


# ---------------------------------------------------------------------------
# Persistence / exchange isolation
# ---------------------------------------------------------------------------


def test_panel_does_not_own_serializer() -> None:
    """Panel must not implement serialization."""
    panel = _panel()

    assert not hasattr(
        panel,
        "serializer",
    )

    assert not hasattr(
        panel,
        "json_serializer",
    )


def test_panel_does_not_own_persistence() -> None:
    """Panel must not implement Save/Load."""
    panel = _panel()

    assert not hasattr(
        panel,
        "persistence",
    )

    assert not hasattr(
        panel,
        "save",
    )

    assert not hasattr(
        panel,
        "load",
    )


def test_panel_does_not_own_exchange() -> None:
    """Panel must not implement Import/Export."""
    panel = _panel()

    assert not hasattr(
        panel,
        "importer",
    )

    assert not hasattr(
        panel,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Agent / AI boundaries
# ---------------------------------------------------------------------------


def test_panel_does_not_own_agent_runtime() -> None:
    """Panel must not execute or own Agents directly."""
    panel = _panel()

    assert not hasattr(
        panel,
        "agent_runtime",
    )

    assert not hasattr(
        panel,
        "orchestrator",
    )

    assert not hasattr(
        panel,
        "coordinator",
    )


def test_panel_does_not_treat_ai_as_engineering_truth() -> None:
    """AI-generated navigation must remain separate from engineering truth."""
    panel = _panel()

    assert not hasattr(
        panel,
        "engineering_facts_from_ai",
    )


# ---------------------------------------------------------------------------
# 3D boundary
# ---------------------------------------------------------------------------


def test_panel_does_not_own_3d_engine() -> None:
    """ENG-045 must not implement the Phase 10 3D engine."""
    panel = _panel()

    assert not hasattr(
        panel,
        "scene",
    )

    assert not hasattr(
        panel,
        "camera",
    )

    assert not hasattr(
        panel,
        "gizmos",
    )

    assert not hasattr(
        panel,
        "renderer",
    )


# ---------------------------------------------------------------------------
# Workspace lifecycle boundary
# ---------------------------------------------------------------------------


def test_panel_does_not_own_workspace() -> None:
    """Panel must not create a second Workspace."""
    panel = _panel()

    assert not hasattr(
        panel,
        "workspace",
    )

    assert not hasattr(
        panel,
        "atlas_workspace",
    )


def test_workspace_remains_responsible_for_panel_registry() -> None:
    """Workspace must remain the owner of Panel registration."""
    workspace = _workspace()

    assert hasattr(
        workspace,
        "panel_registry",
    )

    assert not hasattr(
        workspace,
        "secondary_registry",
    )


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_panel_public_exports_exist() -> None:
    """Panel contracts must be publicly accessible."""
    from atlas import application

    expected = {
        "AtlasPanel",
        "AtlasPanelRegistry",
        "AtlasWorkspace",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )


# ---------------------------------------------------------------------------
# Deterministic panel behavior
# ---------------------------------------------------------------------------


def test_panel_state_is_deterministic() -> None:
    """Equivalent Panel state must remain equivalent."""
    panel_a = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    panel_b = _panel(
        panel_id="explorer",
        name="Explorer",
    )

    panel_a.set_order(20)
    panel_b.set_order(20)

    assert panel_a.panel_id == panel_b.panel_id
    assert panel_a.name == panel_b.name
    assert panel_a.order == panel_b.order
    assert panel_a.visible == panel_b.visible
    assert panel_a.enabled == panel_b.enabled
    assert panel_a.active == panel_b.active


def test_workspace_panel_registration_is_deterministic() -> None:
    """Equivalent registrations must produce equivalent panel identity order."""
    workspace_a = _workspace()
    workspace_b = _workspace()

    panels = (
        ("dashboard", "Dashboard", 10),
        ("explorer", "Explorer", 20),
        ("inspector", "Inspector", 30),
    )

    for workspace in (
        workspace_a,
        workspace_b,
    ):
        for panel_id, name, order in panels:
            panel = _panel(
                panel_id=panel_id,
                name=name,
            )

            panel.set_order(
                order,
            )

            workspace.register_panel(
                panel,
            )

    assert [
        panel.panel_id
        for panel in workspace_a.panels
    ] == [
        panel.panel_id
        for panel in workspace_b.panels
    ]
"""
ENG-041 — Atlas Dashboard

RED-phase tests for the Atlas Dashboard capability.

The Dashboard is a read-oriented project-level presentation surface
inside the ENG-040 UI Application Shell.

These tests intentionally avoid coupling Atlas to any specific frontend
framework or rendering technology.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Dashboard type and identity
# ---------------------------------------------------------------------------


def test_dashboard_type_exists() -> None:
    """Atlas must expose a dedicated Dashboard capability."""
    from atlas.application.dashboard import AtlasDashboard

    assert AtlasDashboard is not None


def test_dashboard_has_stable_identity() -> None:
    """Dashboard identity must be stable and UI-specific."""
    from atlas.application.dashboard import AtlasDashboard

    dashboard = AtlasDashboard()

    assert dashboard.dashboard_id == "dashboard"


def test_dashboard_is_not_an_atlas_resource() -> None:
    """Dashboard must remain a presentation object."""
    from atlas.application.dashboard import AtlasDashboard
    from atlas.core.resource import AtlasResource

    dashboard = AtlasDashboard()

    assert not isinstance(
        dashboard,
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Dashboard presentation model
# ---------------------------------------------------------------------------


def test_dashboard_presentation_model_exists() -> None:
    """Dashboard must expose a dedicated presentation representation."""
    from atlas.application.dashboard import AtlasDashboardPresentation

    assert AtlasDashboardPresentation is not None


def test_dashboard_presentation_model_contains_project_identity() -> None:
    """Dashboard presentation must expose project identity."""
    from atlas.application.dashboard import (
        AtlasDashboardPresentation,
    )

    presentation = AtlasDashboardPresentation(
        project_id="project-001",
        project_name="Sample Building",
    )

    assert presentation.project_id == "project-001"
    assert presentation.project_name == "Sample Building"


def test_dashboard_presentation_model_is_not_atlas_project() -> None:
    """Presentation data must not replace the canonical AtlasProject."""
    from atlas.application.dashboard import (
        AtlasDashboardPresentation,
    )
    from atlas.project.project import AtlasProject

    presentation = AtlasDashboardPresentation(
        project_id="project-001",
        project_name="Sample Building",
    )

    assert not isinstance(
        presentation,
        AtlasProject,
    )


def test_dashboard_presentation_does_not_store_project_object() -> None:
    """Dashboard presentation must not embed AtlasProject."""
    from atlas.application.dashboard import (
        AtlasDashboardPresentation,
    )

    presentation = AtlasDashboardPresentation(
        project_id="project-001",
        project_name="Sample Building",
    )

    assert not hasattr(
        presentation,
        "project",
    )


# ---------------------------------------------------------------------------
# Project identity
# ---------------------------------------------------------------------------


def test_dashboard_can_read_project_identity() -> None:
    """Dashboard must obtain canonical project identity."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Sample Building")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.project_name == "Sample Building"
    assert presentation.project_id == str(project.aid)


# ---------------------------------------------------------------------------
# Resource summary
# ---------------------------------------------------------------------------


def test_dashboard_presents_resource_summary() -> None:
    """Dashboard must expose resource-level summary data."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Resource Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.resource_summary is not None
    assert presentation.resource_summary.total == 0


def test_dashboard_resource_summary_has_lifecycle_counts() -> None:
    """Resource summary must support lifecycle-level counts."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Lifecycle Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    summary = presentation.resource_summary

    assert summary.active == 0
    assert summary.archived == 0
    assert summary.deleted == 0


def test_dashboard_resource_count_is_derived_not_stored_as_database() -> None:
    """Dashboard must not own a parallel Resource count database."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Derived Counts")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "resource_database",
    )
    assert not hasattr(
        dashboard,
        "resource_registry",
    )


# ---------------------------------------------------------------------------
# Classification summary
# ---------------------------------------------------------------------------


def test_dashboard_presents_classification_summary() -> None:
    """Dashboard must expose classification summary data."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Classification Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.classification_summary is not None


def test_dashboard_does_not_own_classification_registry() -> None:
    """Dashboard must not maintain a competing classification hierarchy."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Classification Isolation")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "classification_registry",
    )
    assert not hasattr(
        dashboard,
        "classification_hierarchy",
    )


# ---------------------------------------------------------------------------
# Relationship summary
# ---------------------------------------------------------------------------


def test_dashboard_presents_relationship_summary() -> None:
    """Dashboard must expose relationship summary data."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Relationship Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.relationship_summary is not None
    assert presentation.relationship_summary.total == 0


def test_dashboard_does_not_own_resource_graph() -> None:
    """Dashboard must not create a second relationship graph."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Graph Isolation")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "resource_graph",
    )
    assert not hasattr(
        dashboard,
        "graph",
    )


# ---------------------------------------------------------------------------
# Validation summary
# ---------------------------------------------------------------------------


def test_dashboard_presents_validation_summary() -> None:
    """Dashboard must expose validation summary data."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Validation Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.validation_summary is not None


def test_dashboard_validation_summary_has_expected_counters() -> None:
    """Validation summary must expose high-level result counters."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Validation Counters")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    summary = presentation.validation_summary

    assert summary.errors == 0
    assert summary.warnings == 0
    assert summary.passed == 0


def test_dashboard_does_not_implement_validation_engine() -> None:
    """Dashboard must consume validation results, not reimplement validation."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Validation Isolation")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "validation_engine",
    )
    assert not hasattr(
        dashboard,
        "validation_rules",
    )


# ---------------------------------------------------------------------------
# Agent / activity summary
# ---------------------------------------------------------------------------


def test_dashboard_presents_agent_summary() -> None:
    """Dashboard must expose high-level Agent/activity information."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Agent Summary")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.agent_summary is not None


def test_dashboard_agent_summary_has_expected_counters() -> None:
    """Agent summary must expose high-level counters."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Agent Counters")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    summary = presentation.agent_summary

    assert summary.active == 0
    assert summary.completed == 0
    assert summary.failed == 0


def test_dashboard_does_not_own_agent_runtime() -> None:
    """Dashboard must remain independent from Agent execution."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Agent Isolation")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "agent_runtime",
    )
    assert not hasattr(
        dashboard,
        "orchestrator",
    )
    assert not hasattr(
        dashboard,
        "coordinator",
    )


# ---------------------------------------------------------------------------
# Project status
# ---------------------------------------------------------------------------


def test_dashboard_presents_project_status() -> None:
    """Dashboard must expose project-level status."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Project Status")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.project_status is not None


def test_dashboard_project_status_is_not_fake_engineering_state() -> None:
    """Dashboard status must not become a new domain lifecycle."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Status Isolation")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "engineering_status",
    )


# ---------------------------------------------------------------------------
# Read-only behavior
# ---------------------------------------------------------------------------


def test_dashboard_refresh_does_not_replace_project() -> None:
    """Dashboard refresh must preserve canonical project identity."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Read Only Project")
    application = AtlasApplication(project)

    dashboard = AtlasDashboard(
        application=application,
    )

    dashboard.refresh()

    assert application.project is project


def test_dashboard_refresh_does_not_create_resources() -> None:
    """Dashboard rendering must not create Resources."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("No Mutation")
    application = AtlasApplication(project)

    before = project.resource_count

    dashboard = AtlasDashboard(
        application=application,
    )

    dashboard.refresh()

    after = project.resource_count

    assert before == after


def test_dashboard_refresh_does_not_mutate_relationships() -> None:
    """Dashboard rendering must not mutate the Project Graph."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Graph Read Only")
    application = AtlasApplication(project)

    before = project.relationship_count

    dashboard = AtlasDashboard(
        application=application,
    )

    dashboard.refresh()

    after = project.relationship_count

    assert before == after


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_dashboard_requires_atlas_application() -> None:
    """Dashboard must operate through the ENG-039 Application Boundary."""
    from atlas.application.dashboard import AtlasDashboard

    with pytest.raises(TypeError):
        AtlasDashboard(
            application="invalid",  # type: ignore[arg-type]
        )


def test_dashboard_exposes_application_reference() -> None:
    """Dashboard must be bound to the application boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Application Boundary"),
    )

    dashboard = AtlasDashboard(
        application=application,
    )

    assert dashboard.application is application


def test_dashboard_does_not_directly_own_atlas_project() -> None:
    """Dashboard must not become a project container."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Project Ownership"),
    )

    dashboard = AtlasDashboard(
        application=application,
    )

    assert not hasattr(
        dashboard,
        "project",
    )
    assert not hasattr(
        dashboard,
        "atlas_project",
    )


# ---------------------------------------------------------------------------
# Dashboard and Workspace
# ---------------------------------------------------------------------------


def test_dashboard_is_hostable_by_workspace() -> None:
    """Dashboard must be compatible with ENG-040 Workspace."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Dashboard Workspace"),
    )

    workspace = AtlasWorkspace(
        application=application,
    )

    dashboard = AtlasDashboard(
        application=application,
    )

    panel = AtlasPanel(
        panel_id=dashboard.dashboard_id,
        name="Dashboard",
    )

    workspace.register_panel(panel)

    assert workspace.panel_registry.get(
        "dashboard",
    ) is panel


def test_dashboard_panel_identity_is_dashboard() -> None:
    """Dashboard panel identity must be stable."""
    from atlas.application.dashboard import AtlasDashboard

    dashboard = AtlasDashboard()

    assert dashboard.dashboard_id == "dashboard"


# ---------------------------------------------------------------------------
# AtlasID-based selection
# ---------------------------------------------------------------------------


def test_dashboard_can_expose_identity_based_selection_target() -> None:
    """Dashboard navigation targets must use AtlasID."""
    from atlas.application.dashboard import AtlasDashboard
    from atlas.application.presentation import (
        AtlasDashboardSelectionTarget,
    )
    from atlas.core.aid import AtlasID

    dashboard = AtlasDashboard.__new__(AtlasDashboard)

    resource_id = AtlasID.generate()

    target = AtlasDashboardSelectionTarget(
        resource_id=resource_id,
    )

    assert target.resource_id == resource_id
    assert isinstance(
        target.resource_id,
        AtlasID,
    )


def test_dashboard_selection_target_does_not_store_resource_copy() -> None:
    """Selection targets must not embed canonical Resources."""
    from atlas.application.dashboard import (
        AtlasDashboardSelectionTarget,
    )
    from atlas.core.aid import AtlasID

    target = AtlasDashboardSelectionTarget(
        resource_id=AtlasID.generate(),
    )

    assert not hasattr(
        target,
        "resource",
    )
    assert not hasattr(
        target,
        "resource_copy",
    )


# ---------------------------------------------------------------------------
# Empty project
# ---------------------------------------------------------------------------


def test_dashboard_supports_empty_project() -> None:
    """An empty Atlas Project must produce valid Dashboard presentation."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    project = AtlasProject("Empty Project")

    application = AtlasApplication(project)
    dashboard = AtlasDashboard(
        application=application,
    )

    presentation = dashboard.refresh()

    assert presentation.project_name == "Empty Project"
    assert presentation.resource_summary.total == 0
    assert presentation.relationship_summary.total == 0
    assert presentation.validation_summary.errors == 0
    assert presentation.validation_summary.warnings == 0
    assert presentation.agent_summary.active == 0


# ---------------------------------------------------------------------------
# Refresh and determinism
# ---------------------------------------------------------------------------


def test_dashboard_refresh_returns_new_presentation() -> None:
    """Refreshing should produce a fresh derived presentation."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Refresh Project"),
    )

    dashboard = AtlasDashboard(
        application=application,
    )

    first = dashboard.refresh()
    second = dashboard.refresh()

    assert first is not second
    assert first.project_id == second.project_id


def test_dashboard_refresh_is_deterministic_for_unchanged_project() -> None:
    """Equivalent queries over unchanged state must be equivalent."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Deterministic Project"),
    )

    dashboard = AtlasDashboard(
        application=application,
    )

    first = dashboard.refresh()
    second = dashboard.refresh()

    assert first == second


# ---------------------------------------------------------------------------
# Persistence / exchange separation
# ---------------------------------------------------------------------------


def test_dashboard_does_not_own_serializer() -> None:
    """Dashboard must not implement serialization."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    dashboard = AtlasDashboard(
        application=AtlasApplication(
            AtlasProject("Serialization Isolation"),
        ),
    )

    assert not hasattr(
        dashboard,
        "serializer",
    )
    assert not hasattr(
        dashboard,
        "json_serializer",
    )


def test_dashboard_does_not_own_persistence() -> None:
    """Dashboard must not implement filesystem persistence."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    dashboard = AtlasDashboard(
        application=AtlasApplication(
            AtlasProject("Persistence Isolation"),
        ),
    )

    assert not hasattr(
        dashboard,
        "persistence",
    )
    assert not hasattr(
        dashboard,
        "save",
    )
    assert not hasattr(
        dashboard,
        "load",
    )


def test_dashboard_does_not_own_exchange() -> None:
    """Dashboard must not implement Import/Export."""
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    dashboard = AtlasDashboard(
        application=AtlasApplication(
            AtlasProject("Exchange Isolation"),
        ),
    )

    assert not hasattr(
        dashboard,
        "importer",
    )
    assert not hasattr(
        dashboard,
        "exporter",
    )


# ---------------------------------------------------------------------------
# AI / future extensibility
# ---------------------------------------------------------------------------


def test_dashboard_does_not_treat_ai_insight_as_engineering_truth() -> None:
    """
    Future AI insights must remain separate from canonical Dashboard facts.
    """
    from atlas.application import AtlasApplication
    from atlas.application.dashboard import AtlasDashboard
    from atlas.project.project import AtlasProject

    dashboard = AtlasDashboard(
        application=AtlasApplication(
            AtlasProject("AI Boundary"),
        ),
    )

    assert not hasattr(
        dashboard,
        "engineering_facts_from_ai",
    )


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_dashboard_public_exports_exist() -> None:
    """Dashboard contracts must be publicly accessible."""
    from atlas import application

    expected = {
        "AtlasDashboard",
        "AtlasDashboardPresentation",
        "AtlasDashboardSelectionTarget",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )
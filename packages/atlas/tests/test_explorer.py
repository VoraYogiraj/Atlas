"""
ENG-042 — Atlas Explorer

RED/GREEN tests for the Atlas Explorer capability.

The Explorer is a read-oriented navigation and discovery surface
inside the ENG-040 UI Application Shell.

These tests intentionally avoid coupling Atlas to any frontend framework.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Explorer type and identity
# ---------------------------------------------------------------------------


def test_explorer_type_exists() -> None:
    """Atlas must expose a dedicated Explorer capability."""
    from atlas.application.explorer import AtlasExplorer

    assert AtlasExplorer is not None


def test_explorer_has_stable_identity() -> None:
    """Explorer identity must be stable and UI-specific."""
    from atlas.application.explorer import AtlasExplorer

    explorer = AtlasExplorer.__new__(AtlasExplorer)

    assert explorer.explorer_id == "explorer"


def test_explorer_is_not_an_atlas_resource() -> None:
    """Explorer must remain a presentation object."""
    from atlas.application.explorer import AtlasExplorer
    from atlas.core.resource import AtlasResource

    explorer = AtlasExplorer.__new__(AtlasExplorer)

    assert not isinstance(
        explorer,
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Presentation model
# ---------------------------------------------------------------------------


def test_explorer_presentation_model_exists() -> None:
    """Explorer must expose a dedicated presentation representation."""
    from atlas.application.explorer import AtlasExplorerPresentation

    assert AtlasExplorerPresentation is not None


def test_explorer_node_exists() -> None:
    """Explorer must expose a generic presentation node."""
    from atlas.application.explorer import AtlasExplorerNode

    assert AtlasExplorerNode is not None


def test_explorer_node_supports_project_identity() -> None:
    """Project nodes must identify the project without embedding AtlasProject."""
    from atlas.application.explorer import AtlasExplorerNode

    node = AtlasExplorerNode(
        node_id="project",
        node_type="project",
        label="Sample Building",
    )

    assert node.node_id == "project"
    assert node.node_type == "project"
    assert node.label == "Sample Building"


def test_explorer_node_is_not_atlas_project() -> None:
    """Explorer nodes must remain presentation data."""
    from atlas.application.explorer import AtlasExplorerNode
    from atlas.project.project import AtlasProject

    node = AtlasExplorerNode(
        node_id="project",
        node_type="project",
        label="Sample Building",
    )

    assert not isinstance(
        node,
        AtlasProject,
    )


def test_explorer_presentation_is_not_atlas_project() -> None:
    """Explorer presentation must not replace the canonical Project."""
    from atlas.application.explorer import AtlasExplorerPresentation
    from atlas.project.project import AtlasProject

    presentation = AtlasExplorerPresentation(
        project_id="project-001",
        project_name="Sample Building",
    )

    assert not isinstance(
        presentation,
        AtlasProject,
    )


# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------


def test_explorer_can_read_project_identity() -> None:
    """Explorer must obtain the canonical Project identity."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Sample Building")

    application = AtlasApplication(project)
    explorer = AtlasExplorer(
        application=application,
    )

    presentation = explorer.refresh()

    assert presentation.project_id == str(project.aid)
    assert presentation.project_name == "Sample Building"


def test_explorer_provides_project_root() -> None:
    """Explorer must provide a Project root node."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Root Project"),
    )

    explorer = AtlasExplorer(
        application=application,
    )

    presentation = explorer.refresh()

    assert presentation.root is not None
    assert presentation.root.node_type == "project"


# ---------------------------------------------------------------------------
# Resource navigation
# ---------------------------------------------------------------------------


def test_explorer_can_present_resources() -> None:
    """Explorer must expose canonical Resources."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.core.resource import AtlasResource
    from atlas.project.project import AtlasProject

    project = AtlasProject("Resource Navigation")

    # The exact Resource registration contract is exercised here through
    # the canonical Project API.
    resource = AtlasResource(
        classification="wall",
        name="External Wall",
    )
    project.add_resource(resource)

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    presentation = explorer.refresh()

    resource_nodes = [
        node
        for node in presentation.nodes
        if node.node_type == "resource"
    ]

    assert len(resource_nodes) == 1
    assert resource_nodes[0].resource_id == resource.aid
    assert resource_nodes[0].label == "External Wall"


def test_explorer_resource_identity_is_atlas_id() -> None:
    """Explorer Resource nodes must use canonical AtlasID."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.core.aid import AtlasID
    from atlas.core.resource import AtlasResource
    from atlas.project.project import AtlasProject

    project = AtlasProject("Resource Identity")

    resource = AtlasResource(
        classification="wall",
        name="Wall 001",
    )
    project.add_resource(resource)

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    presentation = explorer.refresh()

    resource_nodes = [
        node
        for node in presentation.nodes
        if node.node_type == "resource"
    ]

    assert isinstance(
        resource_nodes[0].resource_id,
        AtlasID,
    )
    assert resource_nodes[0].resource_id == resource.aid


def test_explorer_does_not_copy_canonical_resource() -> None:
    """Explorer nodes must not embed canonical Resource objects."""
    from atlas.application.explorer import AtlasExplorerNode

    node = AtlasExplorerNode(
        node_id="resource-001",
        node_type="resource",
        label="Wall 001",
    )

    assert not hasattr(
        node,
        "resource",
    )
    assert not hasattr(
        node,
        "resource_copy",
    )


# ---------------------------------------------------------------------------
# Classification navigation
# ---------------------------------------------------------------------------


def test_explorer_supports_classification_nodes() -> None:
    """Explorer must represent Classification navigation."""
    from atlas.application.explorer import AtlasExplorerNode

    node = AtlasExplorerNode(
        node_id="classification-wall",
        node_type="classification",
        label="Wall",
    )

    assert node.node_type == "classification"


def test_explorer_does_not_own_classification_registry() -> None:
    """Explorer must not create a second Classification Registry."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Classification Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "classification_registry",
    )
    assert not hasattr(
        explorer,
        "classification_hierarchy",
    )


# ---------------------------------------------------------------------------
# Resource grouping
# ---------------------------------------------------------------------------


def test_explorer_can_group_resources_by_classification() -> None:
    """Resource grouping must support canonical Classification."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Grouping")

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    presentation = explorer.refresh(
        group_by="classification",
    )

    assert presentation is not None


def test_explorer_grouping_is_not_a_second_domain_model() -> None:
    """Grouping must remain presentation/query state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Grouping Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "group_registry",
    )


# ---------------------------------------------------------------------------
# Relationship visibility
# ---------------------------------------------------------------------------


def test_explorer_relationship_group_node_exists() -> None:
    """Explorer must support a Relationship Group presentation node."""
    from atlas.application.explorer import AtlasExplorerNode

    node = AtlasExplorerNode(
        node_id="relationships",
        node_type="relationship_group",
        label="Relationships",
    )

    assert node.node_type == "relationship_group"


def test_explorer_does_not_own_relationship_graph() -> None:
    """Explorer must not create a second Resource Graph."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Graph Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "graph",
    )
    assert not hasattr(
        explorer,
        "resource_graph",
    )
    assert not hasattr(
        explorer,
        "explorer_graph",
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def test_explorer_supports_search() -> None:
    """Explorer must provide a query-level search capability."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Search"),
        ),
    )

    results = explorer.search("wall")

    assert results is not None


def test_explorer_search_is_read_only() -> None:
    """Searching must not mutate the Project."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Search Read Only")

    application = AtlasApplication(project)
    explorer = AtlasExplorer(
        application=application,
    )

    before_resources = project.resource_count
    before_relationships = project.relationship_count

    explorer.search("wall")

    assert project.resource_count == before_resources
    assert project.relationship_count == before_relationships


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_explorer_supports_filtering() -> None:
    """Explorer must provide a query-level filtering capability."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Filtering"),
        ),
    )

    result = explorer.filter(
        classification="wall",
    )

    assert result is not None


def test_explorer_filtering_is_read_only() -> None:
    """Filtering must not mutate Atlas state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Filter Read Only")

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    before_resources = project.resource_count
    before_relationships = project.relationship_count

    explorer.filter(
        classification="wall",
    )

    assert project.resource_count == before_resources
    assert project.relationship_count == before_relationships


# ---------------------------------------------------------------------------
# Expansion / collapse state
# ---------------------------------------------------------------------------


def test_explorer_supports_expansion_state() -> None:
    """Explorer must maintain transient expansion state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Expansion"),
        ),
    )

    explorer.set_expanded(
        "project",
        True,
    )

    assert explorer.is_expanded("project") is True


def test_explorer_expansion_state_is_ui_state() -> None:
    """Expansion state must not be stored in Atlas Core."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Expansion Isolation")

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    explorer.set_expanded(
        "project",
        True,
    )

    assert not hasattr(
        project,
        "expanded",
    )


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def test_explorer_supports_atlas_id_selection() -> None:
    """Explorer selection must use AtlasID."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Selection"),
        ),
    )

    resource_id = AtlasID.generate()

    explorer.select_resource(resource_id)

    assert explorer.selected_resource_id == resource_id
    assert isinstance(
        explorer.selected_resource_id,
        AtlasID,
    )


def test_explorer_rejects_invalid_selection_identity() -> None:
    """Explorer must reject non-AtlasID selection values."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Selection Validation"),
        ),
    )

    with pytest.raises(TypeError):
        explorer.select_resource(
            "not-an-atlas-id",  # type: ignore[arg-type]
        )


def test_explorer_selection_does_not_store_resource_copy() -> None:
    """Selection must use identity rather than embedding a Resource."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Selection Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "selected_resource",
    )
    assert not hasattr(
        explorer,
        "resource_selection_object",
    )


# ---------------------------------------------------------------------------
# Selection handoff
# ---------------------------------------------------------------------------


def test_explorer_selection_can_produce_workspace_selection() -> None:
    """Explorer selection must be compatible with ENG-039 selection."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.application.selection import AtlasResourceSelection
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Selection Handoff"),
        ),
    )

    resource_id = AtlasID.generate()

    explorer.select_resource(resource_id)

    selection = explorer.to_selection()

    assert isinstance(
        selection,
        AtlasResourceSelection,
    )
    assert selection.resource_id == resource_id


# ---------------------------------------------------------------------------
# Workspace integration
# ---------------------------------------------------------------------------


def test_explorer_is_hostable_by_workspace() -> None:
    """Explorer must integrate with ENG-040 Workspace."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Explorer Workspace"),
    )

    workspace = AtlasWorkspace(
        application=application,
    )

    explorer = AtlasExplorer(
        application=application,
    )

    panel = AtlasPanel(
        panel_id=explorer.explorer_id,
        name="Explorer",
    )

    workspace.register_panel(panel)

    assert workspace.panel_registry.get(
        "explorer",
    ) is panel


def test_explorer_panel_identity_is_explorer() -> None:
    """Explorer panel identity must be stable."""
    from atlas.application.explorer import AtlasExplorer

    explorer = AtlasExplorer.__new__(AtlasExplorer)

    assert explorer.explorer_id == "explorer"


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_explorer_requires_atlas_application() -> None:
    """Explorer must operate through the ENG-039 Application Boundary."""
    from atlas.application.explorer import AtlasExplorer

    with pytest.raises(TypeError):
        AtlasExplorer(
            application="invalid",  # type: ignore[arg-type]
        )


def test_explorer_exposes_application_reference() -> None:
    """Explorer must remain bound to the Application Boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Application Boundary"),
    )

    explorer = AtlasExplorer(
        application=application,
    )

    assert explorer.application is application


def test_explorer_does_not_directly_own_atlas_project() -> None:
    """Explorer must not become a Project container."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Project Ownership"),
        ),
    )

    assert not hasattr(
        explorer,
        "project",
    )
    assert not hasattr(
        explorer,
        "atlas_project",
    )


# ---------------------------------------------------------------------------
# Empty project
# ---------------------------------------------------------------------------


def test_explorer_supports_empty_project() -> None:
    """Empty Atlas Projects must produce valid Explorer state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Empty Explorer Project")

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    presentation = explorer.refresh()

    assert presentation.project_name == "Empty Explorer Project"
    assert presentation.root is not None
    assert presentation.nodes


# ---------------------------------------------------------------------------
# Loading / error states
# ---------------------------------------------------------------------------


def test_explorer_exposes_loading_state() -> None:
    """Explorer must distinguish loading state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Loading"),
        ),
    )

    assert explorer.is_loading is False

    explorer.set_loading(True)

    assert explorer.is_loading is True


def test_explorer_loading_state_is_not_project_state() -> None:
    """Loading state must remain UI state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    project = AtlasProject("Loading Isolation")

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    explorer.set_loading(True)

    assert not hasattr(
        project,
        "loading",
    )


def test_explorer_exposes_error_state() -> None:
    """Explorer must support an explicit presentation error state."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Error State"),
        ),
    )

    explorer.set_error("Explorer query failed")

    assert explorer.error == "Explorer query failed"


# ---------------------------------------------------------------------------
# Deterministic ordering
# ---------------------------------------------------------------------------


def test_explorer_refresh_is_deterministic() -> None:
    """Equivalent queries on unchanged state must be equivalent."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Deterministic Explorer"),
    )

    explorer = AtlasExplorer(
        application=application,
    )

    first = explorer.refresh()
    second = explorer.refresh()

    assert first == second


def test_explorer_preserves_registry_order() -> None:
    """Explorer should preserve canonical Resource Registry order."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.core.resource import AtlasResource
    from atlas.project.project import AtlasProject

    project = AtlasProject("Registry Order")

    first = AtlasResource(
        classification="wall",
        name="Wall A",
    )
    second = AtlasResource(
        classification="wall",
        name="Wall B",
    )

    project.add_resource(first)
    project.add_resource(second)

    explorer = AtlasExplorer(
        application=AtlasApplication(project),
    )

    presentation = explorer.refresh()

    resource_nodes = [
        node
        for node in presentation.nodes
        if node.node_type == "resource"
    ]

    assert [
        node.resource_id
        for node in resource_nodes
    ] == [
        first.aid,
        second.aid,
    ]


# ---------------------------------------------------------------------------
# Core isolation
# ---------------------------------------------------------------------------


def test_explorer_does_not_own_resource_registry() -> None:
    """Explorer must not own an independent Resource Registry."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Registry Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "resource_registry",
    )
    assert not hasattr(
        explorer,
        "explorer_resource_registry",
    )


def test_explorer_does_not_own_graph() -> None:
    """Explorer must not own an independent Graph."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Graph Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "explorer_graph",
    )


# ---------------------------------------------------------------------------
# Persistence / exchange isolation
# ---------------------------------------------------------------------------


def test_explorer_does_not_own_serializer() -> None:
    """Explorer must not implement serialization."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Serialization Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "serializer",
    )
    assert not hasattr(
        explorer,
        "json_serializer",
    )


def test_explorer_does_not_own_persistence() -> None:
    """Explorer must not implement Save/Load."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Persistence Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "persistence",
    )
    assert not hasattr(
        explorer,
        "save",
    )
    assert not hasattr(
        explorer,
        "load",
    )


def test_explorer_does_not_own_exchange() -> None:
    """Explorer must not implement Import/Export."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Exchange Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "importer",
    )
    assert not hasattr(
        explorer,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Agent / AI boundaries
# ---------------------------------------------------------------------------


def test_explorer_does_not_own_agent_runtime() -> None:
    """Explorer must not directly execute or own Agents."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("Agent Isolation"),
        ),
    )

    assert not hasattr(
        explorer,
        "agent_runtime",
    )
    assert not hasattr(
        explorer,
        "orchestrator",
    )
    assert not hasattr(
        explorer,
        "coordinator",
    )


def test_explorer_does_not_treat_ai_as_engineering_truth() -> None:
    """Future AI assistance must remain separate from canonical facts."""
    from atlas.application import AtlasApplication
    from atlas.application.explorer import AtlasExplorer
    from atlas.project.project import AtlasProject

    explorer = AtlasExplorer(
        application=AtlasApplication(
            AtlasProject("AI Boundary"),
        ),
    )

    assert not hasattr(
        explorer,
        "engineering_facts_from_ai",
    )


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_explorer_public_exports_exist() -> None:
    """Explorer contracts must be publicly accessible."""
    from atlas import application

    expected = {
        "AtlasExplorer",
        "AtlasExplorerNode",
        "AtlasExplorerPresentation",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )
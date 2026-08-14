"""
ENG-043 — Atlas Inspector

RED/GREEN tests for the Atlas Inspector capability.

The Inspector is a read-oriented Resource-level detail surface inside the
ENG-040 UI Application Shell.

These tests intentionally avoid coupling Atlas to any frontend framework.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _wall_classification():
    from atlas.classification.classification import AtlasClassification

    return AtlasClassification(
        id="wall",
        name="Wall",
        description="Building wall",
    )


def _project_with_resource(
    project_name: str = "Inspector Project",
):
    from atlas.core.resource import AtlasResource
    from atlas.project.project import AtlasProject

    project = AtlasProject(project_name)

    wall = _wall_classification()
    project.add_classification(wall)

    resource = AtlasResource(
        classification=wall,
        name="External Wall",
    )

    project.add_resource(resource)

    return project, resource, wall


def _project_with_relationship():
    from atlas.core.resource import AtlasResource
    from atlas.project.project import AtlasProject
    from atlas.relationships.relationship import AtlasRelationship

    project = AtlasProject("Inspector Relationships")

    wall = _wall_classification()
    project.add_classification(wall)

    source = AtlasResource(
        classification=wall,
        name="Wall A",
    )

    target = AtlasResource(
        classification=wall,
        name="Wall B",
    )

    project.add_resource(source)
    project.add_resource(target)

    relationship = AtlasRelationship(
        id="relationship-001",
        relationship_type="connects",
        source=source,
        target=target,
        description="Wall connection",
    )

    project.add_relationship(relationship)

    return project, source, target, relationship


# ---------------------------------------------------------------------------
# Inspector type and identity
# ---------------------------------------------------------------------------


def test_inspector_type_exists() -> None:
    """Atlas must expose a dedicated Inspector capability."""
    from atlas.application.inspector import AtlasInspector

    assert AtlasInspector is not None


def test_inspector_has_stable_identity() -> None:
    """Inspector identity must be stable and UI-specific."""
    from atlas.application.inspector import AtlasInspector

    inspector = AtlasInspector.__new__(AtlasInspector)

    assert inspector.inspector_id == "inspector"


def test_inspector_is_not_an_atlas_resource() -> None:
    """Inspector must remain a presentation capability."""
    from atlas.application.inspector import AtlasInspector
    from atlas.core.resource import AtlasResource

    inspector = AtlasInspector.__new__(AtlasInspector)

    assert not isinstance(
        inspector,
        AtlasResource,
    )


# ---------------------------------------------------------------------------
# Presentation model
# ---------------------------------------------------------------------------


def test_inspector_presentation_model_exists() -> None:
    """Inspector must expose a dedicated presentation model."""
    from atlas.application.inspector import AtlasInspectorPresentation

    assert AtlasInspectorPresentation is not None


def test_inspector_presentation_is_not_atlas_resource() -> None:
    """Presentation data must not replace AtlasResource."""
    from atlas.application.inspector import AtlasInspectorPresentation
    from atlas.core.aid import AtlasID
    from atlas.core.resource import AtlasResource

    presentation = AtlasInspectorPresentation(
        resource_id=AtlasID.generate(),
        name="External Wall",
    )

    assert not isinstance(
        presentation,
        AtlasResource,
    )


def test_inspector_presentation_does_not_store_resource_object() -> None:
    """Presentation must not embed canonical AtlasResource."""
    from atlas.application.inspector import AtlasInspectorPresentation
    from atlas.core.aid import AtlasID

    presentation = AtlasInspectorPresentation(
        resource_id=AtlasID.generate(),
        name="External Wall",
    )

    assert not hasattr(
        presentation,
        "resource",
    )
    assert not hasattr(
        presentation,
        "atlas_resource",
    )


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_inspector_requires_atlas_application() -> None:
    """Inspector must operate through ENG-039 AtlasApplication."""
    from atlas.application.inspector import AtlasInspector

    with pytest.raises(TypeError):
        AtlasInspector(
            application="invalid",  # type: ignore[arg-type]
        )


def test_inspector_exposes_application_reference() -> None:
    """Inspector must remain bound to the Application Boundary."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Application Boundary"),
    )

    inspector = AtlasInspector(
        application=application,
    )

    assert inspector.application is application


def test_inspector_does_not_directly_own_project() -> None:
    """Inspector must not become an AtlasProject container."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Project Ownership"),
        ),
    )

    assert not hasattr(
        inspector,
        "project",
    )
    assert not hasattr(
        inspector,
        "atlas_project",
    )


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def test_inspector_accepts_atlas_id_selection() -> None:
    """Inspector selection must use canonical AtlasID."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Selection"),
        ),
    )

    resource_id = AtlasID.generate()

    inspector.set_selection(resource_id)

    assert inspector.selected_resource_id == resource_id
    assert isinstance(
        inspector.selected_resource_id,
        AtlasID,
    )


def test_inspector_accepts_workspace_selection() -> None:
    """Inspector must consume the ENG-039 selection model."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.application.selection import AtlasResourceSelection
    from atlas.project.project import AtlasProject

    resource_id = (
        AtlasResourceSelection.__dataclass_fields__["resource_id"]
    )

    assert resource_id is not None

    project = AtlasProject("Workspace Selection")

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    # Use a real AtlasID through the canonical selection object.
    from atlas.core.aid import AtlasID

    selected_id = AtlasID.generate()

    selection = AtlasResourceSelection(
        resource_id=selected_id,
    )

    inspector.set_selection(
        selection.resource_id,
    )

    assert inspector.selected_resource_id == selected_id


def test_inspector_rejects_invalid_selection_identity() -> None:
    """Inspector must reject invalid Resource identity values."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Selection Validation"),
        ),
    )

    with pytest.raises(TypeError):
        inspector.set_selection(
            "not-an-atlas-id",  # type: ignore[arg-type]
        )


def test_inspector_can_clear_selection() -> None:
    """Inspector must support an empty selection."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Clear Selection"),
        ),
    )

    inspector.set_selection(
        AtlasID.generate(),
    )

    inspector.set_selection(None)

    assert inspector.selected_resource_id is None


# ---------------------------------------------------------------------------
# Resource identity and details
# ---------------------------------------------------------------------------


def test_inspector_can_present_resource_identity() -> None:
    """Inspector must present canonical Resource identity."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Resource Identity",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation is not None
    assert presentation.resource_id == resource.aid
    assert presentation.name == "External Wall"


def test_inspector_presents_classification() -> None:
    """Inspector must present canonical Resource Classification."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, classification = _project_with_resource(
        "Classification",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation.classification is not None
    assert presentation.classification.id == classification.id
    assert presentation.classification.name == classification.name


def test_inspector_presents_classification_path() -> None:
    """Inspector must preserve canonical classification hierarchy."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, classification = _project_with_resource(
        "Classification Path",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation.classification_path == classification.path


def test_inspector_presents_lifecycle() -> None:
    """Inspector must present the canonical Resource lifecycle."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Lifecycle",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation.lifecycle is not None
    assert presentation.lifecycle == resource.lifecycle


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_inspector_presents_properties() -> None:
    """Inspector must expose canonical Resource properties."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Properties",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation.properties == resource.properties


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def test_inspector_presents_metadata() -> None:
    """Inspector must expose canonical Resource metadata."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Metadata",
    )

    resource.metadata["discipline"] = "architectural"

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert presentation.metadata == resource.metadata


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


def test_inspector_presents_tags() -> None:
    """Inspector must expose semantic tags."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.semantic_tags.tag import AtlasSemanticTag

    project, resource, _ = _project_with_resource(
        "Tags",
    )

    tag = AtlasSemanticTag(
        id="external",
        name="External",
        description="External building element",
    )

    resource.add_tag(tag)

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert len(presentation.tags) == 1
    assert presentation.tags[0].id == "external"


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


def test_inspector_presents_categories() -> None:
    """Inspector must expose Resource categories."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.categories.category import AtlasCategory

    project, resource, _ = _project_with_resource(
        "Categories",
    )

    category = AtlasCategory(
        id="architectural",
        name="Architectural",
        description="Architectural elements",
    )

    resource.add_category(category)

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    presentation = inspector.refresh()

    assert len(presentation.categories) == 1
    assert presentation.categories[0].id == "architectural"


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------


def test_inspector_presents_relationships() -> None:
    """Inspector must expose Resource relationship context."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, source, _, relationship = _project_with_relationship()

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(source.aid)

    presentation = inspector.refresh()

    assert len(presentation.relationships) == 1
    assert presentation.relationships[0].relationship_id == (
        relationship.id
    )


def test_inspector_preserves_relationship_direction() -> None:
    """Inspector must preserve source/target relationship direction."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, source, target, _ = _project_with_relationship()

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(source.aid)

    presentation = inspector.refresh()
    relationship = presentation.relationships[0]

    assert relationship.source_id == source.aid
    assert relationship.target_id == target.aid
    assert relationship.relationship_type == "connects"


def test_inspector_relationship_target_is_atlas_id() -> None:
    """Relationship navigation targets must remain AtlasID-based."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.core.aid import AtlasID

    project, source, target, _ = _project_with_relationship()

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(source.aid)

    presentation = inspector.refresh()
    relationship = presentation.relationships[0]

    assert isinstance(
        relationship.source_id,
        AtlasID,
    )
    assert isinstance(
        relationship.target_id,
        AtlasID,
    )

    assert relationship.target_id == target.aid


# ---------------------------------------------------------------------------
# Empty / unavailable selection
# ---------------------------------------------------------------------------


def test_inspector_supports_empty_selection() -> None:
    """Inspector must support no selected Resource."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Empty Selection"),
        ),
    )

    presentation = inspector.refresh()

    assert presentation is None
    assert inspector.selected_resource_id is None


def test_inspector_handles_missing_resource() -> None:
    """Inspector must explicitly handle a missing Resource."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.core.aid import AtlasID
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Missing Resource"),
        ),
    )

    inspector.set_selection(
        AtlasID.generate(),
    )

    with pytest.raises(KeyError):
        inspector.refresh()


# ---------------------------------------------------------------------------
# Loading / error state
# ---------------------------------------------------------------------------


def test_inspector_exposes_loading_state() -> None:
    """Inspector must expose transient loading state."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Loading"),
        ),
    )

    assert inspector.is_loading is False

    inspector.set_loading(True)

    assert inspector.is_loading is True


def test_inspector_loading_state_is_not_resource_state() -> None:
    """Inspector loading state must remain outside AtlasResource."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Loading Isolation",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)
    inspector.set_loading(True)

    assert not hasattr(
        resource,
        "loading",
    )


def test_inspector_exposes_error_state() -> None:
    """Inspector must expose explicit UI/application error state."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Error State"),
        ),
    )

    inspector.set_error(
        "Inspector query failed",
    )

    assert inspector.error == "Inspector query failed"


# ---------------------------------------------------------------------------
# Workspace integration
# ---------------------------------------------------------------------------


def test_inspector_is_hostable_by_workspace() -> None:
    """Inspector must integrate with ENG-040 Workspace."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.application.panel import AtlasPanel
    from atlas.application.workspace import AtlasWorkspace
    from atlas.project.project import AtlasProject

    application = AtlasApplication(
        AtlasProject("Inspector Workspace"),
    )

    workspace = AtlasWorkspace(
        application=application,
    )

    inspector = AtlasInspector(
        application=application,
    )

    panel = AtlasPanel(
        panel_id=inspector.inspector_id,
        name="Inspector",
    )

    workspace.register_panel(panel)

    assert workspace.panel_registry.get(
        "inspector",
    ) is panel


def test_inspector_panel_identity_is_inspector() -> None:
    """Inspector panel identity must be stable."""
    from atlas.application.inspector import AtlasInspector

    inspector = AtlasInspector.__new__(AtlasInspector)

    assert inspector.inspector_id == "inspector"


# ---------------------------------------------------------------------------
# Read-only behavior
# ---------------------------------------------------------------------------


def test_inspector_refresh_does_not_create_resources() -> None:
    """Inspector refresh must not create Resources."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "No Resource Mutation",
    )

    before = project.resource_count

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)
    inspector.refresh()

    assert project.resource_count == before


def test_inspector_refresh_does_not_mutate_relationships() -> None:
    """Inspector refresh must not mutate Project relationships."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "No Relationship Mutation",
    )

    before = project.relationship_count

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)
    inspector.refresh()

    assert project.relationship_count == before


def test_inspector_does_not_own_mutation_methods() -> None:
    """ENG-043 must remain read-only."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Read Only API"),
        ),
    )

    assert not hasattr(
        inspector,
        "create_resource",
    )
    assert not hasattr(
        inspector,
        "delete_resource",
    )
    assert not hasattr(
        inspector,
        "update_resource",
    )
    assert not hasattr(
        inspector,
        "set_property",
    )
    assert not hasattr(
        inspector,
        "remove_property",
    )


# ---------------------------------------------------------------------------
# Core isolation
# ---------------------------------------------------------------------------


def test_inspector_does_not_own_resource_registry() -> None:
    """Inspector must not own a second Resource Registry."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Registry Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "resource_registry",
    )
    assert not hasattr(
        inspector,
        "inspector_resource_registry",
    )


def test_inspector_does_not_own_graph() -> None:
    """Inspector must not own a second Resource Graph."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Graph Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "graph",
    )
    assert not hasattr(
        inspector,
        "resource_graph",
    )
    assert not hasattr(
        inspector,
        "inspector_graph",
    )


def test_inspector_does_not_own_resource_model() -> None:
    """Inspector must not create a competing engineering Resource model."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Resource Model Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "resources",
    )
    assert not hasattr(
        inspector,
        "resource_model",
    )


# ---------------------------------------------------------------------------
# Persistence / exchange isolation
# ---------------------------------------------------------------------------


def test_inspector_does_not_own_serializer() -> None:
    """Inspector must not implement serialization."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Serialization Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "serializer",
    )
    assert not hasattr(
        inspector,
        "json_serializer",
    )


def test_inspector_does_not_own_persistence() -> None:
    """Inspector must not implement Save/Load."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Persistence Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "persistence",
    )
    assert not hasattr(
        inspector,
        "save",
    )
    assert not hasattr(
        inspector,
        "load",
    )


def test_inspector_does_not_own_exchange() -> None:
    """Inspector must not implement Import/Export."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Exchange Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "importer",
    )
    assert not hasattr(
        inspector,
        "exporter",
    )


# ---------------------------------------------------------------------------
# Agent / AI boundaries
# ---------------------------------------------------------------------------


def test_inspector_does_not_own_agent_runtime() -> None:
    """Inspector must not directly execute or own Agents."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("Agent Isolation"),
        ),
    )

    assert not hasattr(
        inspector,
        "agent_runtime",
    )
    assert not hasattr(
        inspector,
        "orchestrator",
    )
    assert not hasattr(
        inspector,
        "coordinator",
    )


def test_inspector_does_not_treat_ai_as_engineering_truth() -> None:
    """Future AI interpretation must remain distinct from canonical facts."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector
    from atlas.project.project import AtlasProject

    inspector = AtlasInspector(
        application=AtlasApplication(
            AtlasProject("AI Boundary"),
        ),
    )

    assert not hasattr(
        inspector,
        "engineering_facts_from_ai",
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_inspector_refresh_is_deterministic() -> None:
    """Equivalent queries over unchanged Resource state must be equivalent."""
    from atlas.application import AtlasApplication
    from atlas.application.inspector import AtlasInspector

    project, resource, _ = _project_with_resource(
        "Determinism",
    )

    inspector = AtlasInspector(
        application=AtlasApplication(project),
    )

    inspector.set_selection(resource.aid)

    first = inspector.refresh()
    second = inspector.refresh()

    assert first == second


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


def test_inspector_public_exports_exist() -> None:
    """Inspector contracts must be publicly accessible."""
    from atlas import application

    expected = {
        "AtlasInspector",
        "AtlasInspectorPresentation",
        "AtlasInspectorRelationship",
        "AtlasInspectorClassification",
    }

    for name in expected:
        assert hasattr(
            application,
            name,
        )
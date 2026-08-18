"""
ENG-057 — Atlas Resource Duplicate

RED phase tests.

These tests define the canonical Resource Duplicate contract before
implementation exists.

Expected initial state:
    atlas.application.duplicate_resource does not yet exist
    or the required duplicate behavior is not implemented.
"""

from __future__ import annotations

from copy import deepcopy

import pytest

from atlas.application import AtlasApplication, AtlasCommand
from atlas.core.aid import AtlasID
from atlas.core.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_project() -> AtlasProject:
    """Create a minimal Project suitable for Resource editing tests."""
    return AtlasProject(name="ENG-057 Duplicate Test Project")


def _make_classification(
    project: AtlasProject,
    *,
    classification_id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    """Create and register a minimal Classification."""
    classification = AtlasClassification(
        id=classification_id,
        name=name,
    )
    project.add_classification(classification)
    return classification


def _make_resource(
    project: AtlasProject,
    *,
    classification: AtlasClassification,
    name: str = "Wall",
) -> AtlasResource:
    """Create and register a Resource through the canonical Project API."""
    resource = AtlasResource(
        classification=classification,
        name=name,
    )
    project.add_resource(resource)
    return resource


def _duplicate(
    application: AtlasApplication,
    resource_id: AtlasID,
):
    """Execute the canonical duplicate command."""
    return application.execute(
        AtlasCommand(
            name="duplicate_resource",
            payload={
                "resource_id": resource_id,
            },
        )
    )


# ---------------------------------------------------------------------------
# Construction / command boundary
# ---------------------------------------------------------------------------


def test_duplicate_command_is_accepted_by_application():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    result = _duplicate(application, resource.aid)

    assert result is not None


def test_duplicate_returns_atlas_resource():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert isinstance(duplicate, AtlasResource)


# ---------------------------------------------------------------------------
# Source resolution
# ---------------------------------------------------------------------------


def test_duplicate_requires_existing_source_resource():
    project = _make_project()
    application = AtlasApplication(project)

    missing_id = AtlasID.generate()

    with pytest.raises(KeyError):
        _duplicate(application, missing_id)


def test_duplicate_source_id_must_be_atlas_id():
    project = _make_project()
    classification = _make_classification(project)
    _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    with pytest.raises(TypeError):
        application.execute(
            AtlasCommand(
                name="duplicate_resource",
                payload={
                    "resource_id": "not-an-atlas-id",
                },
            )
        )


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_duplicate_receives_new_atlas_id():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.aid != resource.aid


def test_duplicate_is_distinct_resource_object():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate is not resource


def test_source_atlas_id_is_unchanged():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    original_id = resource.aid
    application = AtlasApplication(project)

    _duplicate(application, resource.aid)

    assert resource.aid == original_id


def test_duplicate_id_is_not_caller_supplied():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    caller_supplied_id = AtlasID.generate()

    with pytest.raises(TypeError):
        application.execute(
            AtlasCommand(
                name="duplicate_resource",
                payload={
                    "resource_id": resource.aid,
                    "new_resource_id": caller_supplied_id,
                },
            )
        )


# ---------------------------------------------------------------------------
# Project ownership / registry
# ---------------------------------------------------------------------------


def test_duplicate_belongs_to_same_project():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert project.get_resource(duplicate.aid) is duplicate


def test_source_remains_registered_after_duplicate():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    _duplicate(application, resource.aid)

    assert project.get_resource(resource.aid) is resource


def test_registry_contains_both_source_and_duplicate():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert project.get_resource(resource.aid) is resource
    assert project.get_resource(duplicate.aid) is duplicate


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def test_duplicate_preserves_classification():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.classification is classification


def test_classification_definition_is_not_duplicated():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.classification is resource.classification


# ---------------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------------


def test_duplicate_preserves_name():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
        name="North Wall",
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.name == resource.name


def test_duplicate_does_not_invent_name_suffix():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
        name="North Wall",
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.name == "North Wall"


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_duplicate_copies_properties():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.properties["material"] = "concrete"
    resource.properties["thickness"] = 150

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.properties == resource.properties


def test_duplicate_properties_are_independent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.properties["material"] = "concrete"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    duplicate.properties["material"] = "brick"

    assert resource.properties["material"] == "concrete"
    assert duplicate.properties["material"] == "brick"


def test_duplicate_nested_properties_are_independent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.properties["dimensions"] = {
        "width": 200,
        "height": 300,
    }

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    duplicate.properties["dimensions"]["width"] = 500

    assert resource.properties["dimensions"]["width"] == 200
    assert duplicate.properties["dimensions"]["width"] == 500


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def test_duplicate_copies_metadata():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.metadata["source"] = "architect"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.metadata == resource.metadata


def test_duplicate_metadata_is_independent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.metadata["source"] = "architect"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    duplicate.metadata["source"] = "engineer"

    assert resource.metadata["source"] == "architect"
    assert duplicate.metadata["source"] == "engineer"


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


def test_duplicate_copies_tags():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.tags["discipline"] = "architecture"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.tags == resource.tags


def test_duplicate_tag_membership_is_independent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.tags["discipline"] = "architecture"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    duplicate.tags["discipline"] = "structural"

    assert resource.tags["discipline"] == "architecture"
    assert duplicate.tags["discipline"] == "structural"


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


def test_duplicate_copies_categories():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.categories["system"] = "building"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.categories == resource.categories


def test_duplicate_category_membership_is_independent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    resource.categories["system"] = "building"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    duplicate.categories["system"] = "infrastructure"

    assert resource.categories["system"] == "building"
    assert duplicate.categories["system"] == "infrastructure"


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def test_duplicate_uses_new_resource_creation_lifecycle():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.lifecycle == resource.lifecycle


def test_duplicate_does_not_mutate_source_lifecycle():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    original_lifecycle = resource.lifecycle
    application = AtlasApplication(project)

    _duplicate(application, resource.aid)

    assert resource.lifecycle == original_lifecycle


# ---------------------------------------------------------------------------
# Spatial state
# ---------------------------------------------------------------------------


def test_duplicate_copies_position():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_position(
        resource.aid,
        (10.0, 20.0, 30.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert project.get_resource_position(
        duplicate.aid,
    ) == project.get_resource_position(resource.aid)


def test_duplicate_copies_rotation():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_rotation(
        resource.aid,
        (10.0, 20.0, 30.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert project.get_resource_rotation(
        duplicate.aid,
    ) == project.get_resource_rotation(resource.aid)


def test_duplicate_copies_scale():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_scale(
        resource.aid,
        (2.0, 3.0, 4.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert project.get_resource_scale(
        duplicate.aid,
    ) == project.get_resource_scale(resource.aid)


def test_duplicate_spatial_state_is_keyed_by_new_atlas_id():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_position(
        resource.aid,
        (10.0, 20.0, 30.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.aid != resource.aid
    assert project.get_resource_position(
        duplicate.aid,
    ) == (10.0, 20.0, 30.0)


def test_moving_duplicate_does_not_move_source():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_position(
        resource.aid,
        (10.0, 20.0, 30.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    project.set_resource_position(
        duplicate.aid,
        (100.0, 200.0, 300.0),
    )

    assert project.get_resource_position(
        resource.aid,
    ) == (10.0, 20.0, 30.0)


def test_rotating_duplicate_does_not_rotate_source():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_rotation(
        resource.aid,
        (10.0, 20.0, 30.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    project.set_resource_rotation(
        duplicate.aid,
        (90.0, 45.0, 10.0),
    )

    assert project.get_resource_rotation(
        resource.aid,
    ) == (10.0, 20.0, 30.0)


def test_scaling_duplicate_does_not_scale_source():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_scale(
        resource.aid,
        (2.0, 3.0, 4.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    project.set_resource_scale(
        duplicate.aid,
        (5.0, 6.0, 7.0),
    )

    assert project.get_resource_scale(
        resource.aid,
    ) == (2.0, 3.0, 4.0)


# ---------------------------------------------------------------------------
# Relationship semantics
# ---------------------------------------------------------------------------


def test_duplicate_does_not_clone_relationships():
    project = _make_project()
    classification = _make_classification(project)

    source = _make_resource(
        project,
        classification=classification,
        name="Source",
    )
    target = _make_resource(
        project,
        classification=classification,
        name="Target",
    )

    project.add_relationship(
        source=source,
        target=target,
        relationship_type="depends_on",
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, source.aid)

    relationships = project.graph.relationships

    assert not any(
        relationship.source is duplicate
        for relationship in relationships
    )


def test_source_relationships_remain_unchanged():
    project = _make_project()
    classification = _make_classification(project)

    source = _make_resource(
        project,
        classification=classification,
        name="Source",
    )
    target = _make_resource(
        project,
        classification=classification,
        name="Target",
    )

    project.add_relationship(
        source=source,
        target=target,
        relationship_type="depends_on",
    )

    before = list(project.graph.relationships)

    application = AtlasApplication(project)

    _duplicate(application, source.aid)

    after = list(project.graph.relationships)

    assert after == before


def test_duplicate_does_not_create_reverse_relationship():
    project = _make_project()
    classification = _make_classification(project)

    source = _make_resource(
        project,
        classification=classification,
    )
    target = _make_resource(
        project,
        classification=classification,
    )

    project.add_relationship(
        source=source,
        target=target,
        relationship_type="depends_on",
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, source.aid)

    assert not any(
        relationship.source is duplicate
        or relationship.target is duplicate
        for relationship in project.graph.relationships
    )


# ---------------------------------------------------------------------------
# Source preservation
# ---------------------------------------------------------------------------


def test_duplicate_does_not_modify_source_resource_state():
    project = _make_project()
    classification = _make_classification(project)

    resource = _make_resource(
        project,
        classification=classification,
        name="Original",
    )
    resource.properties["material"] = "concrete"
    resource.metadata["source"] = "architect"
    resource.tags["discipline"] = "architecture"
    resource.categories["system"] = "building"

    original_properties = deepcopy(resource.properties)
    original_metadata = deepcopy(resource.metadata)
    original_tags = deepcopy(resource.tags)
    original_categories = deepcopy(resource.categories)

    application = AtlasApplication(project)

    _duplicate(application, resource.aid)

    assert resource.properties == original_properties
    assert resource.metadata == original_metadata
    assert resource.tags == original_tags
    assert resource.categories == original_categories
    assert resource.name == "Original"


# ---------------------------------------------------------------------------
# Repeated duplication
# ---------------------------------------------------------------------------


def test_duplicate_is_not_idempotent():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    first = _duplicate(application, resource.aid)
    second = _duplicate(application, resource.aid)

    assert first.aid != second.aid
    assert first is not second


def test_duplicate_can_duplicate_duplicate():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
        name="Original",
    )
    application = AtlasApplication(project)

    first = _duplicate(application, resource.aid)
    second = _duplicate(application, first.aid)

    assert second.aid != first.aid
    assert second.aid != resource.aid
    assert second.name == first.name


# ---------------------------------------------------------------------------
# Delete compatibility
# ---------------------------------------------------------------------------


def test_deleting_source_does_not_delete_duplicate():
    project = _make_project()
    classification = _make_classification(project)
    source = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, source.aid)

    application.execute(
        AtlasCommand(
            name="delete_resource",
            payload={
                "resource_id": source.aid,
            },
        )
    )

    assert project.get_resource(duplicate.aid) is duplicate


def test_deleting_duplicate_does_not_delete_source():
    project = _make_project()
    classification = _make_classification(project)
    source = _make_resource(
        project,
        classification=classification,
    )
    application = AtlasApplication(project)

    duplicate = _duplicate(application, source.aid)

    application.execute(
        AtlasCommand(
            name="delete_resource",
            payload={
                "resource_id": duplicate.aid,
            },
        )
    )

    assert project.get_resource(source.aid) is source


# ---------------------------------------------------------------------------
# Spatial independence after duplication
# ---------------------------------------------------------------------------


def test_duplicate_position_is_independent_from_source():
    project = _make_project()
    classification = _make_classification(project)
    source = _make_resource(
        project,
        classification=classification,
    )

    project.set_resource_position(
        source.aid,
        (1.0, 2.0, 3.0),
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, source.aid)

    project.set_resource_position(
        duplicate.aid,
        (4.0, 5.0, 6.0),
    )

    assert project.get_resource_position(
        source.aid,
    ) == (1.0, 2.0, 3.0)

    assert project.get_resource_position(
        duplicate.aid,
    ) == (4.0, 5.0, 6.0)


# ---------------------------------------------------------------------------
# Boundary isolation
# ---------------------------------------------------------------------------


def test_duplicate_does_not_require_scene():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate is not None


def test_duplicate_does_not_require_scene_node():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert not hasattr(duplicate, "scene_node")


def test_duplicate_does_not_require_selection():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.aid != resource.aid


def test_duplicate_does_not_require_gizmo():
    project = _make_project()
    classification = _make_classification(project)
    resource = _make_resource(
        project,
        classification=classification,
    )

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.aid != resource.aid


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_duplicate_preserves_equivalent_resource_state():
    project = _make_project()
    classification = _make_classification(project)

    resource = _make_resource(
        project,
        classification=classification,
        name="Wall",
    )
    resource.properties["material"] = "concrete"
    resource.properties["thickness"] = 200
    resource.metadata["source"] = "architect"
    resource.tags["discipline"] = "architecture"
    resource.categories["system"] = "building"

    application = AtlasApplication(project)

    duplicate = _duplicate(application, resource.aid)

    assert duplicate.aid != resource.aid
    assert duplicate.classification is resource.classification
    assert duplicate.name == resource.name
    assert duplicate.properties == resource.properties
    assert duplicate.metadata == resource.metadata
    assert duplicate.tags == resource.tags
    assert duplicate.categories == resource.categories


# ---------------------------------------------------------------------------
# Failure atomicity
# ---------------------------------------------------------------------------


def test_failed_duplicate_does_not_add_resource():
    project = _make_project()
    application = AtlasApplication(project)

    missing_id = AtlasID.generate()

    before = list(project.resources)

    with pytest.raises(KeyError):
        _duplicate(application, missing_id)

    after = list(project.resources)

    assert after == before


def test_failed_duplicate_does_not_create_spatial_state():
    project = _make_project()
    application = AtlasApplication(project)

    missing_id = AtlasID.generate()

    with pytest.raises(KeyError):
        _duplicate(application, missing_id)

    with pytest.raises(KeyError):
        project.get_resource_position(missing_id)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def test_duplicate_command_uses_existing_atlas_command():
    command = AtlasCommand(
        name="duplicate_resource",
        payload={
            "resource_id": AtlasID.generate(),
        },
    )

    assert command.name == "duplicate_resource"


def test_duplicate_does_not_require_new_command_type():
    command = AtlasCommand(
        name="duplicate_resource",
        payload={
            "resource_id": AtlasID.generate(),
        },
    )

    assert isinstance(command, AtlasCommand)
"""
ENG-057 — Atlas Resource Duplicate

RED phase tests.

These tests define the canonical Resource Duplicate contract before
production implementation exists.

ENG-057 establishes that duplicating a Resource:
    - creates a new canonical AtlasResource
    - generates a new AtlasID
    - preserves Resource state where specified
    - creates independent mutable Resource state
    - copies Position / Rotation / Scale into the new AtlasID's spatial state
    - does not clone relationships
    - preserves the source and unrelated Resources
    - is intentionally non-idempotent
    - remains independent of Scene, Selection, Gizmo, and Renderer state
    - fails atomically for invalid source identity
"""

from __future__ import annotations

from copy import deepcopy

import pytest

from atlas.application import AtlasApplication, AtlasCommand
from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.core.spatial import (
    AtlasSpatialPosition,
    AtlasSpatialRotation,
    AtlasSpatialScale,
)
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.properties.property import AtlasProperty
from atlas.project.project import AtlasProject
from atlas.relationships.relationship import AtlasRelationship
from atlas.semantic_tags.tag import AtlasSemanticTag


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_project() -> AtlasProject:
    """Create a minimal Project suitable for ENG-057 tests."""
    return AtlasProject(
        name="ENG-057 Duplicate Test Project"
    )


def _make_classification(
    project: AtlasProject,
    *,
    classification_id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    """Create and register a canonical Classification."""
    classification = AtlasClassification(
        id=classification_id,
        name=name,
    )
    project.add_classification(
        classification
    )
    return classification


def _make_resource(
    project: AtlasProject,
    *,
    classification: AtlasClassification,
    name: str = "Wall",
) -> AtlasResource:
    """Create and register a Resource through AtlasProject."""
    resource = AtlasResource(
        classification=classification,
        name=name,
    )
    project.add_resource(
        resource
    )
    return resource


def _duplicate(
    application: AtlasApplication,
    resource_id: AtlasID,
) -> AtlasResource:
    """Execute the canonical ENG-057 duplicate command."""
    return application.execute(
        AtlasCommand(
            name="duplicate_resource",
            payload={
                "resource_id": resource_id,
            },
        )
    )


def _set_spatial_state(
    project: AtlasProject,
    resource: AtlasResource,
) -> None:
    """Set a non-default spatial state on a Resource."""
    project.spatial_states.set_position(
        resource.aid,
        AtlasSpatialPosition(
            x=10.0,
            y=20.0,
            z=30.0,
        ),
    )

    project.spatial_states.set_rotation(
        resource.aid,
        AtlasSpatialRotation(
            x=15.0,
            y=25.0,
            z=35.0,
        ),
    )

    project.spatial_states.set_scale(
        resource.aid,
        AtlasSpatialScale(
            x=2.0,
            y=3.0,
            z=4.0,
        ),
    )


# ---------------------------------------------------------------------------
# Command / Application Boundary
# ---------------------------------------------------------------------------


class TestResourceDuplicateCommand:

    def test_duplicate_command_can_be_constructed(self) -> None:
        command = AtlasCommand(
            name="duplicate_resource",
            payload={
                "resource_id": AtlasID.generate(),
            },
        )

        assert command.name == "duplicate_resource"
        assert isinstance(command, AtlasCommand)

    def test_duplicate_returns_atlas_resource(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert isinstance(
            duplicate,
            AtlasResource,
        )


# ---------------------------------------------------------------------------
# Source Resolution / Validation
# ---------------------------------------------------------------------------


class TestResourceDuplicateSourceResolution:

    def test_duplicate_requires_existing_source_resource(self) -> None:
        project = _make_project()
        application = AtlasApplication(project)

        missing_id = AtlasID.generate()

        with pytest.raises(KeyError):
            _duplicate(
                application,
                missing_id,
            )

    def test_duplicate_source_id_must_be_atlas_id(self) -> None:
        project = _make_project()
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

    def test_invalid_source_does_not_mutate_resource_registry(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)
        missing_id = AtlasID.generate()

        before = list(project.resources)

        with pytest.raises(KeyError):
            _duplicate(
                application,
                missing_id,
            )

        assert list(project.resources) == before
        assert project.resource_count == 1
        assert project.get_resource(resource.aid) is resource

    def test_invalid_source_does_not_mutate_spatial_registry(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)
        missing_id = AtlasID.generate()

        before_count = project.spatial_states.count

        with pytest.raises(KeyError):
            _duplicate(
                application,
                missing_id,
            )

        assert project.spatial_states.count == before_count
        assert project.spatial_states.get_position(
            missing_id
        ) is None
        assert project.spatial_states.get_rotation(
            missing_id
        ) is None
        assert project.spatial_states.get_scale(
            missing_id
        ) is None
        assert project.get_resource(resource.aid) is resource

    def test_duplicate_does_not_accept_caller_supplied_duplicate_id(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        before_count = project.resource_count
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

        assert project.resource_count == before_count
        assert project.get_resource(
            caller_supplied_id
        ) is None


# ---------------------------------------------------------------------------
# Identity / Canonical Ownership
# ---------------------------------------------------------------------------


class TestResourceDuplicateIdentity:

    def test_duplicate_receives_new_atlas_id(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.aid != resource.aid
        assert isinstance(duplicate.aid, AtlasID)

    def test_duplicate_is_distinct_resource_object(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate is not resource

    def test_source_identity_is_unchanged(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        original_id = resource.aid
        application = AtlasApplication(project)

        _duplicate(
            application,
            resource.aid,
        )

        assert resource.aid == original_id

    def test_duplicate_is_registered_in_same_project(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert project.get_resource(
            duplicate.aid
        ) is duplicate

    def test_source_remains_registered(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        _duplicate(
            application,
            resource.aid,
        )

        assert project.get_resource(
            resource.aid
        ) is resource

    def test_duplicate_result_is_canonical_registered_instance(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert project.resources.get(
            duplicate.aid
        ) is duplicate


# ---------------------------------------------------------------------------
# Resource State Copy
# ---------------------------------------------------------------------------


class TestResourceDuplicateState:

    def test_duplicate_preserves_classification(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.classification is classification
        assert duplicate.classification is resource.classification

    def test_classification_definition_is_not_duplicated(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.classification.id == classification.id
        assert project.get_classification(
            classification.id
        ) is classification
        assert duplicate.classification is classification

    def test_duplicate_preserves_name(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
            name="North Wall",
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.name == "North Wall"
        assert duplicate.name == resource.name

    def test_duplicate_does_not_invent_name_suffix(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
            name="North Wall",
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.name == "North Wall"

    def test_duplicate_copies_properties(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        material = AtlasProperty(
            id="material",
            name="Material",
            value="concrete",
            data_type="string",
        )
        thickness = AtlasProperty(
            id="thickness",
            name="Thickness",
            value=150,
            data_type="integer",
            unit="mm",
        )

        resource.set_property(material)
        resource.set_property(thickness)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.properties == resource.properties
        assert duplicate.properties is not resource.properties
        assert duplicate.get_property("material") is not material
        assert duplicate.get_property("thickness") is not thickness

    def test_duplicate_property_values_are_independent(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        property_value = {
            "width": 200,
            "height": 300,
        }

        resource.set_property(
            AtlasProperty(
                id="dimensions",
                name="Dimensions",
                value=property_value,
                data_type="object",
            )
        )

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        duplicate_property = duplicate.get_property(
            "dimensions"
        )
        source_property = resource.get_property(
            "dimensions"
        )

        assert duplicate_property is not None
        assert source_property is not None
        assert duplicate_property is not source_property
        assert duplicate_property.value is not source_property.value

        duplicate_property.value["width"] = 500

        assert source_property.value["width"] == 200
        assert duplicate_property.value["width"] == 500

    def test_duplicate_copies_metadata(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        resource.metadata["source"] = "architect"
        resource.metadata["nested"] = {
            "discipline": "architecture",
        }

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.metadata == resource.metadata
        assert duplicate.metadata is not resource.metadata
        assert duplicate.metadata["nested"] is not resource.metadata[
            "nested"
        ]

    def test_duplicate_metadata_is_independent(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        resource.metadata["nested"] = {
            "source": "architect",
        }

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        duplicate.metadata["nested"]["source"] = "engineer"

        assert resource.metadata["nested"]["source"] == "architect"
        assert duplicate.metadata["nested"]["source"] == "engineer"

    def test_duplicate_copies_semantic_tag_membership(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        tag = AtlasSemanticTag(
            id="discipline-architecture",
            name="Architecture",
        )
        resource.add_tag(tag)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.tags == resource.tags
        assert duplicate.tags is not resource.tags
        assert duplicate.get_tag(tag.id) is tag

    def test_duplicate_tag_membership_is_independent(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        tag = AtlasSemanticTag(
            id="discipline-architecture",
            name="Architecture",
        )
        resource.add_tag(tag)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        duplicate.remove_tag(tag.id)

        assert resource.has_tag(tag.id)
        assert not duplicate.has_tag(tag.id)

    def test_duplicate_copies_category_membership(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        category = AtlasCategory(
            id="building",
            name="Building",
        )
        resource.add_category(category)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.categories == resource.categories
        assert duplicate.categories is not resource.categories
        assert duplicate.get_category(category.id) is category

    def test_duplicate_category_membership_is_independent(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )

        category = AtlasCategory(
            id="building",
            name="Building",
        )
        resource.add_category(category)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        duplicate.remove_category(category.id)

        assert resource.has_category(category.id)
        assert not duplicate.has_category(category.id)

    def test_duplicate_enters_new_resource_lifecycle(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        resource.activate()
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert resource.lifecycle is AtlasLifecycle.ACTIVE
        assert duplicate.lifecycle is AtlasLifecycle.CREATED

    def test_duplicate_does_not_modify_source_lifecycle(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        resource.activate()
        original_lifecycle = resource.lifecycle
        application = AtlasApplication(project)

        _duplicate(
            application,
            resource.aid,
        )

        assert resource.lifecycle is original_lifecycle


# ---------------------------------------------------------------------------
# Spatial State
# ---------------------------------------------------------------------------


class TestResourceDuplicateSpatialState:

    def test_duplicate_copies_position(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert project.spatial_states.require_position(
            duplicate.aid
        ) == project.spatial_states.require_position(
            resource.aid
        )

    def test_duplicate_copies_rotation(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert project.spatial_states.require_rotation(
            duplicate.aid
        ) == project.spatial_states.require_rotation(
            resource.aid
        )

    def test_duplicate_copies_scale(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert project.spatial_states.require_scale(
            duplicate.aid
        ) == project.spatial_states.require_scale(
            resource.aid
        )

    def test_duplicate_spatial_state_is_keyed_by_new_atlas_id(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.aid != resource.aid
        assert project.spatial_states.get_position(
            resource.aid
        ) is not None
        assert project.spatial_states.get_position(
            duplicate.aid
        ) is not None

    def test_moving_duplicate_does_not_move_source(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        project.spatial_states.set_position(
            duplicate.aid,
            AtlasSpatialPosition(
                x=100.0,
                y=200.0,
                z=300.0,
            ),
        )

        assert project.spatial_states.require_position(
            resource.aid
        ) == AtlasSpatialPosition(
            x=10.0,
            y=20.0,
            z=30.0,
        )

    def test_rotating_duplicate_does_not_rotate_source(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        project.spatial_states.set_rotation(
            duplicate.aid,
            AtlasSpatialRotation(
                x=90.0,
                y=45.0,
                z=10.0,
            ),
        )

        assert project.spatial_states.require_rotation(
            resource.aid
        ) == AtlasSpatialRotation(
            x=15.0,
            y=25.0,
            z=35.0,
        )

    def test_scaling_duplicate_does_not_scale_source(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        _set_spatial_state(project, resource)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        project.spatial_states.set_scale(
            duplicate.aid,
            AtlasSpatialScale(
                x=5.0,
                y=6.0,
                z=7.0,
            ),
        )

        assert project.spatial_states.require_scale(
            resource.aid
        ) == AtlasSpatialScale(
            x=2.0,
            y=3.0,
            z=4.0,
        )


# ---------------------------------------------------------------------------
# Relationship Semantics
# ---------------------------------------------------------------------------


class TestResourceDuplicateRelationships:

    def test_duplicate_does_not_clone_relationships(self) -> None:
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

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="depends_on",
            source=source,
            target=target,
        )
        project.add_relationship(relationship)

        before = project.relationships_for_resource(source)
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            source.aid,
        )

        after = project.relationships_for_resource(source)

        assert after == before
        assert project.relationships_for_resource(duplicate) == []

    def test_source_relationships_remain_unchanged(self) -> None:
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

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="depends_on",
            source=source,
            target=target,
        )
        project.add_relationship(relationship)

        before = project.relationships_for_resource(source)
        application = AtlasApplication(project)

        _duplicate(
            application,
            source.aid,
        )

        assert project.relationships_for_resource(source) == before

    def test_duplicate_does_not_create_reverse_relationship(self) -> None:
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

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="depends_on",
            source=source,
            target=target,
        )
        project.add_relationship(relationship)

        application = AtlasApplication(project)
        duplicate = _duplicate(
            application,
            source.aid,
        )

        assert project.relationships_for_resource(duplicate) == []


# ---------------------------------------------------------------------------
# Source / Unrelated Resource Preservation
# ---------------------------------------------------------------------------


class TestResourceDuplicateIsolation:

    def test_duplicate_does_not_modify_source(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
            name="Original",
        )
        _set_spatial_state(project, source)

        source.set_property(
            AtlasProperty(
                id="material",
                name="Material",
                value="concrete",
                data_type="string",
            )
        )
        source.metadata["source"] = "architect"

        tag = AtlasSemanticTag(
            id="architecture",
            name="Architecture",
        )
        category = AtlasCategory(
            id="building",
            name="Building",
        )
        source.add_tag(tag)
        source.add_category(category)
        source.activate()

        before = {
            "aid": source.aid,
            "classification": source.classification,
            "name": source.name,
            "properties": deepcopy(source.properties),
            "metadata": deepcopy(source.metadata),
            "tags": list(source.tags),
            "categories": list(source.categories),
            "lifecycle": source.lifecycle,
            "position": project.spatial_states.require_position(
                source.aid
            ),
            "rotation": project.spatial_states.require_rotation(
                source.aid
            ),
            "scale": project.spatial_states.require_scale(
                source.aid
            ),
        }

        application = AtlasApplication(project)
        _duplicate(
            application,
            source.aid,
        )

        assert source.aid == before["aid"]
        assert source.classification is before["classification"]
        assert source.name == before["name"]
        assert source.properties == before["properties"]
        assert source.metadata == before["metadata"]
        assert source.tags == before["tags"]
        assert source.categories == before["categories"]
        assert source.lifecycle is before["lifecycle"]
        assert project.spatial_states.require_position(
            source.aid
        ) == before["position"]
        assert project.spatial_states.require_rotation(
            source.aid
        ) == before["rotation"]
        assert project.spatial_states.require_scale(
            source.aid
        ) == before["scale"]

    def test_duplicate_does_not_modify_unrelated_resource(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
            name="Source",
        )
        unrelated = _make_resource(
            project,
            classification=classification,
            name="Unrelated",
        )
        project.spatial_states.set_position(
            unrelated.aid,
            AtlasSpatialPosition(
                x=7.0,
                y=8.0,
                z=9.0,
            ),
        )

        before_count = project.resource_count
        before_name = unrelated.name
        before_position = project.spatial_states.require_position(
            unrelated.aid
        )

        application = AtlasApplication(project)
        duplicate = _duplicate(
            application,
            source.aid,
        )

        assert project.resource_count == before_count + 1
        assert duplicate.aid != unrelated.aid
        assert project.get_resource(unrelated.aid) is unrelated
        assert unrelated.name == before_name
        assert project.spatial_states.require_position(
            unrelated.aid
        ) == before_position


# ---------------------------------------------------------------------------
# Repeated Duplication / Non-Idempotency
# ---------------------------------------------------------------------------


class TestResourceDuplicateRepeated:

    def test_duplicate_is_not_idempotent(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        first = _duplicate(
            application,
            source.aid,
        )
        second = _duplicate(
            application,
            source.aid,
        )

        assert first.aid != second.aid
        assert first is not second
        assert project.resource_count == 3

    def test_duplicate_can_duplicate_duplicate(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
            name="Original",
        )
        application = AtlasApplication(project)

        first = _duplicate(
            application,
            source.aid,
        )
        second = _duplicate(
            application,
            first.aid,
        )

        assert first.aid != source.aid
        assert second.aid != first.aid
        assert second.aid != source.aid
        assert second.name == first.name


# ---------------------------------------------------------------------------
# Delete Compatibility
# ---------------------------------------------------------------------------


class TestResourceDuplicateDeleteCompatibility:

    def test_deleting_source_does_not_delete_duplicate(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            source.aid,
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": source.aid,
                },
            )
        )

        assert project.get_resource(
            source.aid
        ) is None
        assert project.get_resource(
            duplicate.aid
        ) is duplicate

    def test_deleting_duplicate_does_not_delete_source(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            source.aid,
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": duplicate.aid,
                },
            )
        )

        assert project.get_resource(
            duplicate.aid
        ) is None
        assert project.get_resource(
            source.aid
        ) is source


# ---------------------------------------------------------------------------
# Boundary Isolation
# ---------------------------------------------------------------------------


class TestResourceDuplicateBoundaryIsolation:

    def test_duplicate_does_not_require_scene(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate is not None

    def test_duplicate_does_not_require_scene_node(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert not hasattr(
            duplicate,
            "scene_node",
        )

    def test_duplicate_does_not_require_selection(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.aid != resource.aid

    def test_duplicate_does_not_require_gizmo(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.aid != resource.aid


# ---------------------------------------------------------------------------
# Equivalent State / Determinism
# ---------------------------------------------------------------------------


class TestResourceDuplicateDeterminism:

    def test_duplicate_preserves_equivalent_resource_state(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        resource = _make_resource(
            project,
            classification=classification,
            name="Wall",
        )

        resource.set_property(
            AtlasProperty(
                id="material",
                name="Material",
                value="concrete",
                data_type="string",
            )
        )
        resource.metadata["source"] = "architect"
        resource.add_tag(
            AtlasSemanticTag(
                id="architecture",
                name="Architecture",
            )
        )
        resource.add_category(
            AtlasCategory(
                id="building",
                name="Building",
            )
        )
        _set_spatial_state(project, resource)

        application = AtlasApplication(project)

        duplicate = _duplicate(
            application,
            resource.aid,
        )

        assert duplicate.aid != resource.aid
        assert duplicate.classification is resource.classification
        assert duplicate.name == resource.name
        assert duplicate.properties == resource.properties
        assert duplicate.metadata == resource.metadata
        assert duplicate.tags == resource.tags
        assert duplicate.categories == resource.categories
        assert duplicate.lifecycle is AtlasLifecycle.CREATED

        assert project.spatial_states.require_position(
            duplicate.aid
        ) == project.spatial_states.require_position(
            resource.aid
        )
        assert project.spatial_states.require_rotation(
            duplicate.aid
        ) == project.spatial_states.require_rotation(
            resource.aid
        )
        assert project.spatial_states.require_scale(
            duplicate.aid
        ) == project.spatial_states.require_scale(
            resource.aid
        )


# ---------------------------------------------------------------------------
# Final source preservation / graph count
# ---------------------------------------------------------------------------


class TestResourceDuplicateProjectIntegrity:

    def test_duplicate_increases_resource_count_by_one(self) -> None:
        project = _make_project()
        classification = _make_classification(project)
        source = _make_resource(
            project,
            classification=classification,
        )
        application = AtlasApplication(project)

        before = project.resource_count

        duplicate = _duplicate(
            application,
            source.aid,
        )

        assert project.resource_count == before + 1
        assert project.get_resource(
            duplicate.aid
        ) is duplicate

    def test_duplicate_does_not_change_relationship_count(self) -> None:
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

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="depends_on",
            source=source,
            target=target,
        )
        project.add_relationship(relationship)

        application = AtlasApplication(project)
        before = project.relationship_count

        _duplicate(
            application,
            source.aid,
        )

        assert project.relationship_count == before
        assert project.relationships_for_resource(source) == [
            relationship
        ]

    def test_duplicate_preserves_source_relationship_identity(self) -> None:
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

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="depends_on",
            source=source,
            target=target,
        )
        project.add_relationship(relationship)

        application = AtlasApplication(project)
        _duplicate(
            application,
            source.aid,
        )

        remaining = project.relationships_for_resource(source)

        assert len(remaining) == 1
        assert remaining[0] is relationship
        assert remaining[0].source is source
        assert remaining[0].target is target
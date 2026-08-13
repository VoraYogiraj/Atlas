"""
ENG-036 — Atlas JSON Serialization

RED test suite.

These tests define the canonical JSON serialization contract for:

- AtlasID
- AtlasClassification
- AtlasProperty
- AtlasSemanticTag
- AtlasCategory
- AtlasResource
- AtlasRelationship
- AtlasProject

Serialization must:

- preserve engineering meaning
- preserve identity
- preserve classification hierarchy
- preserve properties
- preserve relationships
- preserve semantics
- preserve lifecycle
- preserve metadata
- be deterministic
- be versioned
- not mutate source objects
- avoid recursively serializing relationship endpoints
"""

from __future__ import annotations

import json

import pytest

from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.project.project import AtlasProject
from atlas.properties.property import AtlasProperty
from atlas.relationships.relationship import AtlasRelationship
from atlas.semantic_tags.tag import AtlasSemanticTag

from atlas.serialization.json_serializer import (
    AtlasJSONSerializer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_classifications() -> tuple[
    AtlasClassification,
    AtlasClassification,
    AtlasClassification,
]:
    physical = AtlasClassification(
        id="physical-resource",
        name="Physical Resource",
        description="A physical engineering entity.",
    )

    building_element = AtlasClassification(
        id="building-element",
        name="Building Element",
        description="A component of a building.",
        parent=physical,
    )

    wall = AtlasClassification(
        id="wall",
        name="Wall",
        description="A wall element.",
        parent=building_element,
    )

    return (
        physical,
        building_element,
        wall,
    )


def create_resource(
    classification: AtlasClassification,
    *,
    name: str = "External Wall",
) -> AtlasResource:
    resource = AtlasResource(
        classification=classification,
        name=name,
    )

    resource.set_property(
        AtlasProperty(
            id="thickness",
            name="Thickness",
            value=150,
            data_type="number",
            unit="mm",
            description="Wall thickness.",
            required=True,
        )
    )

    resource.set_property(
        AtlasProperty(
            id="height",
            name="Height",
            value=3.0,
            data_type="number",
            unit="m",
            description="Wall height.",
            required=True,
        )
    )

    resource.metadata.update(
        {
            "discipline": "architecture",
            "source": "engineer",
        }
    )

    resource.add_tag(
        AtlasSemanticTag(
            id="load-bearing",
            name="Load Bearing",
            description="Structural load-bearing element.",
        )
    )

    resource.add_tag(
        AtlasSemanticTag(
            id="external",
            name="External",
            description="External building element.",
        )
    )

    resource.add_category(
        AtlasCategory(
            id="structural",
            name="Structural",
            description="Structural building elements.",
        )
    )

    resource.add_category(
        AtlasCategory(
            id="building-envelope",
            name="Building Envelope",
            description="Envelope elements.",
        )
    )

    resource.activate()

    return resource


def create_project() -> tuple[
    AtlasProject,
    AtlasResource,
    AtlasResource,
    AtlasRelationship,
]:
    physical, building_element, wall = (
        create_classifications()
    )

    project = AtlasProject(
        name="Atlas Test Building",
        metadata={
            "location": "Surat",
            "country": "India",
        },
    )

    project.add_classification(
        physical
    )
    project.add_classification(
        building_element
    )
    project.add_classification(
        wall
    )

    wall_a = create_resource(
        wall,
        name="External Wall A",
    )

    wall_b = create_resource(
        wall,
        name="External Wall B",
    )

    project.add_resource(
        wall_a
    )
    project.add_resource(
        wall_b
    )

    relationship = AtlasRelationship(
        id="rel-wall-001",
        relationship_type="adjacent_to",
        source=wall_a,
        target=wall_b,
        description="Walls share a common boundary.",
    )

    project.add_relationship(
        relationship
    )

    return (
        project,
        wall_a,
        wall_b,
        relationship,
    )


# ---------------------------------------------------------------------------
# Serializer API
# ---------------------------------------------------------------------------


def test_serializer_can_be_created():
    serializer = AtlasJSONSerializer()

    assert serializer is not None


def test_serializer_exposes_serialization_version():
    serializer = AtlasJSONSerializer()

    assert isinstance(
        serializer.serialization_version,
        str,
    )

    assert serializer.serialization_version


# ---------------------------------------------------------------------------
# AtlasID
# ---------------------------------------------------------------------------


def test_resource_identity_is_serialized_as_string():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    assert isinstance(
        data["id"],
        str,
    )

    assert data["id"] == str(
        wall.aid
    )


def test_resource_identity_round_trip_preserves_atlas_id():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert restored.aid == wall.aid


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def test_classification_registry_is_serialized():
    project, _, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    classifications = (
        data["project"]["classifications"]
    )

    assert len(classifications) == 3


def test_classification_hierarchy_is_serialized_by_parent_id():
    project, _, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    classifications = {
        item["id"]: item
        for item in data["project"][
            "classifications"
        ]
    }

    assert classifications[
        "physical-resource"
    ]["parent"] is None

    assert classifications[
        "building-element"
    ]["parent"] == "physical-resource"

    assert classifications[
        "wall"
    ]["parent"] == "building-element"


def test_resource_references_classification_by_id():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    assert data["classification"] == (
        wall.classification.id
    )


def test_classification_hierarchy_round_trip_is_preserved():
    project, _, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    wall = (
        restored.get_classification(
            "wall"
        )
    )

    assert wall is not None
    assert wall.parent is not None
    assert wall.parent.id == (
        "building-element"
    )

    assert wall.parent.parent is not None
    assert wall.parent.parent.id == (
        "physical-resource"
    )

    assert wall.path == (
        "Physical Resource",
        "Building Element",
        "Wall",
    )

    assert wall.depth == 2


# ---------------------------------------------------------------------------
# Resource Name
# ---------------------------------------------------------------------------


def test_resource_name_is_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    assert data["name"] == (
        "External Wall A"
    )


def test_resource_name_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert restored.name == wall.name


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_resource_properties_are_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    properties = data["properties"]

    assert "thickness" in properties
    assert "height" in properties


def test_property_fields_are_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    thickness = data["properties"][
        "thickness"
    ]

    assert thickness == {
        "id": "thickness",
        "name": "Thickness",
        "value": 150,
        "data_type": "number",
        "unit": "mm",
        "description": "Wall thickness.",
        "required": True,
    }


def test_properties_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    original = wall.get_property(
        "thickness"
    )

    restored_property = (
        restored.get_property(
            "thickness"
        )
    )

    assert restored_property is not None
    assert original is not None

    assert restored_property.id == (
        original.id
    )
    assert restored_property.name == (
        original.name
    )
    assert restored_property.value == (
        original.value
    )
    assert restored_property.data_type == (
        original.data_type
    )
    assert restored_property.unit == (
        original.unit
    )
    assert restored_property.description == (
        original.description
    )
    assert restored_property.required == (
        original.required
    )


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def test_resource_metadata_is_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    assert data["metadata"] == {
        "discipline": "architecture",
        "source": "engineer",
    }


def test_resource_metadata_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert restored.metadata == (
        wall.metadata
    )


# ---------------------------------------------------------------------------
# Semantic Tags
# ---------------------------------------------------------------------------


def test_resource_tags_are_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    tag_ids = {
        tag["id"]
        for tag in data["tags"]
    }

    assert tag_ids == {
        "load-bearing",
        "external",
    }


def test_tag_fields_are_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    tag = next(
        item
        for item in data["tags"]
        if item["id"] == "load-bearing"
    )

    assert tag == {
        "id": "load-bearing",
        "name": "Load Bearing",
        "description": (
            "Structural load-bearing element."
        ),
    }


def test_tags_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert [
        tag.id
        for tag in restored.tags
    ] == [
        tag.id
        for tag in wall.tags
    ]


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


def test_resource_categories_are_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    category_ids = {
        category["id"]
        for category in data["categories"]
    }

    assert category_ids == {
        "structural",
        "building-envelope",
    }


def test_category_fields_are_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    category = next(
        item
        for item in data["categories"]
        if item["id"] == "structural"
    )

    assert category == {
        "id": "structural",
        "name": "Structural",
        "description": (
            "Structural building elements."
        ),
    }


def test_categories_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert [
        category.id
        for category in restored.categories
    ] == [
        category.id
        for category in wall.categories
    ]


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def test_resource_lifecycle_is_serialized():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    assert data["lifecycle"] == "active"


def test_resource_lifecycle_round_trip_is_preserved():
    _, wall, _, _ = create_project()

    serializer = AtlasJSONSerializer()

    data = serializer.resource_to_dict(
        wall
    )

    restored = (
        serializer.resource_from_dict(
            data
        )
    )

    assert restored.lifecycle is (
        AtlasLifecycle.ACTIVE
    )


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------


def test_project_relationships_are_serialized():
    project, _, _, relationship = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    relationships = data[
        "project"
    ]["relationships"]

    assert len(relationships) == 1

    assert relationships[0] == {
        "id": relationship.id,
        "relationship_type": (
            relationship.relationship_type
        ),
        "source": str(
            relationship.source.aid
        ),
        "target": str(
            relationship.target.aid
        ),
        "description": (
            relationship.description
        ),
    }


def test_relationships_are_not_recursively_serialized():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    relationship = data[
        "project"
    ]["relationships"][0]

    assert isinstance(
        relationship["source"],
        str,
    )

    assert isinstance(
        relationship["target"],
        str,
    )


def test_relationship_round_trip_preserves_endpoints():
    project, wall_a, wall_b, relationship = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    restored_relationships = list(
        restored.graph
    )

    assert len(
        restored_relationships
    ) == 1

    restored_relationship = (
        restored_relationships[0]
    )

    assert restored_relationship.id == (
        relationship.id
    )

    assert (
        restored_relationship.relationship_type
        == relationship.relationship_type
    )

    assert (
        restored_relationship.source.aid
        == wall_a.aid
    )

    assert (
        restored_relationship.target.aid
        == wall_b.aid
    )


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


def test_project_identity_is_serialized():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    assert data["project"]["id"] == (
        str(project.aid)
    )


def test_project_name_is_serialized():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    assert data["project"]["name"] == (
        "Atlas Test Building"
    )


def test_project_metadata_is_serialized():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    assert data["project"][
        "metadata"
    ] == {
        "location": "Surat",
        "country": "India",
    }


def test_project_resource_collection_is_serialized():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    resources = data[
        "project"
    ]["resources"]

    assert len(resources) == (
        project.resource_count
    )


def test_project_round_trip_preserves_resource_count():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    assert restored.resource_count == (
        project.resource_count
    )


def test_project_round_trip_preserves_relationship_count():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    assert (
        restored.relationship_count
        == project.relationship_count
    )


def test_project_round_trip_preserves_identity():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    assert restored.aid == (
        project.aid
    )


def test_project_round_trip_preserves_name():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    restored = (
        serializer.project_from_dict(
            data
        )
    )

    assert restored.name == (
        project.name
    )


# ---------------------------------------------------------------------------
# Version Envelope
# ---------------------------------------------------------------------------


def test_project_json_has_atlas_envelope():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    assert "atlas" in data

    assert (
        "serialization_version"
        in data["atlas"]
    )

    assert (
        "atlas_version"
        in data["atlas"]
    )


def test_serialization_version_matches_serializer():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    assert data["atlas"][
        "serialization_version"
    ] == serializer.serialization_version


# ---------------------------------------------------------------------------
# JSON Text
# ---------------------------------------------------------------------------


def test_project_can_be_serialized_to_json_text():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    text = serializer.dumps(
        project
    )

    assert isinstance(
        text,
        str,
    )

    parsed = json.loads(
        text
    )

    assert isinstance(
        parsed,
        dict,
    )


def test_json_text_is_valid_json():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    text = serializer.dumps(
        project
    )

    parsed = json.loads(
        text
    )

    assert parsed["project"][
        "name"
    ] == "Atlas Test Building"


def test_json_round_trip_is_supported():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    text = serializer.dumps(
        project
    )

    restored = serializer.loads(
        text
    )

    assert restored.aid == (
        project.aid
    )

    assert restored.name == (
        project.name
    )

    assert restored.resource_count == (
        project.resource_count
    )

    assert (
        restored.relationship_count
        == project.relationship_count
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_project_serialization_is_deterministic():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    first = serializer.dumps(
        project
    )

    second = serializer.dumps(
        project
    )

    assert first == second


# ---------------------------------------------------------------------------
# Source Immutability
# ---------------------------------------------------------------------------


def test_serialization_does_not_modify_project():
    project, _, _, _ = (
        create_project()
    )

    original_name = project.name
    original_metadata = dict(
        project.metadata
    )
    original_resource_count = (
        project.resource_count
    )
    original_relationship_count = (
        project.relationship_count
    )

    serializer = AtlasJSONSerializer()

    serializer.dumps(
        project
    )

    assert project.name == (
        original_name
    )

    assert project.metadata == (
        original_metadata
    )

    assert project.resource_count == (
        original_resource_count
    )

    assert project.relationship_count == (
        original_relationship_count
    )


def test_resource_serialization_does_not_modify_resource():
    _, wall, _, _ = create_project()

    original_name = wall.name
    original_metadata = dict(
        wall.metadata
    )
    original_property_ids = set(
        wall.properties
    )
    original_tag_ids = {
        tag.id
        for tag in wall.tags
    }
    original_category_ids = {
        category.id
        for category in wall.categories
    }

    serializer = AtlasJSONSerializer()

    serializer.resource_to_dict(
        wall
    )

    assert wall.name == (
        original_name
    )

    assert wall.metadata == (
        original_metadata
    )

    assert set(
        wall.properties
    ) == original_property_ids

    assert {
        tag.id
        for tag in wall.tags
    } == original_tag_ids

    assert {
        category.id
        for category in wall.categories
    } == original_category_ids


# ---------------------------------------------------------------------------
# Invalid Input
# ---------------------------------------------------------------------------


def test_serializer_rejects_non_project():
    serializer = AtlasJSONSerializer()

    with pytest.raises(
        TypeError
    ):
        serializer.project_to_dict(
            object()
        )


def test_serializer_rejects_non_resource():
    serializer = AtlasJSONSerializer()

    with pytest.raises(
        TypeError
    ):
        serializer.resource_to_dict(
            object()
        )


def test_serializer_rejects_invalid_json_text():
    serializer = AtlasJSONSerializer()

    with pytest.raises(
        ValueError
    ):
        serializer.loads(
            "{invalid-json"
        )


def test_serializer_rejects_missing_project_section():
    serializer = AtlasJSONSerializer()

    with pytest.raises(
        ValueError
    ):
        serializer.project_from_dict(
            {
                "atlas": {
                    "serialization_version": "0.1.0",
                    "atlas_version": "0.1.0",
                }
            }
        )


def test_serializer_rejects_unknown_relationship_endpoint():
    project, _, _, _ = (
        create_project()
    )

    serializer = AtlasJSONSerializer()

    data = serializer.project_to_dict(
        project
    )

    data[
        "project"
    ]["relationships"][0]["target"] = (
        str(AtlasID.generate())
    )

    with pytest.raises(
        ValueError
    ):
        serializer.project_from_dict(
            data
        )
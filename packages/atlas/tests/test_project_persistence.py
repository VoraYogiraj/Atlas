"""
ENG-037 — Atlas Project Save / Load

RED test suite.

Defines the filesystem persistence contract around ENG-036.
"""

from __future__ import annotations

import json

import pytest

from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.project.project import AtlasProject
from atlas.properties.property import AtlasProperty
from atlas.relationships.relationship import AtlasRelationship
from atlas.semantic_tags.tag import AtlasSemanticTag
from atlas.persistence.project_persistence import (
    AtlasProjectPersistence,
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

    return physical, building_element, wall


def create_project() -> AtlasProject:
    physical, building_element, wall = (
        create_classifications()
    )

    project = AtlasProject(
        name="Atlas Persistence Test",
        metadata={
            "location": "Surat",
            "country": "India",
        },
    )

    project.add_classification(physical)
    project.add_classification(building_element)
    project.add_classification(wall)

    wall_a = AtlasResource(
        classification=wall,
        name="Wall A",
    )

    wall_a.set_property(
        AtlasProperty(
            id="thickness",
            name="Thickness",
            value=150,
            data_type="number",
            unit="mm",
            required=True,
        )
    )

    wall_a.add_tag(
        AtlasSemanticTag(
            id="external",
            name="External",
            description="External wall.",
        )
    )

    wall_a.add_category(
        AtlasCategory(
            id="building-envelope",
            name="Building Envelope",
        )
    )

    wall_a.metadata.update(
        {
            "discipline": "architecture",
        }
    )

    wall_a.activate()

    wall_b = AtlasResource(
        classification=wall,
        name="Wall B",
    )

    wall_b.activate()

    project.add_resource(wall_a)
    project.add_resource(wall_b)

    project.add_relationship(
        AtlasRelationship(
            id="rel-001",
            relationship_type="adjacent_to",
            source=wall_a,
            target=wall_b,
            description="Shared boundary.",
        )
    )

    return project


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_persistence_can_be_created():
    persistence = AtlasProjectPersistence()

    assert persistence is not None


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


def test_save_creates_project_file(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    result = persistence.save(
        project,
        path,
    )

    assert result == path
    assert path.exists()
    assert path.is_file()


def test_save_writes_utf8_json(tmp_path):
    project = create_project()
    project.name = "Atlas Gebäude 🏗️"

    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    raw = path.read_bytes()
    text = raw.decode("utf-8")

    data = json.loads(text)

    assert data["project"]["name"] == (
        "Atlas Gebäude 🏗️"
    )


def test_save_uses_serializer_contract(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert "atlas" in data
    assert "project" in data
    assert (
        "serialization_version"
        in data["atlas"]
    )


def test_save_does_not_modify_project(tmp_path):
    project = create_project()

    original_id = project.aid
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

    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    assert project.aid == original_id
    assert project.name == original_name
    assert project.metadata == original_metadata
    assert project.resource_count == (
        original_resource_count
    )
    assert project.relationship_count == (
        original_relationship_count
    )


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def test_load_returns_project(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert isinstance(
        loaded,
        AtlasProject,
    )


def test_load_returns_new_project_instance(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert loaded is not project


def test_load_preserves_project_identity(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert loaded.aid == project.aid


def test_load_preserves_project_name(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert loaded.name == project.name


def test_load_preserves_project_metadata(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert loaded.metadata == (
        project.metadata
    )


def test_load_preserves_classifications(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert (
        loaded.classification_registry.count
        == project.classification_registry.count
    )

    wall = loaded.get_classification("wall")

    assert wall is not None
    assert wall.path == (
        "Physical Resource",
        "Building Element",
        "Wall",
    )
    assert wall.depth == 2


def test_load_preserves_resources(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert (
        loaded.resource_count
        == project.resource_count
    )


def test_load_preserves_resource_identity(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    original_ids = {
        str(resource.aid)
        for resource in project.resources
    }

    loaded_ids = {
        str(resource.aid)
        for resource in loaded.resources
    }

    assert loaded_ids == original_ids


def test_load_preserves_resource_properties(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    loaded_wall = next(
        resource
        for resource in loaded.resources
        if resource.name == "Wall A"
    )

    property = loaded_wall.get_property(
        "thickness"
    )

    assert property is not None
    assert property.value == 150
    assert property.unit == "mm"


def test_load_preserves_semantics(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    loaded_wall = next(
        resource
        for resource in loaded.resources
        if resource.name == "Wall A"
    )

    assert loaded_wall.has_tag("external")
    assert loaded_wall.has_category(
        "building-envelope"
    )


def test_load_preserves_lifecycle(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    loaded_wall = next(
        resource
        for resource in loaded.resources
        if resource.name == "Wall A"
    )

    assert loaded_wall.lifecycle is (
        AtlasLifecycle.ACTIVE
    )


def test_load_preserves_relationships(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert (
        loaded.relationship_count
        == project.relationship_count
    )


def test_load_preserves_relationship_endpoints(tmp_path):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    relationships = list(
        loaded.graph
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.id == "rel-001"
    assert relationship.source.name == "Wall A"
    assert relationship.target.name == "Wall B"


# ---------------------------------------------------------------------------
# Round Trip
# ---------------------------------------------------------------------------


def test_save_load_round_trip_preserves_full_project(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    persistence.save(
        project,
        path,
    )

    loaded = persistence.load(path)

    assert loaded.aid == project.aid
    assert loaded.name == project.name
    assert loaded.metadata == project.metadata
    assert (
        loaded.resource_count
        == project.resource_count
    )
    assert (
        loaded.relationship_count
        == project.relationship_count
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_saving_same_project_is_deterministic(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    first = tmp_path / "first.atlas.json"
    second = tmp_path / "second.atlas.json"

    persistence.save(
        project,
        first,
    )

    persistence.save(
        project,
        second,
    )

    assert first.read_bytes() == (
        second.read_bytes()
    )


# ---------------------------------------------------------------------------
# Overwrite Policy
# ---------------------------------------------------------------------------


def test_save_does_not_overwrite_existing_file_by_default(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    path.write_text(
        "existing content",
        encoding="utf-8",
    )

    with pytest.raises(
        FileExistsError
    ):
        persistence.save(
            project,
            path,
        )

    assert path.read_text(
        encoding="utf-8"
    ) == "existing content"


def test_save_can_explicitly_overwrite_existing_file(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = tmp_path / "project.atlas.json"

    path.write_text(
        "existing content",
        encoding="utf-8",
    )

    persistence.save(
        project,
        path,
        overwrite=True,
    )

    loaded = persistence.load(path)

    assert loaded.aid == project.aid


# ---------------------------------------------------------------------------
# Missing / Invalid Files
# ---------------------------------------------------------------------------


def test_load_missing_file_raises_file_not_found_error(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    path = tmp_path / "missing.atlas.json"

    with pytest.raises(
        FileNotFoundError
    ):
        persistence.load(path)


def test_load_invalid_json_raises_value_error(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    path = tmp_path / "invalid.atlas.json"

    path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        persistence.load(path)


def test_load_invalid_atlas_payload_raises_value_error(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    path = tmp_path / "invalid.atlas.json"

    path.write_text(
        json.dumps(
            {
                "atlas": {
                    "serialization_version": "0.1.0",
                    "atlas_version": "0.1.0",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        persistence.load(path)


# ---------------------------------------------------------------------------
# Path Handling
# ---------------------------------------------------------------------------


def test_save_requires_file_path(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    with pytest.raises(
        TypeError
    ):
        persistence.save(
            project,
            None,
        )


def test_load_requires_file_path(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    with pytest.raises(
        TypeError
    ):
        persistence.load(None)


def test_save_fails_when_parent_directory_does_not_exist(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    path = (
        tmp_path
        / "does-not-exist"
        / "project.atlas.json"
    )

    with pytest.raises(
        FileNotFoundError
    ):
        persistence.save(
            project,
            path,
        )


def test_save_rejects_directory_as_target(
    tmp_path,
):
    project = create_project()
    persistence = AtlasProjectPersistence()

    directory = tmp_path / "project.atlas.json"
    directory.mkdir()

    with pytest.raises(
        IsADirectoryError
    ):
        persistence.save(
            project,
            directory,
            overwrite=True,
        )


# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------


def test_save_rejects_non_project(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    with pytest.raises(
        TypeError
    ):
        persistence.save(
            object(),
            tmp_path / "project.atlas.json",
        )


def test_load_rejects_directory(
    tmp_path,
):
    persistence = AtlasProjectPersistence()

    directory = tmp_path / "project.atlas.json"
    directory.mkdir()

    with pytest.raises(
        IsADirectoryError
    ):
        persistence.load(directory)


# ---------------------------------------------------------------------------
# Serializer Boundary
# ---------------------------------------------------------------------------


def test_persistence_exposes_serializer(
):
    persistence = AtlasProjectPersistence()

    assert persistence.serializer is not None


def test_persistence_reuses_serializer(
):
    persistence = AtlasProjectPersistence()

    first = persistence.serializer
    second = persistence.serializer

    assert first is second
"""
ENG-056 — Atlas Resource Delete

RED test suite.

These tests define the canonical Resource Delete contract.
Implementation is intentionally expected to be incomplete at
this stage.
"""

from __future__ import annotations

import pytest

from atlas.application import AtlasApplication, AtlasCommand, AtlasQuery
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.relationships.relationship import AtlasRelationship


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_project() -> AtlasProject:
    project = AtlasProject("Delete Test Project")

    classification = AtlasClassification(
        name="Wall",
    )

    project.add_classification(classification)

    return project


def make_resource(
    project: AtlasProject,
    name: str,
) -> AtlasResource:
    classification = project.classifications.get(
        next(iter(project.classifications))
    )

    resource = AtlasResource(
        classification=classification,
        name=name,
    )

    project.add_resource(resource)

    return resource


def make_application(
    project: AtlasProject,
) -> AtlasApplication:
    return AtlasApplication(project)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class TestResourceDeleteCommand:
    def test_delete_command_can_be_constructed(self) -> None:
        resource_id = AtlasID.generate()

        command = AtlasCommand(
            name="delete_resource",
            payload={
                "resource_id": resource_id,
            },
        )

        assert command.name == "delete_resource"

    def test_delete_command_preserves_resource_id(self) -> None:
        resource_id = AtlasID.generate()

        command = AtlasCommand(
            name="delete_resource",
            payload={
                "resource_id": resource_id,
            },
        )

        assert command.payload["resource_id"] == resource_id


# ---------------------------------------------------------------------------
# Resource deletion
# ---------------------------------------------------------------------------


class TestResourceDeleteApplication:
    def test_delete_existing_resource(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        assert project.get_resource(resource.aid) is resource

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        assert project.get_resource(resource.aid) is None

    def test_delete_decreases_resource_count(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        count_before = project.resource_count

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        assert project.resource_count == count_before - 1


# ---------------------------------------------------------------------------
# Relationship cleanup
# ---------------------------------------------------------------------------


class TestResourceDeleteRelationshipCleanup:
    def test_delete_removes_outgoing_relationships(self) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        relationship = AtlasRelationship(
            source=resource_a,
            target=resource_b,
            relationship_type="supports",
        )

        project.add_relationship(relationship)

        assert project.relationship_count == 1

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        assert project.relationship_count == 0

    def test_delete_removes_incoming_relationships(self) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        relationship = AtlasRelationship(
            source=resource_a,
            target=resource_b,
            relationship_type="supports",
        )

        project.add_relationship(relationship)

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_b.aid,
                },
            )
        )

        assert project.relationship_count == 0

    def test_delete_preserves_unrelated_relationships(self) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")
        resource_c = make_resource(project, "Wall C")

        relationship_ab = AtlasRelationship(
            source=resource_a,
            target=resource_b,
            relationship_type="supports",
        )

        relationship_bc = AtlasRelationship(
            source=resource_b,
            target=resource_c,
            relationship_type="adjacent",
        )

        project.add_relationship(relationship_ab)
        project.add_relationship(relationship_bc)

        assert project.relationship_count == 2

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        assert project.relationship_count == 1

        remaining = project.relationships_by_type(
            "adjacent"
        )

        assert relationship_bc in remaining


# ---------------------------------------------------------------------------
# Spatial cleanup
# ---------------------------------------------------------------------------


class TestResourceDeleteSpatialCleanup:
    def test_delete_removes_position(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="move_resource",
                payload={
                    "resource_id": resource.aid,
                    "position": {
                        "x": 10.0,
                        "y": 20.0,
                        "z": 30.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        with pytest.raises(Exception):
            application.execute(
                AtlasQuery(
                    name="get_resource_position",
                    parameters={
                        "resource_id": resource.aid,
                    },
                )
            )

    def test_delete_removes_rotation(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="rotate_resource",
                payload={
                    "resource_id": resource.aid,
                    "rotation": {
                        "x": 10.0,
                        "y": 20.0,
                        "z": 30.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        with pytest.raises(Exception):
            application.execute(
                AtlasQuery(
                    name="get_resource_rotation",
                    parameters={
                        "resource_id": resource.aid,
                    },
                )
            )

    def test_delete_removes_scale(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="scale_resource",
                payload={
                    "resource_id": resource.aid,
                    "scale": {
                        "x": 2.0,
                        "y": 3.0,
                        "z": 4.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        with pytest.raises(Exception):
            application.execute(
                AtlasQuery(
                    name="get_resource_scale",
                    parameters={
                        "resource_id": resource.aid,
                    },
                )
            )


# ---------------------------------------------------------------------------
# Resource isolation
# ---------------------------------------------------------------------------


class TestResourceDeleteIsolation:
    def test_delete_one_resource_does_not_delete_another(self) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        assert project.get_resource(resource_a.aid) is None
        assert project.get_resource(resource_b.aid) is resource_b

    def test_delete_one_resource_does_not_change_another_position(
        self,
    ) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        application.execute(
            AtlasCommand(
                name="move_resource",
                payload={
                    "resource_id": resource_b.aid,
                    "position": {
                        "x": 11.0,
                        "y": 22.0,
                        "z": 33.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        position = application.execute(
            AtlasQuery(
                name="get_resource_position",
                parameters={
                    "resource_id": resource_b.aid,
                },
            )
        )

        assert position == {
            "x": 11.0,
            "y": 22.0,
            "z": 33.0,
        }

    def test_delete_one_resource_does_not_change_another_rotation(
        self,
    ) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        application.execute(
            AtlasCommand(
                name="rotate_resource",
                payload={
                    "resource_id": resource_b.aid,
                    "rotation": {
                        "x": 11.0,
                        "y": 22.0,
                        "z": 33.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        rotation = application.execute(
            AtlasQuery(
                name="get_resource_rotation",
                parameters={
                    "resource_id": resource_b.aid,
                },
            )
        )

        assert rotation == {
            "x": 11.0,
            "y": 22.0,
            "z": 33.0,
        }

    def test_delete_one_resource_does_not_change_another_scale(
        self,
    ) -> None:
        project = make_project()
        application = make_application(project)

        resource_a = make_resource(project, "Wall A")
        resource_b = make_resource(project, "Wall B")

        application.execute(
            AtlasCommand(
                name="scale_resource",
                payload={
                    "resource_id": resource_b.aid,
                    "scale": {
                        "x": 2.0,
                        "y": 3.0,
                        "z": 4.0,
                    },
                },
            )
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        scale = application.execute(
            AtlasQuery(
                name="get_resource_scale",
                parameters={
                    "resource_id": resource_b.aid,
                },
            )
        )

        assert scale == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }


# ---------------------------------------------------------------------------
# Unknown Resource
# ---------------------------------------------------------------------------


class TestResourceDeleteUnknownResource:
    def test_delete_unknown_resource_fails(self) -> None:
        project = make_project()
        application = make_application(project)

        unknown_id = AtlasID.generate()

        with pytest.raises(Exception):
            application.execute(
                AtlasCommand(
                    name="delete_resource",
                    payload={
                        "resource_id": unknown_id,
                    },
                )
            )

    def test_delete_unknown_resource_does_not_mutate_project(
        self,
    ) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        resource_count_before = project.resource_count
        spatial_count_before = project.spatial_states.count

        unknown_id = AtlasID.generate()

        with pytest.raises(Exception):
            application.execute(
                AtlasCommand(
                    name="delete_resource",
                    payload={
                        "resource_id": unknown_id,
                    },
                )
            )

        assert project.resource_count == resource_count_before
        assert project.spatial_states.count == spatial_count_before
        assert project.get_resource(resource.aid) is resource


# ---------------------------------------------------------------------------
# Invalid identity
# ---------------------------------------------------------------------------


class TestResourceDeleteValidation:
    def test_delete_rejects_non_atlas_id(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        resource_count_before = project.resource_count

        with pytest.raises(Exception):
            application.execute(
                AtlasCommand(
                    name="delete_resource",
                    payload={
                        "resource_id": "not-an-atlas-id",
                    },
                )
            )

        assert project.resource_count == resource_count_before
        assert project.get_resource(resource.aid) is resource


# ---------------------------------------------------------------------------
# Repeated deletion
# ---------------------------------------------------------------------------


class TestResourceDeleteRepeated:
    def test_second_delete_fails(self) -> None:
        project = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            "Wall A",
        )

        command = AtlasCommand(
            name="delete_resource",
            payload={
                "resource_id": resource.aid,
            },
        )

        application.execute(command)

        with pytest.raises(Exception):
            application.execute(command)
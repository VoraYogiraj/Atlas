"""
ENG-056 — Resource Delete

Tests for canonical project-level Resource deletion.

Delete must:
    - remove the Resource from the canonical Resource Registry
    - remove all relationships involving the Resource
    - preserve unrelated Resources and Relationships
    - remove Position, Rotation, and Scale spatial state
    - fail for unknown Resources
    - fail on repeated deletion
    - remain isolated from unrelated Resources
"""

from __future__ import annotations

import pytest

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.application.queries import AtlasQuery
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.core.spatial import (
    AtlasSpatialPosition,
    AtlasSpatialRotation,
    AtlasSpatialScale,
)
from atlas.project.project import AtlasProject
from atlas.relationships.relationship import AtlasRelationship


# ----------------------------------------------------------------------
# Fixtures / Helpers
# ----------------------------------------------------------------------


def make_project() -> tuple[AtlasProject, AtlasClassification]:
    project = AtlasProject(
        "Delete Test Project"
    )

    classification = AtlasClassification(
        id=AtlasID.generate(),
        name="Wall",
    )

    project.add_classification(
        classification
    )

    return project, classification


def make_application(
    project: AtlasProject,
) -> AtlasApplication:
    return AtlasApplication(
        project
    )


def make_resource(
    project: AtlasProject,
    classification: AtlasClassification,
    name: str,
) -> AtlasResource:
    resource = AtlasResource(
        classification=classification,
        name=name,
    )

    project.add_resource(
        resource
    )

    return resource


# ----------------------------------------------------------------------
# Resource Delete Command
# ----------------------------------------------------------------------


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
        assert command.payload["resource_id"] == resource_id


# ----------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------


class TestResourceDeleteApplication:

    def test_delete_existing_resource(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            classification,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        assert project.get_resource(
            resource.aid
        ) is None

    def test_delete_decreases_resource_count(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        make_resource(
            project,
            classification,
            "Wall B",
        )

        count_before = project.resource_count

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        assert project.resource_count == count_before - 1


# ----------------------------------------------------------------------
# Relationship Cleanup
# ----------------------------------------------------------------------


class TestResourceDeleteRelationshipCleanup:

    def test_delete_removes_outgoing_relationships(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="supports",
            source=resource_a,
            target=resource_b,
        )

        project.add_relationship(
            relationship
        )

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
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

        relationship = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="supports",
            source=resource_a,
            target=resource_b,
        )

        project.add_relationship(
            relationship
        )

        assert project.relationship_count == 1

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
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

        resource_c = make_resource(
            project,
            classification,
            "Wall C",
        )

        relationship_ab = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="supports",
            source=resource_a,
            target=resource_b,
        )

        relationship_bc = AtlasRelationship(
            id=str(AtlasID.generate()),
            relationship_type="adjacent",
            source=resource_b,
            target=resource_c,
        )

        project.add_relationship(
            relationship_ab
        )

        project.add_relationship(
            relationship_bc
        )

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

        remaining = project.relationships_for_resource(
            resource_b
        )

        assert remaining == [
            relationship_bc
        ]


# ----------------------------------------------------------------------
# Spatial Cleanup
# ----------------------------------------------------------------------


class TestResourceDeleteSpatialCleanup:

    def test_delete_removes_position(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            classification,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="move_resource",
                payload={
                    "resource_id": resource.aid,
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
                    "resource_id": resource.aid,
                },
            )
        )

        assert not project.spatial_states.contains(
            resource.aid
        )

    def test_delete_removes_rotation(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            classification,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="rotate_resource",
                payload={
                    "resource_id": resource.aid,
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
                    "resource_id": resource.aid,
                },
            )
        )

        assert not project.spatial_states.contains(
            resource.aid
        )

    def test_delete_removes_scale(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            classification,
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

        assert not project.spatial_states.contains(
            resource.aid
        )


# ----------------------------------------------------------------------
# Isolation
# ----------------------------------------------------------------------


class TestResourceDeleteIsolation:

    def test_delete_one_resource_does_not_delete_another(
        self,
    ) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource_a.aid,
                },
            )
        )

        assert project.get_resource(
            resource_a.aid
        ) is None

        assert project.get_resource(
            resource_b.aid
        ) is resource_b

    def test_delete_one_resource_does_not_change_another_position(
        self,
    ) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

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

        position = application.query(
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
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

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

        rotation = application.query(
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
        project, classification = make_project()
        application = make_application(project)

        resource_a = make_resource(
            project,
            classification,
            "Wall A",
        )

        resource_b = make_resource(
            project,
            classification,
            "Wall B",
        )

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

        scale = application.query(
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


# ----------------------------------------------------------------------
# Repeated Delete
# ----------------------------------------------------------------------


class TestResourceDeleteRepeated:

    def test_second_delete_fails(self) -> None:
        project, classification = make_project()
        application = make_application(project)

        resource = make_resource(
            project,
            classification,
            "Wall A",
        )

        application.execute(
            AtlasCommand(
                name="delete_resource",
                payload={
                    "resource_id": resource.aid,
                },
            )
        )

        with pytest.raises(
            KeyError
        ):
            application.execute(
                AtlasCommand(
                    name="delete_resource",
                    payload={
                        "resource_id": resource.aid,
                    },
                )
            )
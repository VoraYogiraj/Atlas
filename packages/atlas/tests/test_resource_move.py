"""
ENG-053 — Atlas Resource Move

RED-phase contract tests.

ENG-053 defines Resource Move as an absolute 3D position mutation.

Canonical semantics:

    AtlasID + absolute AtlasPosition
        ->
    canonical Resource-associated spatial state

Important architectural boundaries:

- AtlasResource does not own position/transform fields.
- SceneNode is not the canonical engineering state.
- Move enters Atlas through AtlasApplication.execute().
- Canonical Resource identity remains AtlasID.
- Spatial state is Resource-associated canonical state, separate from
  AtlasResource itself.
- Invalid requests must be atomic.
- Move is absolute and therefore idempotent.
"""

from __future__ import annotations

import math

import pytest

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.application.queries import AtlasQuery
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.core.spatial import AtlasPosition
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_project_with_resource() -> tuple[
    AtlasProject,
    AtlasResource,
]:
    project = AtlasProject(
        name="ENG-053 Move Test Project",
    )

    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    project.add_classification(classification)

    resource = AtlasResource(
        classification=classification,
        name="North Wall",
    )

    project.add_resource(resource)

    return project, resource


def create_move_command(
    resource_id: AtlasID,
    *,
    x: float,
    y: float,
    z: float,
) -> AtlasCommand:
    """
    Create the canonical ENG-053 Move command.

    Move uses an absolute target position.
    """
    return AtlasCommand(
        name="move_resource",
        payload={
            "resource_id": resource_id,
            "position": {
                "x": x,
                "y": y,
                "z": z,
            },
        },
    )


def create_position_query(
    resource_id: AtlasID,
) -> AtlasQuery:
    """
    Query the canonical spatial state associated with a Resource.
    """
    return AtlasQuery(
        name="get_resource_position",
        payload={
            "resource_id": resource_id,
        },
    )


def get_position(
    application: AtlasApplication,
    resource_id: AtlasID,
) -> AtlasPosition:
    """
    Read canonical Resource spatial state through the application boundary.
    """
    result = application.query(
        create_position_query(resource_id),
    )

    assert isinstance(result, AtlasPosition)

    return result


# ---------------------------------------------------------------------------
# Command Surface
# ---------------------------------------------------------------------------


class TestResourceMoveCommand:
    def test_move_command_can_be_constructed(self) -> None:
        _, resource = create_project_with_resource()

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert isinstance(command, AtlasCommand)
        assert command.name == "move_resource"

    def test_move_command_targets_resource_by_atlas_id(self) -> None:
        _, resource = create_project_with_resource()

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert command.payload["resource_id"] == resource.aid
        assert isinstance(command.payload["resource_id"], AtlasID)

    def test_move_command_contains_absolute_position(self) -> None:
        _, resource = create_project_with_resource()

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert command.payload["position"] == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }

    def test_move_command_is_immutable(self) -> None:
        _, resource = create_project_with_resource()

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        with pytest.raises(Exception):
            command.name = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Application Boundary
# ---------------------------------------------------------------------------


class TestResourceMoveApplicationBoundary:
    def test_move_is_executed_through_atlas_application(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        result = application.execute(command)

        assert result is not None

    def test_position_is_observable_through_application_query(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        position = get_position(
            application,
            resource.aid,
        )

        assert position.x == 10.0
        assert position.y == 20.0
        assert position.z == 30.0

    def test_invalid_command_type_is_rejected(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        with pytest.raises(TypeError):
            application.execute(object())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Canonical Identity
# ---------------------------------------------------------------------------


class TestResourceMoveIdentity:
    def test_resource_identity_is_preserved(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_id = resource.aid

        command = create_move_command(
            original_id,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        resolved = project.require_resource(original_id)

        assert resolved.aid == original_id

    def test_move_mutates_canonical_registry_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved is resource


# ---------------------------------------------------------------------------
# Absolute Move Semantics
# ---------------------------------------------------------------------------


class TestResourceMoveSemantics:
    def test_move_sets_absolute_position(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        first_move = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        second_move = create_move_command(
            resource.aid,
            x=100.0,
            y=200.0,
            z=300.0,
        )

        application.execute(first_move)
        application.execute(second_move)

        position = get_position(
            application,
            resource.aid,
        )

        assert position.x == 100.0
        assert position.y == 200.0
        assert position.z == 300.0

    def test_move_is_not_a_delta_operation(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        first_move = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        second_move = create_move_command(
            resource.aid,
            x=5.0,
            y=6.0,
            z=7.0,
        )

        application.execute(first_move)
        application.execute(second_move)

        position = get_position(
            application,
            resource.aid,
        )

        assert position.x == 5.0
        assert position.y == 6.0
        assert position.z == 7.0

    def test_identical_move_is_idempotent(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)
        first = get_position(
            application,
            resource.aid,
        )

        application.execute(command)
        second = get_position(
            application,
            resource.aid,
        )

        assert second == first


# ---------------------------------------------------------------------------
# Position Validation
# ---------------------------------------------------------------------------


class TestResourceMoveValidation:
    @pytest.mark.parametrize(
        "position",
        [
            {},
            {"x": 1.0},
            {"y": 2.0},
            {"z": 3.0},
            {"x": 1.0, "y": 2.0},
            {"x": 1.0, "z": 3.0},
            {"y": 2.0, "z": 3.0},
        ],
    )
    def test_missing_position_component_is_rejected(
        self,
        position: dict[str, object],
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource.aid,
                "position": position,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        ["x", "y", "z"],
    )
    def test_non_numeric_axis_is_rejected(
        self,
        axis: str,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        position: dict[str, object] = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
        }

        position[axis] = "invalid"

        command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource.aid,
                "position": position,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "value",
        [
            math.nan,
            math.inf,
            -math.inf,
        ],
    )
    @pytest.mark.parametrize(
        "axis",
        ["x", "y", "z"],
    )
    def test_non_finite_axis_is_rejected(
        self,
        axis: str,
        value: float,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        position = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
        }

        position[axis] = value

        command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource.aid,
                "position": position,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "position",
        [
            None,
            (),
            [],
            "position",
            123,
        ],
    )
    def test_invalid_position_container_is_rejected(
        self,
        position: object,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource.aid,
                "position": position,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    def test_missing_resource_id_is_rejected(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="move_resource",
            payload={
                "position": {
                    "x": 1.0,
                    "y": 2.0,
                    "z": 3.0,
                },
            },
        )

        with pytest.raises((TypeError, ValueError, KeyError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "resource_id",
        [
            None,
            "resource-id",
            123,
            object(),
        ],
    )
    def test_invalid_resource_id_is_rejected(
        self,
        resource_id: object,
    ) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource_id,
                "position": {
                    "x": 1.0,
                    "y": 2.0,
                    "z": 3.0,
                },
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)


# ---------------------------------------------------------------------------
# Missing Resource
# ---------------------------------------------------------------------------


class TestResourceMoveMissingResource:
    def test_unknown_resource_id_is_rejected(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        unknown_id = AtlasID.generate()

        command = create_move_command(
            unknown_id,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        with pytest.raises((KeyError, ValueError)):
            application.execute(command)

    def test_unknown_resource_does_not_create_resource(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        before_count = project.resources.count

        unknown_id = AtlasID.generate()

        command = create_move_command(
            unknown_id,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        with pytest.raises((KeyError, ValueError)):
            application.execute(command)

        assert project.resources.count == before_count


# ---------------------------------------------------------------------------
# Resource Isolation
# ---------------------------------------------------------------------------


class TestResourceMoveIsolation:
    def test_move_does_not_create_second_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        before_count = project.resources.count

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        assert project.resources.count == before_count

    def test_move_does_not_replace_resource_object(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved is resource


# ---------------------------------------------------------------------------
# Resource State Preservation
# ---------------------------------------------------------------------------


class TestResourceMoveStatePreservation:
    def test_move_preserves_classification(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = resource.classification

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert resource.classification is original

    def test_move_preserves_name(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = resource.name

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert resource.name == original

    def test_move_preserves_properties(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = dict(resource.properties)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert dict(resource.properties) == original

    def test_move_preserves_relationships(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = tuple(resource.relationships)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert tuple(resource.relationships) == original

    def test_move_preserves_metadata(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = dict(resource.metadata)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert dict(resource.metadata) == original

    def test_move_preserves_semantic_tags(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = dict(resource.tags)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert dict(resource.tags) == original

    def test_move_preserves_categories(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = dict(resource.categories)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert dict(resource.categories) == original

    def test_move_preserves_lifecycle(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = resource.lifecycle

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert resource.lifecycle == original


# ---------------------------------------------------------------------------
# Scene Independence
# ---------------------------------------------------------------------------


class TestResourceMoveSceneIndependence:
    def test_move_requires_no_scene(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert result is not None

    def test_move_does_not_require_scene_node(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        position = get_position(
            application,
            resource.aid,
        )

        assert position == AtlasPosition(
            x=10.0,
            y=20.0,
            z=30.0,
        )

    def test_resource_does_not_receive_position_attribute(self) -> None:
        """
        ENG-053 must not put spatial state directly on AtlasResource.
        """
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        assert not hasattr(resource, "position")
        assert not hasattr(resource, "transform")


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestResourceMoveAtomicity:
    def test_invalid_move_preserves_existing_position(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        before = get_position(
            application,
            resource.aid,
        )

        invalid_command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": resource.aid,
                "position": {
                    "x": math.nan,
                    "y": 50.0,
                    "z": 60.0,
                },
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(invalid_command)

        after = get_position(
            application,
            resource.aid,
        )

        assert after == before

    def test_unknown_resource_move_does_not_mutate_existing_state(
        self,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_move_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            ),
        )

        before = get_position(
            application,
            resource.aid,
        )

        unknown_id = AtlasID.generate()

        with pytest.raises((KeyError, ValueError)):
            application.execute(
                create_move_command(
                    unknown_id,
                    x=100.0,
                    y=200.0,
                    z=300.0,
                ),
            )

        after = get_position(
            application,
            resource.aid,
        )

        assert after == before


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestResourceMoveDeterminism:
    def test_identical_requests_produce_identical_position(
        self,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        first = get_position(
            application,
            resource.aid,
        )

        application.execute(command)

        second = get_position(
            application,
            resource.aid,
        )

        assert second == first

    def test_move_result_does_not_depend_on_scene_state(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_move_command(
                resource.aid,
                x=11.0,
                y=22.0,
                z=33.0,
            ),
        )

        position = get_position(
            application,
            resource.aid,
        )

        assert position == AtlasPosition(
            x=11.0,
            y=22.0,
            z=33.0,
        )
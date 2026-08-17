"""
ENG-054 — Atlas Resource Rotate

Absolute 3D Resource rotation capability.

Canonical identity:
    AtlasID

Canonical state:
    Project-owned spatial state keyed by AtlasID

Command:
    rotate_resource

Query:
    get_resource_rotation
"""

from __future__ import annotations

import math
from collections.abc import Mapping

import pytest

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.application.queries import AtlasQuery
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


def create_project_with_resource() -> tuple[
    AtlasProject,
    AtlasResource,
]:
    project = AtlasProject(
        name="ENG-054 Rotate Test Project"
    )

    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    project.add_classification(
        classification
    )

    resource = AtlasResource(
        classification=classification,
        name="North Wall",
    )

    project.add_resource(
        resource
    )

    return project, resource


def create_rotate_command(
    resource_id: AtlasID,
    *,
    x: float,
    y: float,
    z: float,
) -> AtlasCommand:
    return AtlasCommand(
        name="rotate_resource",
        payload={
            "resource_id": resource_id,
            "rotation": {
                "x": x,
                "y": y,
                "z": z,
            },
        },
    )


def create_rotation_query(
    resource_id: AtlasID,
) -> AtlasQuery:
    return AtlasQuery(
        name="get_resource_rotation",
        parameters={
            "resource_id": resource_id,
        },
    )


def get_rotation(
    application: AtlasApplication,
    resource_id: AtlasID,
) -> Mapping[str, float]:
    result = application.query(
        create_rotation_query(
            resource_id
        )
    )

    assert isinstance(
        result,
        Mapping,
    )

    assert set(result.keys()) == {
        "x",
        "y",
        "z",
    }

    return result


# ---------------------------------------------------------------------------
# Command surface
# ---------------------------------------------------------------------------


class TestResourceRotateCommand:
    def test_command_can_be_constructed(self) -> None:
        _, resource = create_project_with_resource()

        command = create_rotate_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert isinstance(
            command,
            AtlasCommand,
        )

        assert command.name == (
            "rotate_resource"
        )

    def test_targets_resource_by_atlas_id(self) -> None:
        _, resource = create_project_with_resource()

        command = create_rotate_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert (
            command.payload["resource_id"]
            == resource.aid
        )

    def test_contains_absolute_rotation(self) -> None:
        _, resource = create_project_with_resource()

        command = create_rotate_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        assert command.payload[
            "rotation"
        ] == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


class TestResourceRotateApplication:
    def test_execute_through_application(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        result = application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert result == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }

    def test_query_returns_rotation(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        rotation = get_rotation(
            application,
            resource.aid,
        )

        assert rotation == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }


# ---------------------------------------------------------------------------
# Absolute semantics
# ---------------------------------------------------------------------------


class TestResourceRotateSemantics:
    def test_rotation_is_absolute(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=100.0,
                y=200.0,
                z=300.0,
            )
        )

        rotation = get_rotation(
            application,
            resource.aid,
        )

        assert rotation == {
            "x": 100.0,
            "y": 200.0,
            "z": 300.0,
        }

    def test_rotation_is_not_delta(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=5.0,
                y=6.0,
                z=7.0,
            )
        )

        rotation = get_rotation(
            application,
            resource.aid,
        )

        assert rotation == {
            "x": 5.0,
            "y": 6.0,
            "z": 7.0,
        }

    def test_identical_rotation_is_idempotent(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        command = create_rotate_command(
            resource.aid,
            x=10.0,
            y=20.0,
            z=30.0,
        )

        application.execute(command)

        first = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        application.execute(command)

        second = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        assert first == second


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestResourceRotateValidation:
    @pytest.mark.parametrize(
        "rotation",
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
    def test_missing_axis_rejected(
        self,
        rotation: dict[str, object],
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        command = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource.aid,
                "rotation": rotation,
            },
        )

        with pytest.raises(
            (TypeError, ValueError, KeyError)
        ):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        ["x", "y", "z"],
    )
    def test_non_numeric_axis_rejected(
        self,
        axis: str,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        rotation: dict[str, object] = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
        }

        rotation[axis] = "invalid"

        command = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource.aid,
                "rotation": rotation,
            },
        )

        with pytest.raises(
            (TypeError, ValueError)
        ):
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
    def test_non_finite_axis_rejected(
        self,
        axis: str,
        value: float,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        rotation = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
        }

        rotation[axis] = value

        command = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource.aid,
                "rotation": rotation,
            },
        )

        with pytest.raises(
            (TypeError, ValueError)
        ):
            application.execute(command)

    @pytest.mark.parametrize(
        "rotation",
        [
            None,
            (),
            [],
            "rotation",
            123,
        ],
    )
    def test_invalid_rotation_container_rejected(
        self,
        rotation: object,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        command = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource.aid,
                "rotation": rotation,
            },
        )

        with pytest.raises(
            (TypeError, ValueError)
        ):
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
    def test_invalid_resource_id_rejected(
        self,
        resource_id: object,
    ) -> None:
        project, _ = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        command = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource_id,
                "rotation": {
                    "x": 1.0,
                    "y": 2.0,
                    "z": 3.0,
                },
            },
        )

        with pytest.raises(
            (TypeError, ValueError)
        ):
            application.execute(command)


# ---------------------------------------------------------------------------
# Resource identity and preservation
# ---------------------------------------------------------------------------


class TestResourceRotateIdentity:
    def test_identity_preserved(self) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original_id = resource.aid

        application.execute(
            create_rotate_command(
                original_id,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert (
            project.require_resource(
                original_id
            )
            is resource
        )

    def test_resource_count_unchanged(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        before = project.resources.count

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert project.resources.count == before


# ---------------------------------------------------------------------------
# State preservation
# ---------------------------------------------------------------------------


class TestResourceRotateStatePreservation:
    def test_classification_preserved(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original = resource.classification

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert resource.classification is original

    def test_name_preserved(self) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original = resource.name

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert resource.name == original

    def test_properties_preserved(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original = dict(
            resource.properties
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert dict(
            resource.properties
        ) == original

    def test_metadata_preserved(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original = dict(
            resource.metadata
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert dict(
            resource.metadata
        ) == original

    def test_lifecycle_preserved(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        original = resource.lifecycle

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert resource.lifecycle == original


# ---------------------------------------------------------------------------
# Move compatibility
# ---------------------------------------------------------------------------


class TestResourceRotateMoveCompatibility:
    def test_rotation_does_not_change_position(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
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
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        position = application.query(
            AtlasQuery(
                name="get_resource_position",
                parameters={
                    "resource_id": resource.aid,
                },
            )
        )

        assert position == {
            "x": 11.0,
            "y": 22.0,
            "z": 33.0,
        }

    def test_move_does_not_change_rotation(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
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

        rotation = get_rotation(
            application,
            resource.aid,
        )

        assert rotation == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }


# ---------------------------------------------------------------------------
# Scene / engineering isolation
# ---------------------------------------------------------------------------


class TestResourceRotateIsolation:
    def test_no_scene_required(self) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        result = application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert result is not None

    def test_resource_has_no_rotation_attribute(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        assert not hasattr(
            resource,
            "rotation",
        )

        assert not hasattr(
            resource,
            "transform",
        )


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestResourceRotateAtomicity:
    def test_invalid_rotation_preserves_previous_state(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        application.execute(
            create_rotate_command(
                resource.aid,
                x=10.0,
                y=20.0,
                z=30.0,
            )
        )

        before = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        invalid = AtlasCommand(
            name="rotate_resource",
            payload={
                "resource_id": resource.aid,
                "rotation": {
                    "x": math.nan,
                    "y": 50.0,
                    "z": 60.0,
                },
            },
        )

        with pytest.raises(
            (TypeError, ValueError)
        ):
            application.execute(
                invalid
            )

        after = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        assert after == before

    def test_unknown_resource_does_not_mutate(
        self,
    ) -> None:
        project, resource = (
            create_project_with_resource()
        )

        application = AtlasApplication(
            project
        )

        before = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        unknown_id = AtlasID.generate()

        with pytest.raises(
            (KeyError, ValueError)
        ):
            application.execute(
                create_rotate_command(
                    unknown_id,
                    x=10.0,
                    y=20.0,
                    z=30.0,
                )
            )

        after = dict(
            get_rotation(
                application,
                resource.aid,
            )
        )

        assert after == before
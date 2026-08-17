"""
ENG-055 — Atlas Resource Scale

RED-phase contract tests.

These tests define the canonical Resource Scale contract before
ENG-055 implementation is accepted.

ENG-055 establishes:

    AtlasID
        ↓
    AtlasSpatialStateRegistry
        ├── Position
        ├── Rotation
        └── Scale

Scale is an absolute 3D spatial scale associated with an Atlas Resource.

The tests intentionally avoid importing the future implementation type
(AtlasSpatialScale) so that the RED phase fails on the missing capability
rather than failing during test collection because the type does not yet
exist.
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
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_project(
    *,
    name: str = "ENG-055 Test Project",
) -> AtlasProject:
    return AtlasProject(name=name)


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_project_with_resource(
    *,
    resource_name: str = "North Wall",
) -> tuple[AtlasProject, AtlasResource]:
    project = create_project()

    classification = create_classification()

    project.add_classification(
        classification,
    )

    resource = AtlasResource(
        classification=classification,
        name=resource_name,
    )

    project.add_resource(
        resource,
    )

    return project, resource


def create_scale_command(
    resource_id: AtlasID,
    *,
    x: object = 2.0,
    y: object = 3.0,
    z: object = 4.0,
) -> AtlasCommand:
    return AtlasCommand(
        name="scale_resource",
        payload={
            "resource_id": resource_id,
            "scale": {
                "x": x,
                "y": y,
                "z": z,
            },
        },
    )


def create_scale_query(
    resource_id: AtlasID,
) -> AtlasQuery:
    return AtlasQuery(
        name="get_resource_scale",
        parameters={
            "resource_id": resource_id,
        },
    )


def get_scale(
    application: AtlasApplication,
    resource_id: AtlasID,
) -> dict[str, float]:
    result = application.query(
        create_scale_query(resource_id),
    )

    assert isinstance(result, dict)

    return result


# ---------------------------------------------------------------------------
# Command surface
# ---------------------------------------------------------------------------


class TestResourceScaleCommand:
    def test_command_name_is_scale_resource(self) -> None:
        project, resource = create_project_with_resource()

        command = create_scale_command(
            resource.aid,
        )

        assert command.name == "scale_resource"
        assert command.payload["resource_id"] == resource.aid
        assert command.payload["scale"] == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }

    def test_command_can_be_constructed_without_implementation(self) -> None:
        project, resource = create_project_with_resource()

        command = create_scale_command(
            resource.aid,
            x=1.5,
            y=2.5,
            z=3.5,
        )

        assert isinstance(command, AtlasCommand)

    def test_query_name_is_get_resource_scale(self) -> None:
        project, resource = create_project_with_resource()

        query = create_scale_query(
            resource.aid,
        )

        assert query.name == "get_resource_scale"
        assert query.parameters["resource_id"] == resource.aid


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


class TestResourceScaleApplicationBoundary:
    def test_scale_enters_through_application_execute(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_scale_command(
            resource.aid,
            x=2.0,
            y=3.0,
            z=4.0,
        )

        result = application.execute(command)

        assert result == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }

    def test_scale_query_enters_through_application_query(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.query(
            create_scale_query(resource.aid),
        )

        assert result == {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0,
        }


# ---------------------------------------------------------------------------
# Default state
# ---------------------------------------------------------------------------


class TestResourceScaleDefaultState:
    def test_new_resource_has_neutral_scale(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = get_scale(
            application,
            resource.aid,
        )

        assert result == {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0,
        }

    def test_default_scale_is_not_zero(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = get_scale(
            application,
            resource.aid,
        )

        assert result["x"] != 0.0
        assert result["y"] != 0.0
        assert result["z"] != 0.0

    def test_default_scale_is_uniform(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = get_scale(
            application,
            resource.aid,
        )

        assert result["x"] == result["y"] == result["z"] == 1.0


# ---------------------------------------------------------------------------
# Absolute scale semantics
# ---------------------------------------------------------------------------


class TestResourceScaleSemantics:
    def test_scale_is_absolute_not_multiplicative(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        application.execute(
            create_scale_command(
                resource.aid,
                x=5.0,
                y=6.0,
                z=7.0,
            ),
        )

        result = get_scale(
            application,
            resource.aid,
        )

        assert result == {
            "x": 5.0,
            "y": 6.0,
            "z": 7.0,
        }

    def test_scale_is_not_additive(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        application.execute(
            create_scale_command(
                resource.aid,
                x=5.0,
                y=6.0,
                z=7.0,
            ),
        )

        result = get_scale(
            application,
            resource.aid,
        )

        assert result != {
            "x": 7.0,
            "y": 9.0,
            "z": 11.0,
        }

    def test_non_uniform_scale_is_valid(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=0.5,
            ),
        )

        assert result == {
            "x": 2.0,
            "y": 3.0,
            "z": 0.5,
        }

    @pytest.mark.parametrize(
        "value",
        [
            0.000001,
            0.1,
            0.5,
            1.0,
            1.5,
            2.0,
            10.0,
            1000.0,
        ],
    )
    def test_positive_scale_value_is_valid(
        self,
        value: float,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_scale_command(
                resource.aid,
                x=value,
                y=1.0,
                z=1.0,
            ),
        )

        assert result["x"] == value


# ---------------------------------------------------------------------------
# Validation — scale components
# ---------------------------------------------------------------------------


class TestResourceScaleValidation:
    @pytest.mark.parametrize(
        "axis",
        [
            "x",
            "y",
            "z",
        ],
    )
    def test_zero_scale_is_rejected(
        self,
        axis: str,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        scale: dict[str, object] = {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }
        scale[axis] = 0.0

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        [
            "x",
            "y",
            "z",
        ],
    )
    @pytest.mark.parametrize(
        "value",
        [
            -0.000001,
            -0.1,
            -1.0,
            -2.0,
            -100.0,
        ],
    )
    def test_negative_scale_is_rejected(
        self,
        axis: str,
        value: float,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        scale: dict[str, object] = {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }
        scale[axis] = value

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        [
            "x",
            "y",
            "z",
        ],
    )
    @pytest.mark.parametrize(
        "value",
        [
            math.nan,
            math.inf,
            -math.inf,
        ],
    )
    def test_non_finite_scale_is_rejected(
        self,
        axis: str,
        value: float,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        scale: dict[str, object] = {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }
        scale[axis] = value

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        [
            "x",
            "y",
            "z",
        ],
    )
    def test_boolean_scale_is_rejected(
        self,
        axis: str,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        scale: dict[str, object] = {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }
        scale[axis] = True

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "axis",
        [
            "x",
            "y",
            "z",
        ],
    )
    @pytest.mark.parametrize(
        "value",
        [
            None,
            "",
            "1.0",
            "2",
            object(),
        ],
    )
    def test_non_numeric_scale_is_rejected(
        self,
        axis: str,
        value: object,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        scale: dict[str, object] = {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }
        scale[axis] = value

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)


# ---------------------------------------------------------------------------
# Validation — scale container
# ---------------------------------------------------------------------------


class TestResourceScaleContainerValidation:
    @pytest.mark.parametrize(
        "scale",
        [
            None,
            (),
            [],
            "scale",
            123,
            object(),
        ],
    )
    def test_invalid_scale_container_is_rejected(
        self,
        scale: object,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "scale",
        [
            {},
            {"x": 2.0},
            {"y": 3.0},
            {"z": 4.0},
            {"x": 2.0, "y": 3.0},
            {"x": 2.0, "z": 4.0},
            {"y": 3.0, "z": 4.0},
        ],
    )
    def test_missing_scale_component_is_rejected(
        self,
        scale: dict[str, object],
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError, KeyError)):
            application.execute(command)

    @pytest.mark.parametrize(
        "scale",
        [
            {
                "x": 2.0,
                "y": 3.0,
                "z": 4.0,
                "w": 5.0,
            },
            {
                "x": 2.0,
                "y": 3.0,
                "z": 4.0,
                "uniform": 2.0,
            },
        ],
    )
    def test_extra_scale_component_is_rejected(
        self,
        scale: dict[str, object],
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": scale,
            },
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(command)


# ---------------------------------------------------------------------------
# Validation — resource identity
# ---------------------------------------------------------------------------


class TestResourceScaleIdentityValidation:
    @pytest.mark.parametrize(
        "resource_id",
        [
            None,
            "",
            "resource-id",
            1,
            1.0,
            True,
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
            name="scale_resource",
            payload={
                "resource_id": resource_id,
                "scale": {
                    "x": 2.0,
                    "y": 3.0,
                    "z": 4.0,
                },
            },
        )

        with pytest.raises((TypeError, ValueError, KeyError)):
            application.execute(command)  # type: ignore[arg-type]

    def test_unknown_resource_id_is_rejected(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        unknown_id = AtlasID.generate()

        command = create_scale_command(
            unknown_id,
        )

        with pytest.raises((KeyError, ValueError)):
            application.execute(command)

    def test_unknown_resource_does_not_create_resource(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        before_count = project.resources.count

        unknown_id = AtlasID.generate()

        with pytest.raises((KeyError, ValueError)):
            application.execute(
                create_scale_command(
                    unknown_id,
                ),
            )

        assert project.resources.count == before_count


# ---------------------------------------------------------------------------
# Query validation
# ---------------------------------------------------------------------------


class TestResourceScaleQueryValidation:
    @pytest.mark.parametrize(
        "resource_id",
        [
            None,
            "",
            "resource-id",
            1,
            1.0,
            True,
            object(),
        ],
    )
    def test_query_rejects_invalid_resource_id(
        self,
        resource_id: object,
    ) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        query = AtlasQuery(
            name="get_resource_scale",
            parameters={
                "resource_id": resource_id,
            },
        )

        with pytest.raises((TypeError, ValueError, KeyError)):
            application.query(query)  # type: ignore[arg-type]

    def test_query_rejects_unknown_resource(self) -> None:
        project, _ = create_project_with_resource()
        application = AtlasApplication(project)

        query = create_scale_query(
            AtlasID.generate(),
        )

        with pytest.raises((KeyError, ValueError)):
            application.query(query)


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestResourceScaleAtomicity:
    def test_invalid_scale_does_not_modify_previous_scale(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        invalid_command = create_scale_command(
            resource.aid,
            x=5.0,
            y=0.0,
            z=7.0,
        )

        with pytest.raises((TypeError, ValueError)):
            application.execute(invalid_command)

        result = get_scale(
            application,
            resource.aid,
        )

        assert result == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }

    @pytest.mark.parametrize(
        "invalid_scale",
        [
            {
                "x": 0.0,
                "y": 3.0,
                "z": 4.0,
            },
            {
                "x": 2.0,
                "y": -1.0,
                "z": 4.0,
            },
            {
                "x": 2.0,
                "y": math.nan,
                "z": 4.0,
            },
            {
                "x": 2.0,
                "y": 3.0,
                "z": math.inf,
            },
            {
                "x": 2.0,
                "y": 3.0,
            },
        ],
    )
    def test_invalid_scale_never_partially_mutates(
        self,
        invalid_scale: dict[str, object],
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=8.0,
                y=9.0,
                z=10.0,
            ),
        )

        command = AtlasCommand(
            name="scale_resource",
            payload={
                "resource_id": resource.aid,
                "scale": invalid_scale,
            },
        )

        with pytest.raises((TypeError, ValueError, KeyError)):
            application.execute(command)

        result = get_scale(
            application,
            resource.aid,
        )

        assert result == {
            "x": 8.0,
            "y": 9.0,
            "z": 10.0,
        }


# ---------------------------------------------------------------------------
# Idempotency and determinism
# ---------------------------------------------------------------------------


class TestResourceScaleDeterminism:
    def test_scale_is_idempotent(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_scale_command(
            resource.aid,
            x=2.5,
            y=3.5,
            z=4.5,
        )

        first = application.execute(command)
        second = application.execute(command)
        third = application.execute(command)

        assert first == {
            "x": 2.5,
            "y": 3.5,
            "z": 4.5,
        }
        assert second == first
        assert third == first

    def test_identical_initial_state_and_request_are_deterministic(
        self,
    ) -> None:
        project_a, resource_a = create_project_with_resource()
        project_b, resource_b = create_project_with_resource()

        application_a = AtlasApplication(project_a)
        application_b = AtlasApplication(project_b)

        result_a = application_a.execute(
            create_scale_command(
                resource_a.aid,
                x=1.25,
                y=2.5,
                z=3.75,
            ),
        )

        result_b = application_b.execute(
            create_scale_command(
                resource_b.aid,
                x=1.25,
                y=2.5,
                z=3.75,
            ),
        )

        assert result_a == result_b


# ---------------------------------------------------------------------------
# Resource preservation
# ---------------------------------------------------------------------------


class TestResourceScalePreservation:
    def test_scale_preserves_resource_identity(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_id = resource.aid

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        resolved = project.require_resource(
            original_id,
        )

        assert resolved.aid == original_id

    def test_scale_preserves_resource_name(self) -> None:
        project, resource = create_project_with_resource(
            resource_name="Preserved Wall",
        )
        application = AtlasApplication(project)

        original_name = resource.name

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        resolved = project.require_resource(
            resource.aid,
        )

        assert resolved.name == original_name

    def test_scale_does_not_add_scale_to_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        assert not hasattr(resource, "scale")

    def test_scale_does_not_add_transform_to_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        assert not hasattr(resource, "transform")


# ---------------------------------------------------------------------------
# Spatial isolation — Position
# ---------------------------------------------------------------------------


class TestResourceScalePositionIsolation:
    def test_scale_does_not_modify_position(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

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
            ),
        )

        before = application.query(
            AtlasQuery(
                name="get_resource_position",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        after = application.query(
            AtlasQuery(
                name="get_resource_position",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        assert after == before
        assert after == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }


# ---------------------------------------------------------------------------
# Spatial isolation — Rotation
# ---------------------------------------------------------------------------


class TestResourceScaleRotationIsolation:
    def test_scale_does_not_modify_rotation(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            AtlasCommand(
                name="rotate_resource",
                payload={
                    "resource_id": resource.aid,
                    "rotation": {
                        "x": 15.0,
                        "y": 25.0,
                        "z": 35.0,
                    },
                },
            ),
        )

        before = application.query(
            AtlasQuery(
                name="get_resource_rotation",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        after = application.query(
            AtlasQuery(
                name="get_resource_rotation",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        assert after == before
        assert after == {
            "x": 15.0,
            "y": 25.0,
            "z": 35.0,
        }


# ---------------------------------------------------------------------------
# Resource isolation
# ---------------------------------------------------------------------------


class TestResourceScaleIsolation:
    def test_scaling_one_resource_does_not_change_another(self) -> None:
        project = create_project()

        classification_a = create_classification(
            id="wall",
            name="Wall",
        )
        classification_b = create_classification(
            id="door",
            name="Door",
        )

        project.add_classification(
            classification_a,
        )
        project.add_classification(
            classification_b,
        )

        resource_a = AtlasResource(
            classification=classification_a,
            name="Wall A",
        )
        resource_b = AtlasResource(
            classification=classification_b,
            name="Door B",
        )

        project.add_resource(
            resource_a,
        )
        project.add_resource(
            resource_b,
        )

        application = AtlasApplication(project)

        before_b = get_scale(
            application,
            resource_b.aid,
        )

        application.execute(
            create_scale_command(
                resource_a.aid,
                x=5.0,
                y=6.0,
                z=7.0,
            ),
        )

        after_b = get_scale(
            application,
            resource_b.aid,
        )

        assert after_b == before_b
        assert after_b == {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0,
        }

    def test_scaling_one_resource_does_not_change_registry_count(
        self,
    ) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        before_count = project.resources.count

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        assert project.resources.count == before_count


# ---------------------------------------------------------------------------
# Scene independence
# ---------------------------------------------------------------------------


class TestResourceScaleSceneIndependence:
    def test_scale_does_not_require_scene(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        assert result == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }

    def test_scale_does_not_require_scene_node(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        assert result is not None


# ---------------------------------------------------------------------------
# Command/query isolation
# ---------------------------------------------------------------------------


class TestResourceScaleCanonicalBoundary:
    def test_scale_query_returns_only_canonical_scale_mapping(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        result = application.query(
            create_scale_query(resource.aid),
        )

        assert result == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }

        assert "resource" not in result
        assert "scene" not in result
        assert "node" not in result
        assert "transform" not in result

    def test_scale_command_targets_canonical_atlas_id(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        result = application.execute(
            create_scale_command(
                resource.aid,
                x=7.0,
                y=8.0,
                z=9.0,
            ),
        )

        assert result == {
            "x": 7.0,
            "y": 8.0,
            "z": 9.0,
        }

        queried = get_scale(
            application,
            resource.aid,
        )

        assert queried == result


# ---------------------------------------------------------------------------
# Full state preservation across all three spatial capabilities
# ---------------------------------------------------------------------------


class TestResourceScaleSpatialStatePreservation:
    def test_scale_preserves_position_and_rotation_together(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        application.execute(
            AtlasCommand(
                name="move_resource",
                payload={
                    "resource_id": resource.aid,
                    "position": {
                        "x": 100.0,
                        "y": 200.0,
                        "z": 300.0,
                    },
                },
            ),
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
            ),
        )

        application.execute(
            create_scale_command(
                resource.aid,
                x=2.0,
                y=3.0,
                z=4.0,
            ),
        )

        position = application.query(
            AtlasQuery(
                name="get_resource_position",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        rotation = application.query(
            AtlasQuery(
                name="get_resource_rotation",
                parameters={
                    "resource_id": resource.aid,
                },
            ),
        )

        scale = application.query(
            create_scale_query(resource.aid),
        )

        assert position == {
            "x": 100.0,
            "y": 200.0,
            "z": 300.0,
        }

        assert rotation == {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        }

        assert scale == {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        }


# ---------------------------------------------------------------------------
# RED contract guard
# ---------------------------------------------------------------------------


class TestResourceScaleImplementationBoundary:
    def test_scale_command_is_not_basic_editing(self) -> None:
        project, resource = create_project_with_resource()

        command = create_scale_command(
            resource.aid,
        )

        assert command.name == "scale_resource"
        assert command.name != "scale"

    def test_scale_is_resource_level_not_scene_node_level(self) -> None:
        project, resource = create_project_with_resource()

        command = create_scale_command(
            resource.aid,
        )

        assert command.payload["resource_id"] == resource.aid
        assert "node_id" not in command.payload
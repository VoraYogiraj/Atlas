"""
ENG-053 — Atlas Resource Move

RED-phase contract tests.

These tests define the application-boundary and canonical-identity contract
for Resource Move before the implementation exists.

Important:
    ENG-053 has not yet frozen the concrete representation of canonical
    spatial state. Therefore these tests intentionally do not introduce
    position/transform fields on AtlasResource.
"""

from __future__ import annotations

import pytest

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.classification.classification import AtlasClassification
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_resource() -> AtlasResource:
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    return AtlasResource(
        classification=classification,
        name="North Wall",
    )


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

    # AtlasProject requires the Resource's Classification
    # to be registered before the Resource itself is added.
    project.add_classification(classification)

    resource = AtlasResource(
        classification=classification,
        name="North Wall",
    )

    project.add_resource(resource)

    return project, resource


def create_move_command(
    resource_id: AtlasID,
) -> AtlasCommand:
    """
    Build the ENG-053 command using only the semantics currently frozen.

    The concrete Move payload is intentionally not defined here because
    ENG-053 has not yet frozen the representation of canonical spatial state.
    """
    return AtlasCommand(
        name="move_resource",
        payload={
            "resource_id": resource_id,
        },
    )


# ---------------------------------------------------------------------------
# Command Surface
# ---------------------------------------------------------------------------


class TestResourceMoveCommand:
    def test_move_command_can_be_constructed(self) -> None:
        project, resource = create_project_with_resource()

        command = create_move_command(resource.aid)

        assert isinstance(command, AtlasCommand)
        assert command.name == "move_resource"
        assert command.payload["resource_id"] == resource.aid

    def test_move_command_requires_canonical_resource_identity(
        self,
    ) -> None:
        project, resource = create_project_with_resource()

        command = create_move_command(resource.aid)

        assert isinstance(command.payload["resource_id"], AtlasID)

    def test_move_command_is_immutable(self) -> None:
        project, resource = create_project_with_resource()

        command = create_move_command(resource.aid)

        with pytest.raises(Exception):
            command.name = "other"  # type: ignore[misc]

    def test_move_command_does_not_own_domain_rules(self) -> None:
        project, resource = create_project_with_resource()

        command = create_move_command(resource.aid)

        assert command.name == "move_resource"
        assert isinstance(command.payload, dict)


# ---------------------------------------------------------------------------
# Application Boundary
# ---------------------------------------------------------------------------


class TestResourceMoveApplicationBoundary:
    def test_move_is_executed_through_atlas_application(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(resource.aid)

        # RED:
        # AtlasApplication does not yet implement "move_resource".
        result = application.execute(command)

        assert result is not None

    def test_unknown_resource_identity_is_rejected(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        unknown_id = AtlasID.generate()
        command = create_move_command(unknown_id)

        with pytest.raises(Exception):
            application.execute(command)

    def test_invalid_command_type_is_rejected(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        with pytest.raises(TypeError):
            application.execute(object())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Canonical Resource Identity
# ---------------------------------------------------------------------------


class TestResourceMoveIdentity:
    def test_resource_identity_is_preserved(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_id = resource.aid

        command = create_move_command(original_id)

        # RED:
        application.execute(command)

        moved_resource = project.require_resource(original_id)

        assert moved_resource.aid == original_id

    def test_move_targets_canonical_registry_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved is resource


# ---------------------------------------------------------------------------
# Resource Isolation
# ---------------------------------------------------------------------------


class TestResourceMoveIsolation:
    def test_move_does_not_create_second_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        before_count = project.resources.count

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        assert project.resources.count == before_count

    def test_move_does_not_replace_resource_identity(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_resource = resource

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved is original_resource


# ---------------------------------------------------------------------------
# Resource State Preservation
# ---------------------------------------------------------------------------


class TestResourceMoveStatePreservation:
    def test_move_preserves_classification(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_classification = resource.classification

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved.classification is original_classification

    def test_move_preserves_name(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_name = resource.name

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved.name == original_name

    def test_move_preserves_lifecycle(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_lifecycle = resource.lifecycle

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert resolved.lifecycle == original_lifecycle

    def test_move_preserves_properties(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_properties = dict(resource.properties)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert dict(resolved.properties) == original_properties

    def test_move_preserves_relationships(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_relationships = tuple(resource.relationships)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert tuple(resolved.relationships) == original_relationships

    def test_move_preserves_metadata(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_metadata = dict(resource.metadata)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert dict(resolved.metadata) == original_metadata

    def test_move_preserves_semantic_tags(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_tags = dict(resource.tags)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert dict(resolved.tags) == original_tags

    def test_move_preserves_categories(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original_categories = dict(resource.categories)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)

        resolved = project.require_resource(resource.aid)

        assert dict(resolved.categories) == original_categories


# ---------------------------------------------------------------------------
# Scene / Presentation Isolation
# ---------------------------------------------------------------------------


class TestResourceMoveSceneIsolation:
    def test_move_does_not_require_scene(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(resource.aid)

        # RED:
        # A canonical Resource Move must not require a Scene instance.
        application.execute(command)

    def test_move_does_not_mutate_scene_node_state(self) -> None:
        """
        ENG-053 must not silently delegate Resource Move to ENG-051
        SceneNode transformation.
        """
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        command = create_move_command(resource.aid)

        # RED:
        application.execute(command)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestResourceMoveDeterminism:
    def test_identical_move_requests_are_deterministic(self) -> None:
        project_a, resource_a = create_project_with_resource()
        project_b, resource_b = create_project_with_resource()

        application_a = AtlasApplication(project_a)
        application_b = AtlasApplication(project_b)

        command_a = create_move_command(resource_a.aid)
        command_b = create_move_command(resource_b.aid)

        # RED:
        result_a = application_a.execute(command_a)
        result_b = application_b.execute(command_b)

        assert result_a == result_b


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestResourceMoveAtomicity:
    def test_invalid_move_does_not_partially_mutate_resource(self) -> None:
        project, resource = create_project_with_resource()
        application = AtlasApplication(project)

        original = {
            "aid": resource.aid,
            "name": resource.name,
            "classification": resource.classification,
            "properties": dict(resource.properties),
            "relationships": tuple(resource.relationships),
            "metadata": dict(resource.metadata),
            "tags": dict(resource.tags),
            "categories": dict(resource.categories),
            "lifecycle": resource.lifecycle,
        }

        invalid_command = AtlasCommand(
            name="move_resource",
            payload={
                "resource_id": AtlasID.generate(),
            },
        )

        with pytest.raises(Exception):
            application.execute(invalid_command)

        assert resource.aid == original["aid"]
        assert resource.name == original["name"]
        assert resource.classification is original["classification"]
        assert dict(resource.properties) == original["properties"]
        assert tuple(resource.relationships) == original["relationships"]
        assert dict(resource.metadata) == original["metadata"]
        assert dict(resource.tags) == original["tags"]
        assert dict(resource.categories) == original["categories"]
        assert resource.lifecycle == original["lifecycle"]
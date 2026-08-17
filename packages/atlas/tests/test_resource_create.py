"""
ENG-052 — Atlas Resource Create

RED contract for canonical Resource creation through the
Atlas Application boundary.

Resource creation must create the canonical AtlasResource and
register it in the canonical AtlasProject Resource Registry.

This test does not introduce a new Resource model.
"""

from __future__ import annotations

import pytest

from atlas.application import AtlasApplication, AtlasCommand
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _classification() -> AtlasClassification:
    return AtlasClassification(
        id="wall",
        name="Wall",
    )


def _project() -> AtlasProject:
    return AtlasProject(
        name="ENG-052 Test Project",
    )


def _application() -> AtlasApplication:
    return AtlasApplication(
        _project(),
    )


# ---------------------------------------------------------------------------
# Command construction
# ---------------------------------------------------------------------------


def test_create_resource_command_is_an_atlas_command() -> None:
    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": _classification(),
            "name": "North Wall",
        },
    )

    assert isinstance(command, AtlasCommand)
    assert command.name == "create_resource"


# ---------------------------------------------------------------------------
# Application boundary
# ---------------------------------------------------------------------------


def test_create_resource_is_executed_through_application_boundary() -> None:
    application = _application()

    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": _classification(),
            "name": "North Wall",
        },
    )

    result = application.execute(command)

    assert result is not None


def test_resource_creation_does_not_require_workspace() -> None:
    project = _project()
    application = AtlasApplication(project)

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert isinstance(resource, AtlasResource)


def test_resource_creation_does_not_require_scene() -> None:
    project = _project()
    application = AtlasApplication(project)

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert isinstance(resource, AtlasResource)


# ---------------------------------------------------------------------------
# Canonical Resource creation
# ---------------------------------------------------------------------------


def test_create_resource_returns_atlas_resource() -> None:
    application = _application()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert isinstance(resource, AtlasResource)


def test_created_resource_has_requested_classification() -> None:
    application = _application()
    classification = _classification()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": classification,
                "name": "North Wall",
            },
        )
    )

    assert resource.classification is classification


def test_created_resource_has_requested_name() -> None:
    application = _application()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert resource.name == "North Wall"


def test_resource_creation_without_name_is_supported() -> None:
    application = _application()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
            },
        )
    )

    assert resource.name is None


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_created_resource_receives_atlas_identity() -> None:
    application = _application()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert resource.aid is not None


def test_each_created_resource_has_distinct_atlas_identity() -> None:
    application = _application()

    first = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "Wall A",
            },
        )
    )

    second = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "Wall B",
            },
        )
    )

    assert first.aid != second.aid


# ---------------------------------------------------------------------------
# Canonical Project / Registry state
# ---------------------------------------------------------------------------


def test_created_resource_is_registered_in_canonical_project() -> None:
    project = _project()
    application = AtlasApplication(project)

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert project.require_resource(resource.aid) is resource


def test_created_resource_is_present_in_project_registry() -> None:
    project = _project()
    application = AtlasApplication(project)

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert project.resources.get(resource.aid) is resource


def test_resource_creation_increases_registry_count_by_one() -> None:
    project = _project()
    application = AtlasApplication(project)

    before = project.resources.count

    application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert project.resources.count == before + 1


def test_created_resource_is_contained_by_project_registry() -> None:
    project = _project()
    application = AtlasApplication(project)

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert project.resources.contains(resource.aid)


# ---------------------------------------------------------------------------
# Existing Resource defaults
# ---------------------------------------------------------------------------


def test_created_resource_starts_in_existing_created_lifecycle_state() -> None:
    application = _application()

    resource = application.execute(
        AtlasCommand(
            name="create_resource",
            payload={
                "classification": _classification(),
                "name": "North Wall",
            },
        )
    )

    assert resource.lifecycle == "created"


# ---------------------------------------------------------------------------
# Invalid requests / atomicity
# ---------------------------------------------------------------------------


def test_invalid_create_command_does_not_mutate_project() -> None:
    project = _project()
    application = AtlasApplication(project)

    before_count = project.resources.count

    with pytest.raises((TypeError, ValueError)):
        application.execute(
            AtlasCommand(
                name="create_resource",
                payload={
                    "classification": "Wall",
                    "name": "Invalid Wall",
                },
            )
        )

    assert project.resources.count == before_count


def test_missing_classification_does_not_mutate_project() -> None:
    project = _project()
    application = AtlasApplication(project)

    before_count = project.resources.count

    with pytest.raises((TypeError, ValueError, KeyError)):
        application.execute(
            AtlasCommand(
                name="create_resource",
                payload={
                    "name": "Invalid Wall",
                },
            )
        )

    assert project.resources.count == before_count
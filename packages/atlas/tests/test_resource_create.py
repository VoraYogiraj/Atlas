"""
ENG-052 — Atlas Resource Create

RED contract for canonical Resource creation through the
Atlas Application boundary.

This test suite introduces Resource creation as an application
capability without redefining AtlasResource itself.
"""

from __future__ import annotations

import pytest

from atlas.application import AtlasApplication, AtlasCommand
from atlas.classification.classification import AtlasClassification
from atlas.project.project import AtlasProject


def _classification() -> AtlasClassification:
    return AtlasClassification(name="Wall")


def _project() -> AtlasProject:
    return AtlasProject()


def _application() -> AtlasApplication:
    return AtlasApplication(_project())


# ---------------------------------------------------------------------------
# Construction / boundary
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


# ---------------------------------------------------------------------------
# Canonical Resource creation
# ---------------------------------------------------------------------------


def test_create_resource_returns_atlas_resource() -> None:
    application = _application()

    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": _classification(),
            "name": "North Wall",
        },
    )

    resource = application.execute(command)

    from atlas.core.resource import AtlasResource

    assert isinstance(resource, AtlasResource)


def test_created_resource_has_requested_classification() -> None:
    application = _application()
    classification = _classification()

    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": classification,
            "name": "North Wall",
        },
    )

    resource = application.execute(command)

    assert resource.classification is classification


def test_created_resource_has_requested_name() -> None:
    application = _application()

    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": _classification(),
            "name": "North Wall",
        },
    )

    resource = application.execute(command)

    assert resource.name == "North Wall"


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_created_resource_receives_atlas_identity() -> None:
    application = _application()

    command = AtlasCommand(
        name="create_resource",
        payload={
            "classification": _classification(),
            "name": "North Wall",
        },
    )

    resource = application.execute(command)

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
# Registry / canonical project state
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


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


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

    assert str(resource.lifecycle) == "created"


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


# ---------------------------------------------------------------------------
# Architecture boundaries
# ---------------------------------------------------------------------------


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

    assert resource.aid is not None


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

    assert resource.aid is not None
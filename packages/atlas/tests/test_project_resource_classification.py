from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_resource(
    classification: AtlasClassification,
    name: str = "North Wall",
) -> AtlasResource:
    return AtlasResource(
        classification=classification,
        name=name,
    )


# ----------------------------------------------------------------------
# Valid Classification
# ----------------------------------------------------------------------


def test_project_can_add_resource_with_registered_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    result = project.add_resource(resource)

    assert result is resource
    assert project.resources.contains(resource.aid)


def test_project_resource_keeps_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    project.add_resource(resource)

    assert resource.classification is wall


def test_project_can_add_multiple_resources_of_same_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    south_wall = create_resource(
        wall,
        "South Wall",
    )

    project.add_resource(north_wall)
    project.add_resource(south_wall)

    assert project.resources.count == 2


# ----------------------------------------------------------------------
# Invalid Classification
# ----------------------------------------------------------------------


def test_project_rejects_resource_with_unregistered_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    resource = create_resource(wall)

    try:
        project.add_resource(resource)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected resource with unregistered classification "
            "to raise ValueError"
        )


def test_project_rejects_resource_from_another_project_classification():
    first = AtlasProject(
        name="First Project"
    )

    second = AtlasProject(
        name="Second Project"
    )

    wall = create_classification()

    first.add_classification(wall)

    resource = create_resource(wall)

    try:
        second.add_resource(resource)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected resource classification belonging to "
            "another project to raise ValueError"
        )


def test_project_resource_registry_remains_unchanged_after_invalid_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    resource = create_resource(wall)

    try:
        project.add_resource(resource)
    except ValueError:
        pass

    assert project.resources.count == 0
    assert not project.resources.contains(resource.aid)


# ----------------------------------------------------------------------
# Classification Identity
# ----------------------------------------------------------------------


def test_project_validates_classification_by_identity_id():
    project = AtlasProject(
        name="Residential Project"
    )

    registered_wall = create_classification(
        id="wall",
        name="Wall",
    )

    project.add_classification(registered_wall)

    equivalent_wall = create_classification(
        id="wall",
        name="Wall",
    )

    resource = create_resource(
        equivalent_wall,
        "North Wall",
    )

    result = project.add_resource(resource)

    assert result is resource
    assert project.resources.contains(resource.aid)


def test_project_rejects_unknown_classification_id():
    project = AtlasProject(
        name="Residential Project"
    )

    registered_wall = create_classification(
        id="wall",
        name="Wall",
    )

    project.add_classification(registered_wall)

    unknown_wall = create_classification(
        id="unknown-wall",
        name="Wall",
    )

    resource = create_resource(
        unknown_wall,
        "North Wall",
    )

    try:
        project.add_resource(resource)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unknown classification ID "
            "to raise ValueError"
        )


# ----------------------------------------------------------------------
# Classification Removal Integrity
# ----------------------------------------------------------------------


def test_project_cannot_remove_classification_used_by_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    project.add_resource(resource)

    try:
        project.remove_classification(wall.id)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected classification used by a resource "
            "to raise ValueError"
        )


def test_project_can_remove_unused_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    removed = project.remove_classification(wall.id)

    assert removed is wall
    assert not project.classifications.contains(wall.id)
    assert not project.classification_hierarchy.contains(
        wall.id
    )


def test_project_resource_remains_registered_when_classification_removal_fails():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    project.add_resource(resource)

    try:
        project.remove_classification(wall.id)
    except ValueError:
        pass

    assert project.classifications.contains(wall.id)
    assert project.classification_hierarchy.contains(
        wall.id
    )
    assert project.resources.contains(resource.aid)


# ----------------------------------------------------------------------
# Resource Removal
# ----------------------------------------------------------------------


def test_project_can_remove_resource_with_registered_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    project.add_resource(resource)

    removed = project.remove_resource(resource)

    assert removed is resource
    assert not project.resources.contains(resource.aid)


def test_project_can_remove_classification_after_resource_is_removed():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification()

    project.add_classification(wall)

    resource = create_resource(wall)

    project.add_resource(resource)
    project.remove_resource(resource)

    removed = project.remove_classification(wall.id)

    assert removed is wall
    assert not project.classifications.contains(wall.id)


# ----------------------------------------------------------------------
# Project Isolation
# ----------------------------------------------------------------------


def test_resource_classification_validation_is_project_scoped():
    first = AtlasProject(
        name="First Project"
    )

    second = AtlasProject(
        name="Second Project"
    )

    wall = create_classification()

    first.add_classification(wall)

    first_resource = create_resource(
        wall,
        "First Wall",
    )

    first.add_resource(first_resource)

    assert first.resources.contains(
        first_resource.aid
    )

    try:
        second.add_resource(first_resource)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected resource to be rejected by "
            "another project"
        )

    assert second.resources.count == 0
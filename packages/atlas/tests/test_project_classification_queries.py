from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project import AtlasProject


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str,
    name: str,
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_resource(
    classification: AtlasClassification,
    name: str,
) -> AtlasResource:
    return AtlasResource(
        classification=classification,
        name=name,
    )


def add_resource(
    project: AtlasProject,
    resource: AtlasResource,
) -> AtlasResource:
    """
    Register the Resource classification with the Project when needed,
    then register the Resource.
    """
    classification_id = resource.classification.id

    if not project.classifications.contains(
        classification_id
    ):
        project.add_classification(
            resource.classification
        )

    return project.add_resource(
        resource
    )


# ----------------------------------------------------------------------
# Basic Queries
# ----------------------------------------------------------------------


def test_project_returns_resources_for_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    south_wall = create_resource(
        wall,
        "South Wall",
    )

    add_resource(
        project,
        north_wall,
    )

    add_resource(
        project,
        south_wall,
    )

    result = project.resources_for_classification(
        "wall"
    )

    assert result == [
        north_wall,
        south_wall,
    ]


def test_project_returns_empty_list_for_unknown_classification():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    add_resource(
        project,
        north_wall,
    )

    result = project.resources_for_classification(
        "door"
    )

    assert result == []


def test_project_does_not_return_other_classifications():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    door = create_classification(
        id="door",
        name="Door",
    )

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    entrance_door = create_resource(
        door,
        "Entrance Door",
    )

    add_resource(
        project,
        north_wall,
    )

    add_resource(
        project,
        entrance_door,
    )

    result = project.resources_for_classification(
        "wall"
    )

    assert result == [
        north_wall,
    ]


# ----------------------------------------------------------------------
# Classification Identity
# ----------------------------------------------------------------------


def test_project_query_uses_classification_id():
    project = AtlasProject(
        name="Residential Project"
    )

    registered_classification = create_classification(
        id="wall",
        name="Wall",
    )

    equivalent_classification = create_classification(
        id="wall",
        name="Wall",
    )

    north_wall = create_resource(
        registered_classification,
        "North Wall",
    )

    add_resource(
        project,
        north_wall,
    )

    result = project.resources_for_classification(
        equivalent_classification.id
    )

    assert result == [
        north_wall,
    ]


# ----------------------------------------------------------------------
# Registration Order
# ----------------------------------------------------------------------


def test_project_preserves_resource_registration_order():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    first = create_resource(
        wall,
        "First Wall",
    )

    second = create_resource(
        wall,
        "Second Wall",
    )

    third = create_resource(
        wall,
        "Third Wall",
    )

    add_resource(project, first)
    add_resource(project, second)
    add_resource(project, third)

    result = project.resources_for_classification(
        "wall"
    )

    assert result == [
        first,
        second,
        third,
    ]


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_project_query_updates_after_resource_removal():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    south_wall = create_resource(
        wall,
        "South Wall",
    )

    add_resource(project, north_wall)
    add_resource(project, south_wall)

    project.remove_resource(
        north_wall
    )

    result = project.resources_for_classification(
        "wall"
    )

    assert result == [
        south_wall,
    ]


def test_project_query_is_empty_after_all_resources_are_removed():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    north_wall = create_resource(
        wall,
        "North Wall",
    )

    add_resource(
        project,
        north_wall,
    )

    project.remove_resource(
        north_wall
    )

    assert project.resources_for_classification(
        "wall"
    ) == []


# ----------------------------------------------------------------------
# Project Isolation
# ----------------------------------------------------------------------


def test_project_classification_query_is_project_scoped():
    first = AtlasProject(
        name="Project A"
    )

    second = AtlasProject(
        name="Project B"
    )

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    first_wall = create_resource(
        wall,
        "First Wall",
    )

    second_wall = create_resource(
        wall,
        "Second Wall",
    )

    add_resource(
        first,
        first_wall,
    )

    add_resource(
        second,
        second_wall,
    )

    assert first.resources_for_classification(
        "wall"
    ) == [
        first_wall,
    ]

    assert second.resources_for_classification(
        "wall"
    ) == [
        second_wall,
    ]


# ----------------------------------------------------------------------
# Invalid Input
# ----------------------------------------------------------------------


def test_project_rejects_empty_classification_id_query():
    project = AtlasProject(
        name="Residential Project"
    )

    try:
        project.resources_for_classification(
            ""
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty classification ID "
            "to raise ValueError"
        )


def test_project_rejects_whitespace_classification_id_query():
    project = AtlasProject(
        name="Residential Project"
    )

    try:
        project.resources_for_classification(
            "   "
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace classification ID "
            "to raise ValueError"
        )
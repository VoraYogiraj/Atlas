from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.relationships.relationship import AtlasRelationship


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str = "building-element",
    name: str = "Building Element",
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


def create_project():
    project = AtlasProject(
        name="Residential Project"
    )

    classification = create_classification()

    project.add_classification(
        classification
    )

    wall = create_resource(
        classification,
        "Wall",
    )

    door = create_resource(
        classification,
        "Door",
    )

    window = create_resource(
        classification,
        "Window",
    )

    project.add_resource(wall)
    project.add_resource(door)
    project.add_resource(window)

    return (
        project,
        wall,
        door,
        window,
    )


def create_relationship(
    *,
    id: str,
    relationship_type: str,
    source: AtlasResource,
    target: AtlasResource,
) -> AtlasRelationship:
    return AtlasRelationship(
        id=id,
        relationship_type=relationship_type,
        source=source,
        target=target,
    )


# ----------------------------------------------------------------------
# Project Resource Relationship Queries
# ----------------------------------------------------------------------


def test_project_relationships_for_resource():
    project, wall, door, window = create_project()

    contains = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    supports = create_relationship(
        id="wall-supports-window",
        relationship_type="supports",
        source=wall,
        target=window,
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    result = project.relationships_for_resource(
        wall
    )

    assert result == [
        contains,
        supports,
    ]


def test_project_relationships_for_resource_includes_incoming():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.relationships_for_resource(
        door
    ) == [
        relationship
    ]


def test_project_relationships_for_resource_returns_empty():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.relationships_for_resource(
        window
    ) == []


# ----------------------------------------------------------------------
# Project Outgoing Queries
# ----------------------------------------------------------------------


def test_project_outgoing_relationships():
    project, wall, door, window = create_project()

    contains = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    supports = create_relationship(
        id="wall-supports-window",
        relationship_type="supports",
        source=wall,
        target=window,
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    result = project.outgoing_relationships(
        wall
    )

    assert result == [
        contains,
        supports,
    ]


def test_project_outgoing_relationships_excludes_incoming():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="door-contained-by-wall",
        relationship_type="contained-by",
        source=door,
        target=wall,
    )

    project.add_relationship(
        relationship
    )

    assert project.outgoing_relationships(
        wall
    ) == []


def test_project_outgoing_relationships_empty():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.outgoing_relationships(
        door
    ) == []


# ----------------------------------------------------------------------
# Project Incoming Queries
# ----------------------------------------------------------------------


def test_project_incoming_relationships():
    project, wall, door, window = create_project()

    contains = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    supports = create_relationship(
        id="window-supported-by-wall",
        relationship_type="supported-by",
        source=window,
        target=wall,
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    result = project.incoming_relationships(
        wall
    )

    assert result == [
        supports,
    ]


def test_project_incoming_relationships_excludes_outgoing():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.incoming_relationships(
        wall
    ) == []


def test_project_incoming_relationships_empty():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.incoming_relationships(
        window
    ) == []


# ----------------------------------------------------------------------
# Project Relationship Type Queries
# ----------------------------------------------------------------------


def test_project_relationships_by_type():
    project, wall, door, window = create_project()

    contains = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    supports = create_relationship(
        id="wall-supports-window",
        relationship_type="supports",
        source=wall,
        target=window,
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    assert project.relationships_by_type(
        "contains"
    ) == [
        contains
    ]

    assert project.relationships_by_type(
        "supports"
    ) == [
        supports
    ]


def test_project_relationships_by_type_returns_empty_for_unknown_type():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.relationships_by_type(
        "supports"
    ) == []


def test_project_relationships_by_type_preserves_order():
    project, wall, door, window = create_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=wall,
        target=window,
    )

    third = create_relationship(
        id="third",
        relationship_type="contains",
        source=door,
        target=window,
    )

    project.add_relationship(first)
    project.add_relationship(second)
    project.add_relationship(third)

    assert project.relationships_by_type(
        "contains"
    ) == [
        first,
        second,
        third,
    ]


# ----------------------------------------------------------------------
# Project Query Isolation
# ----------------------------------------------------------------------


def test_project_relationship_queries_are_project_scoped():
    project_a, wall_a, door_a, window_a = create_project()
    project_b, wall_b, door_b, window_b = create_project()

    relationship_a = create_relationship(
        id="project-a-wall-door",
        relationship_type="contains",
        source=wall_a,
        target=door_a,
    )

    relationship_b = create_relationship(
        id="project-b-wall-door",
        relationship_type="contains",
        source=wall_b,
        target=door_b,
    )

    project_a.add_relationship(
        relationship_a
    )

    project_b.add_relationship(
        relationship_b
    )

    assert project_a.relationships_for_resource(
        wall_a
    ) == [
        relationship_a
    ]

    assert project_b.relationships_for_resource(
        wall_b
    ) == [
        relationship_b
    ]

    assert project_a.relationships_by_type(
        "contains"
    ) == [
        relationship_a
    ]

    assert project_b.relationships_by_type(
        "contains"
    ) == [
        relationship_b
    ]


# ----------------------------------------------------------------------
# Removal Updates Queries
# ----------------------------------------------------------------------


def test_project_relationship_queries_update_after_removal():
    project, wall, door, window = create_project()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.relationships_for_resource(
        wall
    ) == [
        relationship
    ]

    removed = project.remove_relationship(
        relationship
    )

    assert removed is relationship

    assert project.relationships_for_resource(
        wall
    ) == []

    assert project.relationships_for_resource(
        door
    ) == []

    assert project.relationships_by_type(
        "contains"
    ) == []


# ----------------------------------------------------------------------
# Foreign Resource Validation
# ----------------------------------------------------------------------


def test_project_relationship_query_rejects_foreign_resource():
    project, wall, door, window = create_project()

    foreign_project, foreign_wall, foreign_door, foreign_window = (
        create_project()
    )

    try:
        project.relationships_for_resource(
            foreign_wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign Resource to raise ValueError"
        )


def test_project_outgoing_query_rejects_foreign_resource():
    project, wall, door, window = create_project()

    foreign_project, foreign_wall, foreign_door, foreign_window = (
        create_project()
    )

    try:
        project.outgoing_relationships(
            foreign_wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign Resource to raise ValueError"
        )


def test_project_incoming_query_rejects_foreign_resource():
    project, wall, door, window = create_project()

    foreign_project, foreign_wall, foreign_door, foreign_window = (
        create_project()
    )

    try:
        project.incoming_relationships(
            foreign_wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign Resource to raise ValueError"
        )


# ----------------------------------------------------------------------
# Invalid Relationship Type
# ----------------------------------------------------------------------


def test_project_relationships_by_type_rejects_empty_type():
    project, wall, door, window = create_project()

    try:
        project.relationships_by_type("")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty relationship type "
            "to raise ValueError"
        )


def test_project_relationships_by_type_rejects_whitespace_type():
    project, wall, door, window = create_project()

    try:
        project.relationships_by_type("   ")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace relationship type "
            "to raise ValueError"
        )
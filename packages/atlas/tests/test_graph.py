from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship


def create_resource(
    name: str,
    classification_id: str = "wall",
) -> AtlasResource:
    classification = AtlasClassification(
        id=classification_id,
        name=classification_id.title(),
    )

    return AtlasResource(
        classification=classification,
        name=name,
    )


def create_relationship(
    first: AtlasResource,
    second: AtlasResource,
    relationship_type: str = "connects",
) -> AtlasRelationship:
    return AtlasRelationship(
        id=f"{first.aid}-{second.aid}-{relationship_type}",
        relationship_type=relationship_type,
        source=first.aid,
        target=second.aid,
    )


# ----------------------------------------------------------------------
# Basic Graph
# ----------------------------------------------------------------------


def test_graph_starts_empty():
    graph = AtlasResourceGraph()

    assert graph.count == 0
    assert len(graph) == 0


def test_add_relationship():
    graph = AtlasResourceGraph()

    first = create_resource("North Wall")
    second = create_resource("Main Door")

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    assert graph.count == 1
    assert len(graph) == 1


def test_contains_relationship():
    graph = AtlasResourceGraph()

    first = create_resource("North Wall")
    second = create_resource("Main Door")

    relationship = create_relationship(first, second)

    assert not graph.contains(relationship)

    graph.add_relationship(relationship)

    assert graph.contains(relationship)


def test_duplicate_relationship_is_rejected():
    graph = AtlasResourceGraph()

    first = create_resource("North Wall")
    second = create_resource("Main Door")

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    try:
        graph.add_relationship(relationship)
    except ValueError as error:
        assert "already exists" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for duplicate relationship"
        )


# ----------------------------------------------------------------------
# Relationship Lookup
# ----------------------------------------------------------------------


def test_get_between_resources():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")
    door = create_resource("Main Door")

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    result = graph.get_between(wall, door)

    assert result == [relationship]


def test_get_between_unrelated_resources_returns_empty():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    result = graph.get_between(wall, window)

    assert result == []


def test_for_resource_returns_all_relationships():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    wall_door = create_relationship(wall, door)
    wall_window = create_relationship(wall, window)

    graph.add_relationship(wall_door)
    graph.add_relationship(wall_window)

    result = graph.for_resource(wall)

    assert result == [wall_door, wall_window]


def test_for_resource_returns_empty_when_no_relationships():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")

    assert graph.for_resource(wall) == []


def test_relationships_are_scoped_to_resource_ids():
    graph = AtlasResourceGraph()

    first_wall = create_resource("North Wall")
    second_wall = create_resource("South Wall")
    door = create_resource("Main Door")

    first_relationship = create_relationship(
        first_wall,
        door,
    )

    second_relationship = create_relationship(
        second_wall,
        door,
    )

    graph.add_relationship(first_relationship)
    graph.add_relationship(second_relationship)

    assert graph.for_resource(first_wall) == [
        first_relationship
    ]

    assert graph.for_resource(second_wall) == [
        second_relationship
    ]


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_remove_relationship():
    graph = AtlasResourceGraph()

    first = create_resource("North Wall")
    second = create_resource("Main Door")

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    removed = graph.remove_relationship(relationship)

    assert removed is relationship
    assert graph.count == 0
    assert not graph.contains(relationship)


def test_remove_missing_relationship():
    graph = AtlasResourceGraph()

    first = create_resource("North Wall")
    second = create_resource("Main Door")

    relationship = create_relationship(first, second)

    assert graph.remove_relationship(relationship) is None


# ----------------------------------------------------------------------
# Iteration / Clearing
# ----------------------------------------------------------------------


def test_graph_iteration():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    wall_door = create_relationship(wall, door)
    wall_window = create_relationship(wall, window)

    graph.add_relationship(wall_door)
    graph.add_relationship(wall_window)

    relationships = list(graph)

    assert relationships == [
        wall_door,
        wall_window,
    ]


def test_clear_graph():
    graph = AtlasResourceGraph()

    wall = create_resource("North Wall")
    door = create_resource("Main Door")

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    assert graph.count == 1

    graph.clear()

    assert graph.count == 0
    assert list(graph) == []
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
) -> AtlasRelationship:
    return AtlasRelationship(
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

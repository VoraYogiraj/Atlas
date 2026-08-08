from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


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


def create_registry(
    *resources: AtlasResource,
) -> AtlasResourceRegistry:
    registry = AtlasResourceRegistry()

    for resource in resources:
        registry.register(resource)

    return registry


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


def create_graph(
    *resources: AtlasResource,
) -> AtlasResourceGraph:
    registry = create_registry(*resources)
    return AtlasResourceGraph(registry)


# ----------------------------------------------------------------------
# Basic Graph
# ----------------------------------------------------------------------


def test_graph_starts_empty():
    graph = create_graph()

    assert graph.count == 0
    assert len(graph) == 0


def test_graph_exposes_resource_registry():
    resource = create_resource("North Wall")

    graph = create_graph(resource)

    assert graph.resources.contains(resource.aid)


def test_add_relationship():
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    assert graph.count == 1
    assert len(graph) == 1


def test_contains_relationship():
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

    relationship = create_relationship(first, second)

    assert not graph.contains(relationship)

    graph.add_relationship(relationship)

    assert graph.contains(relationship)


def test_duplicate_relationship_is_rejected():
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

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
# Project Graph Integrity
# ----------------------------------------------------------------------


def test_relationship_requires_registered_source_resource():
    registered = create_resource("North Wall")
    foreign = create_resource("Foreign Door")

    graph = create_graph(registered)

    relationship = create_relationship(
        foreign,
        registered,
    )

    try:
        graph.add_relationship(relationship)
    except ValueError as error:
        assert "source Resource is not registered" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for unregistered source Resource"
        )


def test_relationship_requires_registered_target_resource():
    registered = create_resource("North Wall")
    foreign = create_resource("Foreign Door")

    graph = create_graph(registered)

    relationship = create_relationship(
        registered,
        foreign,
    )

    try:
        graph.add_relationship(relationship)
    except ValueError as error:
        assert "target Resource is not registered" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for unregistered target Resource"
        )


def test_foreign_project_relationship_is_rejected():
    first = create_resource("Project A Wall")
    second = create_resource("Project B Door")

    project_a_graph = create_graph(first)
    project_b_graph = create_graph(second)

    relationship = create_relationship(first, second)

    try:
        project_a_graph.add_relationship(relationship)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for cross-project relationship"
        )

    assert project_b_graph.count == 0


def test_relationship_between_project_resources_is_allowed():
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    assert graph.contains(relationship)
    assert graph.count == 1


def test_graph_resources_are_project_scoped():
    first = create_resource("Project A Wall")
    second = create_resource("Project B Wall")

    first_graph = create_graph(first)
    second_graph = create_graph(second)

    assert first_graph.resources.contains(first.aid)
    assert not first_graph.resources.contains(second.aid)

    assert second_graph.resources.contains(second.aid)
    assert not second_graph.resources.contains(first.aid)


# ----------------------------------------------------------------------
# Relationship Lookup
# ----------------------------------------------------------------------


def test_get_between_resources():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")

    graph = create_graph(wall, door)

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    result = graph.get_between(wall, door)

    assert result == [relationship]


def test_get_between_resources_is_direction_insensitive():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")

    graph = create_graph(wall, door)

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    assert graph.get_between(wall, door) == [relationship]
    assert graph.get_between(door, wall) == [relationship]


def test_get_between_unrelated_resources_returns_empty():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    graph = create_graph(wall, door, window)

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    result = graph.get_between(wall, window)

    assert result == []


def test_get_between_rejects_foreign_resource():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    foreign = create_resource("Foreign Window")

    graph = create_graph(wall, door)

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    try:
        graph.get_between(wall, foreign)
    except ValueError as error:
        assert "does not belong to graph registry" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for foreign Resource"
        )


def test_for_resource_returns_all_relationships():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    graph = create_graph(wall, door, window)

    wall_door = create_relationship(wall, door)
    wall_window = create_relationship(wall, window)

    graph.add_relationship(wall_door)
    graph.add_relationship(wall_window)

    result = graph.for_resource(wall)

    assert result == [wall_door, wall_window]


def test_for_resource_returns_empty_when_no_relationships():
    wall = create_resource("North Wall")

    graph = create_graph(wall)

    assert graph.for_resource(wall) == []


def test_for_resource_rejects_foreign_resource():
    wall = create_resource("North Wall")
    foreign = create_resource("Foreign Wall")

    graph = create_graph(wall)

    try:
        graph.for_resource(foreign)
    except ValueError as error:
        assert "does not belong to graph registry" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for foreign Resource"
        )


def test_relationships_are_scoped_to_resource_ids():
    first_wall = create_resource("North Wall")
    second_wall = create_resource("South Wall")
    door = create_resource("Main Door")

    graph = create_graph(
        first_wall,
        second_wall,
        door,
    )

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
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

    relationship = create_relationship(first, second)

    graph.add_relationship(relationship)

    removed = graph.remove_relationship(relationship)

    assert removed is relationship
    assert graph.count == 0
    assert not graph.contains(relationship)


def test_remove_missing_relationship():
    first = create_resource("North Wall")
    second = create_resource("Main Door")

    graph = create_graph(first, second)

    relationship = create_relationship(first, second)

    assert graph.remove_relationship(relationship) is None


# ----------------------------------------------------------------------
# Iteration / Clearing
# ----------------------------------------------------------------------


def test_graph_iteration():
    wall = create_resource("North Wall")
    door = create_resource("Main Door")
    window = create_resource("Living Room Window")

    graph = create_graph(wall, door, window)

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
    wall = create_resource("North Wall")
    door = create_resource("Main Door")

    graph = create_graph(wall, door)

    relationship = create_relationship(wall, door)

    graph.add_relationship(relationship)

    assert graph.count == 1

    graph.clear()

    assert graph.count == 0
    assert list(graph) == []
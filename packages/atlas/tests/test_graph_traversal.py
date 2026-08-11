from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.graph.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


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


def create_graph():
    classification = create_classification()

    registry = AtlasResourceRegistry()

    building = create_resource(
        classification,
        "Building",
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

    room = create_resource(
        classification,
        "Room",
    )

    registry.register(building)
    registry.register(wall)
    registry.register(door)
    registry.register(window)
    registry.register(room)

    graph = AtlasResourceGraph(
        registry
    )

    return (
        graph,
        building,
        wall,
        door,
        window,
        room,
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
# Neighbors
# ----------------------------------------------------------------------


def test_graph_neighbors_returns_directly_connected_resources():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    building_wall = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    wall_door = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(building_wall)
    graph.add_relationship(wall_door)

    assert graph.neighbors(wall) == [
        door,
        building,
    ]


def test_graph_neighbors_include_incoming_and_outgoing_connections():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    outgoing = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    incoming = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    graph.add_relationship(outgoing)
    graph.add_relationship(incoming)

    assert graph.neighbors(wall) == [
        door,
        building,
    ]


def test_graph_neighbors_returns_empty_for_isolated_resource():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    assert graph.neighbors(room) == []


def test_graph_neighbors_do_not_duplicate_a_resource():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="wall-door-contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    second = create_relationship(
        id="wall-door-connects",
        relationship_type="connects",
        source=wall,
        target=door,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.neighbors(wall) == [
        door,
    ]


def test_graph_neighbors_preserve_deterministic_order():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    second = create_relationship(
        id="wall-window",
        relationship_type="contains",
        source=wall,
        target=window,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.neighbors(wall) == [
        door,
        window,
    ]


# ----------------------------------------------------------------------
# Connected
# ----------------------------------------------------------------------


def test_graph_connected_returns_true_for_direct_connection():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.connected(
        wall,
        door,
    ) is True


def test_graph_connected_is_direction_independent():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.connected(
        building,
        wall,
    ) is True

    assert graph.connected(
        wall,
        building,
    ) is True


def test_graph_connected_returns_false_for_unconnected_resources():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.connected(
        building,
        window,
    ) is False


def test_graph_connected_does_not_treat_transitive_connection_as_direct():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.connected(
        building,
        door,
    ) is False


def test_graph_connected_resource_to_itself():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    assert graph.connected(
        wall,
        wall,
    ) is False


# ----------------------------------------------------------------------
# Traverse
# ----------------------------------------------------------------------


def test_graph_traverse_includes_starting_resource():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    result = graph.traverse(
        wall
    )

    assert result == [
        wall,
    ]


def test_graph_traverse_follows_multiple_hops():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    third = create_relationship(
        id="door-window",
        relationship_type="connects",
        source=door,
        target=window,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    assert graph.traverse(
        building
    ) == [
        building,
        wall,
        door,
        window,
    ]


def test_graph_traverse_is_direction_independent():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="wall-building",
        relationship_type="contained-by",
        source=wall,
        target=building,
    )

    second = create_relationship(
        id="door-wall",
        relationship_type="contained-by",
        source=door,
        target=wall,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.traverse(
        building
    ) == [
        building,
        wall,
        door,
    ]


def test_graph_traverse_does_not_duplicate_resources_in_cycles():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    third = create_relationship(
        id="door-building",
        relationship_type="connects",
        source=door,
        target=building,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    result = graph.traverse(
        building
    )

    assert result == [
        building,
        wall,
        door,
    ]

    assert len(result) == 3


def test_graph_traverse_is_breadth_first():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="building-door",
        relationship_type="contains",
        source=building,
        target=door,
    )

    third = create_relationship(
        id="wall-window",
        relationship_type="contains",
        source=wall,
        target=window,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    assert graph.traverse(
        building
    ) == [
        building,
        wall,
        door,
        window,
    ]


# ----------------------------------------------------------------------
# Depth-Limited Traversal
# ----------------------------------------------------------------------


def test_graph_traverse_depth_zero_returns_start_only():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.traverse(
        building,
        max_depth=0,
    ) == [
        building,
    ]


def test_graph_traverse_depth_one_returns_direct_neighbors():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.traverse(
        building,
        max_depth=1,
    ) == [
        building,
        wall,
    ]


def test_graph_traverse_depth_two_returns_two_hops():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    third = create_relationship(
        id="door-window",
        relationship_type="connects",
        source=door,
        target=window,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    assert graph.traverse(
        building,
        max_depth=2,
    ) == [
        building,
        wall,
        door,
    ]


def test_graph_traverse_negative_depth_is_rejected():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    try:
        graph.traverse(
            building,
            max_depth=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected negative max_depth to raise ValueError"
        )


# ----------------------------------------------------------------------
# Reachability
# ----------------------------------------------------------------------


def test_graph_reachable_returns_true_for_direct_connection():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.reachable(
        building,
        wall,
    ) is True


def test_graph_reachable_returns_true_for_multi_hop_connection():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    first = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    second = create_relationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    third = create_relationship(
        id="door-window",
        relationship_type="connects",
        source=door,
        target=window,
    )

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    assert graph.reachable(
        building,
        window,
    ) is True


def test_graph_reachable_is_direction_independent():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="wall-building",
        relationship_type="contained-by",
        source=wall,
        target=building,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.reachable(
        building,
        wall,
    ) is True

    assert graph.reachable(
        wall,
        building,
    ) is True


def test_graph_reachable_returns_false_when_no_path_exists():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    relationship = create_relationship(
        id="building-wall",
        relationship_type="contains",
        source=building,
        target=wall,
    )

    graph.add_relationship(
        relationship
    )

    assert graph.reachable(
        building,
        window,
    ) is False


def test_graph_reachable_returns_true_for_same_resource():
    (
        graph,
        building,
        wall,
        door,
        window,
        room,
    ) = create_graph()

    assert graph.reachable(
        wall,
        wall,
    ) is True


# ----------------------------------------------------------------------
# Foreign Resource Validation
# ----------------------------------------------------------------------


def test_graph_neighbors_rejects_foreign_resource():
    graph, building, wall, door, window, room = create_graph()

    (
        foreign_graph,
        foreign_building,
        foreign_wall,
        foreign_door,
        foreign_window,
        foreign_room,
    ) = create_graph()

    try:
        graph.neighbors(
            foreign_wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign Resource to raise ValueError"
        )


def test_graph_traverse_rejects_foreign_resource():
    graph, building, wall, door, window, room = create_graph()

    (
        foreign_graph,
        foreign_building,
        foreign_wall,
        foreign_door,
        foreign_window,
        foreign_room,
    ) = create_graph()

    try:
        graph.traverse(
            foreign_wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign Resource to raise ValueError"
        )


def test_graph_reachable_rejects_foreign_source():
    graph, building, wall, door, window, room = create_graph()

    (
        foreign_graph,
        foreign_building,
        foreign_wall,
        foreign_door,
        foreign_window,
        foreign_room,
    ) = create_graph()

    try:
        graph.reachable(
            foreign_wall,
            wall,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign source to raise ValueError"
        )


def test_graph_reachable_rejects_foreign_target():
    graph, building, wall, door, window, room = create_graph()

    (
        foreign_graph,
        foreign_building,
        foreign_wall,
        foreign_door,
        foreign_window,
        foreign_room,
    ) = create_graph()

    try:
        graph.reachable(
            wall,
            foreign_wall,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected foreign target to raise ValueError"
        )
from atlas.core.resource import AtlasResource
from atlas.graph.graph import AtlasResourceGraph
from atlas.relationships.relationship import AtlasRelationship
from atlas.resource_registry import AtlasResourceRegistry


def make_resource(
    registry: AtlasResourceRegistry,
    name: str,
) -> AtlasResource:
    resource = AtlasResource(
        name=name,
        classification="building",
    )
    registry.register(resource)
    return resource


def make_relationship(
    source: AtlasResource,
    target: AtlasResource,
    relationship_type: str = "contains",
) -> AtlasRelationship:
    return AtlasRelationship(
        source=source.aid,
        target=target.aid,
        relationship_type=relationship_type,
    )


# ---------------------------------------------------------------------------
# Graph creation
# ---------------------------------------------------------------------------


def test_graph_starts_empty() -> None:
    registry = AtlasResourceRegistry()
    graph = AtlasResourceGraph(registry)

    assert len(graph) == 0
    assert graph.count == 0
    assert list(graph) == []


def test_graph_exposes_registry() -> None:
    registry = AtlasResourceRegistry()
    graph = AtlasResourceGraph(registry)

    assert graph.resources is registry


# ---------------------------------------------------------------------------
# Relationship registration
# ---------------------------------------------------------------------------


def test_add_relationship() -> None:
    registry = AtlasResourceRegistry()

    source = make_resource(registry, "Building")
    target = make_resource(registry, "Floor")

    relationship = make_relationship(source, target)

    graph = AtlasResourceGraph(registry)
    graph.add_relationship(relationship)

    assert len(graph) == 1
    assert graph.count == 1
    assert graph.contains(relationship)
    assert list(graph) == [relationship]


def test_duplicate_relationship_is_rejected() -> None:
    registry = AtlasResourceRegistry()

    source = make_resource(registry, "Building")
    target = make_resource(registry, "Floor")

    relationship = make_relationship(source, target)

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(relationship)

    try:
        graph.add_relationship(relationship)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Duplicate relationship should raise ValueError"
        )


def test_relationship_source_must_be_registered() -> None:
    registry = AtlasResourceRegistry()

    source = AtlasResource(
        name="Unregistered",
        classification="building",
    )
    target = make_resource(registry, "Floor")

    relationship = make_relationship(source, target)

    graph = AtlasResourceGraph(registry)

    try:
        graph.add_relationship(relationship)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered source should raise ValueError"
        )


def test_relationship_target_must_be_registered() -> None:
    registry = AtlasResourceRegistry()

    source = make_resource(registry, "Building")
    target = AtlasResource(
        name="Unregistered",
        classification="floor",
    )

    relationship = make_relationship(source, target)

    graph = AtlasResourceGraph(registry)

    try:
        graph.add_relationship(relationship)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered target should raise ValueError"
        )


# ---------------------------------------------------------------------------
# Relationship lookup
# ---------------------------------------------------------------------------


def test_get_between_returns_relationship() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    relationship = make_relationship(building, floor)

    graph = AtlasResourceGraph(registry)
    graph.add_relationship(relationship)

    result = graph.get_between(building, floor)

    assert result == [relationship]


def test_get_between_is_direction_independent() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    relationship = make_relationship(building, floor)

    graph = AtlasResourceGraph(registry)
    graph.add_relationship(relationship)

    assert graph.get_between(floor, building) == [relationship]


def test_get_between_returns_empty_when_not_connected() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    relationship = make_relationship(building, floor)

    graph = AtlasResourceGraph(registry)
    graph.add_relationship(relationship)

    assert graph.get_between(building, room) == []


def test_for_resource_returns_all_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    relationship_one = make_relationship(
        building,
        floor,
        "contains",
    )

    relationship_two = make_relationship(
        room,
        building,
        "belongs_to",
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(relationship_one)
    graph.add_relationship(relationship_two)

    assert graph.for_resource(building) == [
        relationship_one,
        relationship_two,
    ]


def test_for_resource_returns_empty_when_no_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")

    graph = AtlasResourceGraph(registry)

    assert graph.for_resource(building) == []


# ---------------------------------------------------------------------------
# Neighbors
# ---------------------------------------------------------------------------


def test_neighbors_returns_directly_connected_resources() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    graph.add_relationship(
        make_relationship(building, room)
    )

    assert graph.neighbors(building) == [
        floor,
        room,
    ]


def test_neighbors_works_for_incoming_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(
            floor,
            building,
            "belongs_to",
        )
    )

    assert graph.neighbors(building) == [floor]


def test_neighbors_returns_empty_for_isolated_resource() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")

    graph = AtlasResourceGraph(registry)

    assert graph.neighbors(building) == []


def test_neighbors_returns_registered_resource_objects() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    neighbors = graph.neighbors(building)

    assert neighbors[0] is floor


def test_neighbors_rejects_unregistered_resource() -> None:
    registry = AtlasResourceRegistry()

    building = AtlasResource(
        name="Unregistered",
        classification="building",
    )

    graph = AtlasResourceGraph(registry)

    try:
        graph.neighbors(building)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered resource should raise ValueError"
        )


# ---------------------------------------------------------------------------
# Relationship type queries
# ---------------------------------------------------------------------------


def test_relationships_of_type_returns_matching_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    contains_floor = make_relationship(
        building,
        floor,
        "contains",
    )

    contains_room = make_relationship(
        building,
        room,
        "contains",
    )

    belongs_to = make_relationship(
        room,
        building,
        "belongs_to",
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(contains_floor)
    graph.add_relationship(contains_room)
    graph.add_relationship(belongs_to)

    assert graph.relationships_of_type(
        building,
        "contains",
    ) == [
        contains_floor,
        contains_room,
    ]


def test_relationships_of_type_includes_incoming_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    room = make_resource(registry, "Room")

    relationship = make_relationship(
        room,
        building,
        "belongs_to",
    )

    graph = AtlasResourceGraph(registry)
    graph.add_relationship(relationship)

    assert graph.relationships_of_type(
        building,
        "belongs_to",
    ) == [relationship]


def test_relationships_of_type_excludes_other_types() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    contains = make_relationship(
        building,
        floor,
        "contains",
    )

    belongs_to = make_relationship(
        floor,
        building,
        "belongs_to",
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(contains)
    graph.add_relationship(belongs_to)

    assert graph.relationships_of_type(
        building,
        "contains",
    ) == [contains]


def test_relationships_of_type_returns_empty_for_unknown_type() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(
            building,
            floor,
            "contains",
        )
    )

    assert graph.relationships_of_type(
        building,
        "connects_to",
    ) == []


def test_relationships_of_type_rejects_unregistered_resource() -> None:
    registry = AtlasResourceRegistry()

    building = AtlasResource(
        name="Unregistered",
        classification="building",
    )

    graph = AtlasResourceGraph(registry)

    try:
        graph.relationships_of_type(
            building,
            "contains",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered resource should raise ValueError"
        )


# ---------------------------------------------------------------------------
# Connected
# ---------------------------------------------------------------------------


def test_connected_returns_true_for_direct_relationship() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    assert graph.connected(building, floor) is True
    assert graph.connected(floor, building) is True


def test_connected_returns_false_for_unrelated_resources() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    assert graph.connected(building, room) is False


def test_connected_is_direct_only() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    graph.add_relationship(
        make_relationship(floor, room)
    )

    assert graph.connected(building, floor) is True
    assert graph.connected(floor, room) is True
    assert graph.connected(building, room) is False


# ---------------------------------------------------------------------------
# Registry integrity
# ---------------------------------------------------------------------------


def test_get_between_rejects_unregistered_first_resource() -> None:
    registry = AtlasResourceRegistry()

    registered = make_resource(registry, "Registered")

    unregistered = AtlasResource(
        name="Unregistered",
        classification="room",
    )

    graph = AtlasResourceGraph(registry)

    try:
        graph.get_between(
            registered,
            unregistered,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered resource should raise ValueError"
        )


def test_get_between_rejects_unregistered_second_resource() -> None:
    registry = AtlasResourceRegistry()

    registered = make_resource(registry, "Registered")

    unregistered = AtlasResource(
        name="Unregistered",
        classification="room",
    )

    graph = AtlasResourceGraph(registry)

    try:
        graph.get_between(
            unregistered,
            registered,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unregistered resource should raise ValueError"
        )


# ---------------------------------------------------------------------------
# Removal
# ---------------------------------------------------------------------------


def test_remove_relationship() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    relationship = make_relationship(
        building,
        floor,
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(relationship)

    removed = graph.remove_relationship(relationship)

    assert removed is relationship
    assert len(graph) == 0
    assert graph.count == 0
    assert graph.contains(relationship) is False


def test_remove_missing_relationship_returns_none() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    relationship = make_relationship(
        building,
        floor,
    )

    graph = AtlasResourceGraph(registry)

    assert graph.remove_relationship(relationship) is None


def test_remove_relationship_updates_queries() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    relationship = make_relationship(
        building,
        floor,
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(relationship)

    assert graph.connected(building, floor) is True
    assert graph.neighbors(building) == [floor]

    graph.remove_relationship(relationship)

    assert graph.connected(building, floor) is False
    assert graph.neighbors(building) == []
    assert graph.get_between(building, floor) == []


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------


def test_clear_removes_all_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    graph.add_relationship(
        make_relationship(floor, room)
    )

    assert graph.count == 2

    graph.clear()

    assert graph.count == 0
    assert len(graph) == 0
    assert list(graph) == []


def test_clear_does_not_remove_resources_from_registry() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    graph.clear()

    assert registry.contains(building.aid)
    assert registry.contains(floor.aid)
    assert registry.get(building.aid) is building
    assert registry.get(floor.aid) is floor


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------


def test_graph_iteration_preserves_relationship_order() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    first = make_relationship(
        building,
        floor,
        "contains",
    )

    second = make_relationship(
        floor,
        room,
        "contains",
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert list(graph) == [
        first,
        second,
    ]


# ---------------------------------------------------------------------------
# Multiple relationships
# ---------------------------------------------------------------------------


def test_multiple_relationships_between_same_resources_are_supported() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    room = make_resource(registry, "Room")

    first = make_relationship(
        building,
        room,
        "contains",
    )

    second = make_relationship(
        building,
        room,
        "references",
    )

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(first)
    graph.add_relationship(second)

    assert graph.count == 2
    assert graph.get_between(
        building,
        room,
    ) == [
        first,
        second,
    ]


def test_neighbors_returns_one_entry_per_relationship() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(
            building,
            room,
            "contains",
        )
    )

    graph.add_relationship(
        make_relationship(
            building,
            room,
            "references",
        )
    )

    assert graph.neighbors(building) == [
        room,
        room,
    ]
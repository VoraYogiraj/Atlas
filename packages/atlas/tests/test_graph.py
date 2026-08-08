from atlas.core.aid import AtlasAID
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

    result = graph.get_between(floor, building)

    assert result == [relationship]


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

    result = graph.for_resource(building)

    assert result == [
        relationship_one,
        relationship_two,
    ]


def test_for_resource_returns_empty_when_no_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")

    graph = AtlasResourceGraph(registry)

    assert graph.for_resource(building) == []


# ---------------------------------------------------------------------------
# Graph queries
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

    neighbors = graph.neighbors(building)

    assert neighbors == [
        floor,
        room,
    ]


def test_neighbors_works_for_incoming_relationships() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    relationship = make_relationship(
        floor,
        building,
        "belongs_to",
    )

    graph.add_relationship(relationship)

    assert graph.neighbors(building) == [floor]


def test_neighbors_does_not_include_unrelated_resources() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")
    room = make_resource(registry, "Room")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    assert graph.neighbors(building) == [floor]
    assert room not in graph.neighbors(building)


def test_neighbors_returns_actual_registered_resource_objects() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor)
    )

    neighbors = graph.neighbors(building)

    assert neighbors[0] is floor


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

    result = graph.relationships_of_type(
        building,
        "contains",
    )

    assert result == [
        contains_floor,
        contains_room,
    ]


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

    result = graph.relationships_of_type(
        building,
        "belongs_to",
    )

    assert result == [belongs_to]


def test_relationships_of_type_returns_empty_for_unknown_type() -> None:
    registry = AtlasResourceRegistry()

    building = make_resource(registry, "Building")
    floor = make_resource(registry, "Floor")

    graph = AtlasResourceGraph(registry)

    graph.add_relationship(
        make_relationship(building, floor, "
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


def create_graph():
    classification = create_classification(
        id="building-element",
        name="Building Element",
    )

    registry = AtlasResourceRegistry()

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

    registry.register(wall)
    registry.register(door)
    registry.register(window)

    graph = AtlasResourceGraph(
        registry
    )

    return graph, wall, door, window


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
# Relationships for Resource
# ----------------------------------------------------------------------


def test_graph_returns_relationships_for_resource():
    graph, wall, door, window = create_graph()

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

    graph.add_relationship(contains)
    graph.add_relationship(supports)

    result = graph.for_resource(wall)

    assert result == [
        contains,
        supports,
    ]


def test_graph_returns_empty_list_for_resource_without_relationships():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    assert graph.for_resource(window) == []


def test_graph_for_resource_includes_incoming_relationships():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    assert graph.for_resource(door) == [
        relationship
    ]


# ----------------------------------------------------------------------
# Outgoing Relationships
# ----------------------------------------------------------------------


def test_graph_returns_outgoing_relationships():
    graph, wall, door, window = create_graph()

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

    graph.add_relationship(contains)
    graph.add_relationship(supports)

    result = graph.outgoing(wall)

    assert result == [
        contains,
        supports,
    ]


def test_graph_outgoing_does_not_include_incoming():
    graph, wall, door, window = create_graph()

    incoming = create_relationship(
        id="door-contained-by-wall",
        relationship_type="contained-by",
        source=door,
        target=wall,
    )

    graph.add_relationship(incoming)

    assert graph.outgoing(wall) == []


def test_graph_outgoing_returns_empty_when_none_exist():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    assert graph.outgoing(door) == []


# ----------------------------------------------------------------------
# Incoming Relationships
# ----------------------------------------------------------------------


def test_graph_returns_incoming_relationships():
    graph, wall, door, window = create_graph()

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

    graph.add_relationship(contains)
    graph.add_relationship(supports)

    result = graph.incoming(wall)

    assert result == [
        supports,
    ]


def test_graph_incoming_does_not_include_outgoing():
    graph, wall, door, window = create_graph()

    outgoing = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(outgoing)

    assert graph.incoming(wall) == []


def test_graph_incoming_returns_empty_when_none_exist():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    assert graph.incoming(window) == []


# ----------------------------------------------------------------------
# Relationship Type
# ----------------------------------------------------------------------


def test_graph_returns_relationships_by_type():
    graph, wall, door, window = create_graph()

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

    graph.add_relationship(contains)
    graph.add_relationship(supports)

    assert graph.for_relationship_type(
        "contains"
    ) == [
        contains
    ]

    assert graph.for_relationship_type(
        "supports"
    ) == [
        supports
    ]


def test_graph_returns_empty_for_unknown_relationship_type():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    assert graph.for_relationship_type(
        "supports"
    ) == []


def test_graph_type_query_preserves_registration_order():
    graph, wall, door, window = create_graph()

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

    graph.add_relationship(first)
    graph.add_relationship(second)
    graph.add_relationship(third)

    assert graph.for_relationship_type(
        "contains"
    ) == [
        first,
        second,
        third,
    ]


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_graph_queries_update_after_relationship_removal():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(relationship)

    graph.remove_relationship(
        relationship
    )

    assert graph.for_resource(wall) == []
    assert graph.for_resource(door) == []

    assert graph.for_relationship_type(
        "contains"
    ) == []


# ----------------------------------------------------------------------
# Identity / Registered Resource
# ----------------------------------------------------------------------


def test_graph_resource_query_uses_registered_resource_id():
    graph, wall, door, window = create_graph()

    relationship = create_relationship(
        id="wall-contains-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    graph.add_relationship(
        relationship
    )

    result = graph.for_resource(
        wall
    )

    assert result == [
        relationship
    ]


# ----------------------------------------------------------------------
# Invalid Input
# ----------------------------------------------------------------------


def test_graph_rejects_empty_relationship_type_query():
    graph, wall, door, window = create_graph()

    try:
        graph.for_relationship_type("")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty relationship type "
            "to raise ValueError"
        )


def test_graph_rejects_whitespace_relationship_type_query():
    graph, wall, door, window = create_graph()

    try:
        graph.for_relationship_type("   ")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace relationship type "
            "to raise ValueError"
        )
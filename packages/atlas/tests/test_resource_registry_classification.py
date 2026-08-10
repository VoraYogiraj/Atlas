from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
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


# ----------------------------------------------------------------------
# Query by Classification
# ----------------------------------------------------------------------


def test_registry_returns_resources_for_classification():
    registry = AtlasResourceRegistry()

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

    registry.register(north_wall)
    registry.register(south_wall)

    result = registry.for_classification(
        "wall"
    )

    assert result == [
        north_wall,
        south_wall,
    ]


def test_registry_returns_empty_list_for_unknown_classification():
    registry = AtlasResourceRegistry()

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    resource = create_resource(
        wall,
        "North Wall",
    )

    registry.register(resource)

    result = registry.for_classification(
        "door"
    )

    assert result == []


def test_registry_does_not_return_resources_of_other_classification():
    registry = AtlasResourceRegistry()

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

    registry.register(north_wall)
    registry.register(entrance_door)

    result = registry.for_classification(
        "wall"
    )

    assert result == [
        north_wall,
    ]


def test_registry_classification_query_uses_classification_id():
    registry = AtlasResourceRegistry()

    registered_classification = create_classification(
        id="wall",
        name="Wall",
    )

    equivalent_classification = create_classification(
        id="wall",
        name="Wall",
    )

    wall = create_resource(
        registered_classification,
        "North Wall",
    )

    registry.register(wall)

    result = registry.for_classification(
        equivalent_classification.id
    )

    assert result == [
        wall,
    ]


# ----------------------------------------------------------------------
# Multiple Resources
# ----------------------------------------------------------------------


def test_registry_returns_all_resources_of_classification():
    registry = AtlasResourceRegistry()

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    resources = [
        create_resource(wall, "North Wall"),
        create_resource(wall, "South Wall"),
        create_resource(wall, "East Wall"),
        create_resource(wall, "West Wall"),
    ]

    for resource in resources:
        registry.register(resource)

    result = registry.for_classification(
        "wall"
    )

    assert result == resources


def test_registry_preserves_registration_order():
    registry = AtlasResourceRegistry()

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

    registry.register(first)
    registry.register(second)
    registry.register(third)

    result = registry.for_classification(
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


def test_registry_classification_query_updates_after_resource_removal():
    registry = AtlasResourceRegistry()

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

    registry.register(north_wall)
    registry.register(south_wall)

    registry.unregister(
        north_wall.aid
    )

    result = registry.for_classification(
        "wall"
    )

    assert result == [
        south_wall,
    ]


def test_registry_classification_query_empty_after_all_resources_removed():
    registry = AtlasResourceRegistry()

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

    registry.register(north_wall)
    registry.register(south_wall)

    registry.unregister(
        north_wall.aid
    )

    registry.unregister(
        south_wall.aid
    )

    assert registry.for_classification(
        "wall"
    ) == []


# ----------------------------------------------------------------------
# Isolation
# ----------------------------------------------------------------------


def test_registry_classification_query_is_registry_scoped():
    first = AtlasResourceRegistry()
    second = AtlasResourceRegistry()

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

    first.register(first_wall)
    second.register(second_wall)

    assert first.for_classification(
        "wall"
    ) == [first_wall]

    assert second.for_classification(
        "wall"
    ) == [second_wall]


# ----------------------------------------------------------------------
# Invalid Input
# ----------------------------------------------------------------------


def test_registry_rejects_empty_classification_id_query():
    registry = AtlasResourceRegistry()

    try:
        registry.for_classification("")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty classification ID "
            "to raise ValueError"
        )


def test_registry_rejects_whitespace_classification_id_query():
    registry = AtlasResourceRegistry()

    try:
        registry.for_classification("   ")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace classification ID "
            "to raise ValueError"
        )
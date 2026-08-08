from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.resource_registry import AtlasResourceRegistry


def create_resource(name: str) -> AtlasResource:
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    return AtlasResource(
        classification=classification,
        name=name,
    )


def test_registry_starts_empty():
    registry = AtlasResourceRegistry()

    assert registry.count == 0
    assert len(registry) == 0


def test_register_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    registry.register(resource)

    assert registry.count == 1
    assert len(registry) == 1


def test_get_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    registry.register(resource)

    result = registry.get(resource.aid)

    assert result is resource


def test_get_missing_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    assert registry.get(resource.aid) is None


def test_require_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    registry.register(resource)

    assert registry.require(resource.aid) is resource


def test_require_missing_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    try:
        registry.require(resource.aid)
    except KeyError as error:
        assert "Resource not found" in str(error)
    else:
        raise AssertionError(
            "Expected KeyError for missing Resource"
        )


def test_contains_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    assert not registry.contains(resource.aid)

    registry.register(resource)

    assert registry.contains(resource.aid)


def test_unregister_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    registry.register(resource)

    removed = registry.unregister(resource.aid)

    assert removed is resource
    assert registry.count == 0
    assert not registry.contains(resource.aid)


def test_unregister_missing_resource():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    assert registry.unregister(resource.aid) is None


def test_duplicate_registration_is_rejected():
    registry = AtlasResourceRegistry()
    resource = create_resource("North Wall")

    registry.register(resource)

    try:
        registry.register(resource)
    except ValueError as error:
        assert "already registered" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for duplicate registration"
        )


def test_registry_iteration():
    registry = AtlasResourceRegistry()

    wall = create_resource("North Wall")
    south_wall = create_resource("South Wall")

    registry.register(wall)
    registry.register(south_wall)

    resources = list(registry)

    assert resources == [wall, south_wall]


def test_clear_registry():
    registry = AtlasResourceRegistry()

    registry.register(create_resource("North Wall"))
    registry.register(create_resource("South Wall"))

    assert registry.count == 2

    registry.clear()

    assert registry.count == 0
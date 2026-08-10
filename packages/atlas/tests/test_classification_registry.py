from atlas.classification.classification import AtlasClassification
from atlas.classification.registry import AtlasClassificationRegistry


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


# ----------------------------------------------------------------------
# Creation
# ----------------------------------------------------------------------


def test_registry_starts_empty():
    registry = AtlasClassificationRegistry()

    assert registry.count == 0


def test_registry_contains_nothing_initially():
    registry = AtlasClassificationRegistry()

    assert not registry.contains("wall")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------


def test_registry_registers_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    assert registry.count == 1
    assert registry.contains("wall")


def test_registry_register_returns_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    result = registry.register(wall)

    assert result is wall


def test_registry_rejects_duplicate_id():
    registry = AtlasClassificationRegistry()

    first = create_classification(
        id="wall",
        name="Wall",
    )

    second = create_classification(
        id="wall",
        name="Different Wall",
    )

    registry.register(first)

    try:
        registry.register(second)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate classification ID "
            "to raise ValueError"
        )


# ----------------------------------------------------------------------
# Lookup
# ----------------------------------------------------------------------


def test_registry_get_returns_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    result = registry.get("wall")

    assert result is wall


def test_registry_get_missing_returns_none():
    registry = AtlasClassificationRegistry()

    assert registry.get("missing") is None


def test_registry_require_returns_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    result = registry.require("wall")

    assert result is wall


def test_registry_require_missing_raises_key_error():
    registry = AtlasClassificationRegistry()

    try:
        registry.require("missing")
    except KeyError:
        pass
    else:
        raise AssertionError(
            "Expected missing classification to raise KeyError"
        )


# ----------------------------------------------------------------------
# Membership
# ----------------------------------------------------------------------


def test_registry_contains_registered_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    assert registry.contains(wall.id)


def test_registry_does_not_contain_unregistered_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    assert not registry.contains(wall.id)


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_registry_remove_returns_classification():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    removed = registry.remove("wall")

    assert removed is wall


def test_registry_remove_decreases_count():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    registry.remove("wall")

    assert registry.count == 0


def test_registry_remove_removes_membership():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    registry.remove("wall")

    assert not registry.contains("wall")


def test_registry_remove_missing_returns_none():
    registry = AtlasClassificationRegistry()

    assert registry.remove("missing") is None


# ----------------------------------------------------------------------
# Collection
# ----------------------------------------------------------------------


def test_registry_can_iterate_classifications():
    registry = AtlasClassificationRegistry()

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    door = create_classification(
        id="door",
        name="Door",
    )

    window = create_classification(
        id="window",
        name="Window",
    )

    registry.register(wall)
    registry.register(door)
    registry.register(window)

    classifications = list(registry)

    assert classifications == [
        wall,
        door,
        window,
    ]


def test_registry_len_matches_count():
    registry = AtlasClassificationRegistry()

    wall = create_classification()

    registry.register(wall)

    assert len(registry) == registry.count
    assert len(registry) == 1


def test_registry_clear():
    registry = AtlasClassificationRegistry()

    wall = create_classification(
        id="wall",
        name="Wall",
    )

    door = create_classification(
        id="door",
        name="Door",
    )

    registry.register(wall)
    registry.register(door)

    registry.clear()

    assert registry.count == 0
    assert not registry.contains("wall")
    assert not registry.contains("door")
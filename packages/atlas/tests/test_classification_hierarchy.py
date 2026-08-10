from atlas.classification.classification import AtlasClassification
from atlas.classification.hierarchy import AtlasClassificationHierarchy


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_root(
    *,
    id: str = "physical",
    name: str = "Physical Resource",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_building(
    parent: AtlasClassification,
) -> AtlasClassification:
    return AtlasClassification(
        id="building",
        name="Building",
        parent=parent,
    )


def create_wall(
    parent: AtlasClassification,
) -> AtlasClassification:
    return AtlasClassification(
        id="wall",
        name="Wall",
        parent=parent,
    )


# ----------------------------------------------------------------------
# Creation
# ----------------------------------------------------------------------


def test_hierarchy_starts_empty():
    hierarchy = AtlasClassificationHierarchy()

    assert hierarchy.count == 0


def test_hierarchy_contains_no_classifications_initially():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()

    assert not hierarchy.contains(root.id)


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------


def test_hierarchy_add_classification():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()

    hierarchy.add(root)

    assert hierarchy.count == 1
    assert hierarchy.contains(root.id)


def test_hierarchy_add_returns_classification():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()

    result = hierarchy.add(root)

    assert result is root


def test_hierarchy_can_add_child_classification():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()
    building = create_building(root)

    hierarchy.add(root)
    hierarchy.add(building)

    assert hierarchy.count == 2
    assert hierarchy.contains(root.id)
    assert hierarchy.contains(building.id)


def test_hierarchy_rejects_duplicate_id():
    hierarchy = AtlasClassificationHierarchy()

    first = AtlasClassification(
        id="wall",
        name="Wall",
    )

    second = AtlasClassification(
        id="wall",
        name="Different Wall",
    )

    hierarchy.add(first)

    try:
        hierarchy.add(second)
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


def test_hierarchy_get_classification():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()

    hierarchy.add(root)

    result = hierarchy.get(root.id)

    assert result is root


def test_hierarchy_get_missing_classification_returns_none():
    hierarchy = AtlasClassificationHierarchy()

    assert hierarchy.get("missing") is None


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_hierarchy_remove_classification():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()

    hierarchy.add(root)

    removed = hierarchy.remove(root.id)

    assert removed is root
    assert hierarchy.count == 0
    assert not hierarchy.contains(root.id)


def test_hierarchy_remove_missing_classification_returns_none():
    hierarchy = AtlasClassificationHierarchy()

    assert hierarchy.remove("missing") is None


# ----------------------------------------------------------------------
# Collection
# ----------------------------------------------------------------------


def test_hierarchy_can_iterate_classifications():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()
    building = create_building(root)
    wall = create_wall(building)

    hierarchy.add(root)
    hierarchy.add(building)
    hierarchy.add(wall)

    classifications = list(hierarchy)

    assert classifications == [
        root,
        building,
        wall,
    ]


def test_hierarchy_clear():
    hierarchy = AtlasClassificationHierarchy()

    root = create_root()
    building = create_building(root)

    hierarchy.add(root)
    hierarchy.add(building)

    hierarchy.clear()

    assert hierarchy.count == 0
    assert not hierarchy.contains(root.id)
    assert not hierarchy.contains(building.id)
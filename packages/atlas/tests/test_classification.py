from dataclasses import FrozenInstanceError

import pytest

from atlas.classification.classification import AtlasClassification


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


def test_classification_creation():
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    assert classification.id == "wall"
    assert classification.name == "Wall"
    assert classification.description == ""
    assert classification.parent is None


def test_classification_description():
    classification = AtlasClassification(
        id="wall",
        name="Wall",
        description="Vertical building enclosure element.",
    )

    assert classification.description == (
        "Vertical building enclosure element."
    )


# ----------------------------------------------------------------------
# Immutability
# ----------------------------------------------------------------------


def test_classification_is_immutable():
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    with pytest.raises(FrozenInstanceError):
        classification.name = "Door"


def test_classification_parent_is_immutable():
    root = create_root()

    classification = AtlasClassification(
        id="building",
        name="Building",
        parent=root,
    )

    with pytest.raises(FrozenInstanceError):
        classification.parent = None


# ----------------------------------------------------------------------
# Root Classification
# ----------------------------------------------------------------------


def test_root_classification_has_no_parent():
    root = create_root()

    assert root.parent is None


def test_root_classification_is_root():
    root = create_root()

    assert root.is_root


def test_root_classification_has_depth_zero():
    root = create_root()

    assert root.depth == 0


def test_root_classification_path_contains_only_itself():
    root = create_root()

    assert root.path == (
        "Physical Resource",
    )


# ----------------------------------------------------------------------
# Child Classification
# ----------------------------------------------------------------------


def test_child_classification_has_parent():
    root = create_root()
    building = create_building(root)

    assert building.parent is root


def test_child_classification_is_not_root():
    root = create_root()
    building = create_building(root)

    assert not building.is_root


def test_child_classification_has_depth_one():
    root = create_root()
    building = create_building(root)

    assert building.depth == 1


def test_child_classification_path_contains_parent():
    root = create_root()
    building = create_building(root)

    assert building.path == (
        "Physical Resource",
        "Building",
    )


# ----------------------------------------------------------------------
# Multi-Level Hierarchy
# ----------------------------------------------------------------------


def test_nested_classification_has_correct_path():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert wall.path == (
        "Physical Resource",
        "Building",
        "Wall",
    )


def test_nested_classification_has_correct_depth():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert wall.depth == 2


# ----------------------------------------------------------------------
# Descendant Relationships
# ----------------------------------------------------------------------


def test_child_is_descendant_of_parent():
    root = create_root()

    building = create_building(root)

    assert building.is_descendant_of(root)


def test_grandchild_is_descendant_of_root():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert wall.is_descendant_of(root)


def test_grandchild_is_descendant_of_direct_parent():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert wall.is_descendant_of(building)


def test_root_is_not_descendant_of_child():
    root = create_root()

    building = create_building(root)

    assert not root.is_descendant_of(building)


def test_classification_is_not_descendant_of_itself():
    root = create_root()

    assert not root.is_descendant_of(root)


# ----------------------------------------------------------------------
# Ancestor Relationships
# ----------------------------------------------------------------------


def test_parent_is_ancestor_of_child():
    root = create_root()

    building = create_building(root)

    assert root.is_ancestor_of(building)


def test_root_is_ancestor_of_grandchild():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert root.is_ancestor_of(wall)


def test_direct_parent_is_ancestor_of_grandchild():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert building.is_ancestor_of(wall)


def test_child_is_not_ancestor_of_parent():
    root = create_root()

    building = create_building(root)

    assert not building.is_ancestor_of(root)


def test_classification_is_not_ancestor_of_itself():
    root = create_root()

    assert not root.is_ancestor_of(root)


# ----------------------------------------------------------------------
# Sibling Relationships
# ----------------------------------------------------------------------


def test_siblings_are_not_descendants_of_each_other():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    door = AtlasClassification(
        id="door",
        name="Door",
        parent=building,
    )

    assert not wall.is_descendant_of(door)
    assert not door.is_descendant_of(wall)


def test_siblings_share_same_parent():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    door = AtlasClassification(
        id="door",
        name="Door",
        parent=building,
    )

    assert wall.parent is door.parent
    assert wall.parent is building


# ----------------------------------------------------------------------
# String Representation
# ----------------------------------------------------------------------


def test_classification_string_representation():
    root = create_root()

    building = create_building(root)

    wall = create_wall(building)

    assert str(wall) == (
        "Physical Resource > Building > Wall"
    )


def test_classification_repr():
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    representation = repr(classification)

    assert "AtlasClassification" in representation
    assert "wall" in representation
    assert "Wall" in representation
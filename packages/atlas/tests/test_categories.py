"""
ENG-025 — Resource Categories

Tests the Resource Category model and its integration
with AtlasResource.
"""

from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_category(
    *,
    id: str = "structural",
    name: str = "Structural",
    description: str = "",
) -> AtlasCategory:
    return AtlasCategory(
        id=id,
        name=name,
        description=description,
    )


def create_resource() -> AtlasResource:
    classification = AtlasClassification(
        id="building-element",
        name="Building Element",
    )

    return AtlasResource(
        classification=classification,
        name="North Wall",
    )


# ----------------------------------------------------------------------
# Category Identity
# ----------------------------------------------------------------------


def test_category_has_id():
    category = create_category()

    assert category.id == "structural"


def test_category_has_name():
    category = create_category()

    assert category.name == "Structural"


def test_category_has_description():
    category = create_category(
        description="Resources participating in the structural system.",
    )

    assert category.description == (
        "Resources participating in the structural system."
    )


def test_category_repr():
    category = create_category()

    representation = repr(category)

    assert "AtlasCategory" in representation
    assert "structural" in representation


# ----------------------------------------------------------------------
# Category Immutability
# ----------------------------------------------------------------------


def test_category_is_immutable():
    category = create_category()

    try:
        category.id = "different"
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError(
            "Category must be immutable"
        )


def test_category_name_is_immutable():
    category = create_category()

    try:
        category.name = "Different"
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError(
            "Category name must be immutable"
        )


def test_category_description_is_immutable():
    category = create_category()

    try:
        category.description = "Different"
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError(
            "Category description must be immutable"
        )


# ----------------------------------------------------------------------
# Resource Category Collection
# ----------------------------------------------------------------------


def test_resource_starts_without_categories():
    resource = create_resource()

    assert resource.categories == []


def test_resource_add_category():
    resource = create_resource()
    category = create_category()

    result = resource.add_category(category)

    assert result is category
    assert resource.categories == [category]


def test_resource_get_category():
    resource = create_resource()
    category = create_category()

    resource.add_category(category)

    assert resource.get_category("structural") is category


def test_resource_has_category():
    resource = create_resource()
    category = create_category()

    resource.add_category(category)

    assert resource.has_category("structural") is True


def test_resource_has_category_returns_false_when_missing():
    resource = create_resource()

    assert resource.has_category("structural") is False


def test_resource_remove_category():
    resource = create_resource()
    category = create_category()

    resource.add_category(category)

    removed = resource.remove_category("structural")

    assert removed is category
    assert resource.categories == []


def test_resource_remove_missing_category_returns_none():
    resource = create_resource()

    assert resource.remove_category("structural") is None


# ----------------------------------------------------------------------
# Multiple Categories
# ----------------------------------------------------------------------


def test_resource_supports_multiple_categories():
    resource = create_resource()

    structural = create_category(
        id="structural",
        name="Structural",
    )

    exterior = create_category(
        id="exterior",
        name="Exterior",
    )

    ground_floor = create_category(
        id="ground-floor",
        name="Ground Floor",
    )

    resource.add_category(structural)
    resource.add_category(exterior)
    resource.add_category(ground_floor)

    assert resource.categories == [
        structural,
        exterior,
        ground_floor,
    ]


def test_resource_categories_preserve_insertion_order():
    resource = create_resource()

    first = create_category(
        id="first",
        name="First",
    )

    second = create_category(
        id="second",
        name="Second",
    )

    third = create_category(
        id="third",
        name="Third",
    )

    resource.add_category(first)
    resource.add_category(second)
    resource.add_category(third)

    assert resource.categories == [
        first,
        second,
        third,
    ]


# ----------------------------------------------------------------------
# Duplicate Categories
# ----------------------------------------------------------------------


def test_resource_rejects_duplicate_category_id():
    resource = create_resource()

    first = create_category(
        id="structural",
        name="Structural",
    )

    second = create_category(
        id="structural",
        name="Different Meaning",
    )

    resource.add_category(first)

    try:
        resource.add_category(second)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate category ID to raise ValueError"
        )


def test_duplicate_category_does_not_replace_existing_category():
    resource = create_resource()

    first = create_category(
        id="structural",
        name="Structural",
    )

    second = create_category(
        id="structural",
        name="Different Meaning",
    )

    resource.add_category(first)

    try:
        resource.add_category(second)
    except ValueError:
        pass

    assert resource.get_category("structural") is first


# ----------------------------------------------------------------------
# Category Sharing
# ----------------------------------------------------------------------


def test_same_category_can_be_shared_by_multiple_resources():
    first_resource = create_resource()
    second_resource = create_resource()

    category = create_category()

    first_resource.add_category(category)
    second_resource.add_category(category)

    assert first_resource.get_category(
        "structural"
    ) is category

    assert second_resource.get_category(
        "structural"
    ) is category


def test_removing_category_from_one_resource_does_not_affect_another():
    first_resource = create_resource()
    second_resource = create_resource()

    category = create_category()

    first_resource.add_category(category)
    second_resource.add_category(category)

    first_resource.remove_category("structural")

    assert first_resource.has_category(
        "structural"
    ) is False

    assert second_resource.has_category(
        "structural"
    ) is True


# ----------------------------------------------------------------------
# Category Collection Isolation
# ----------------------------------------------------------------------


def test_resource_categories_are_resource_scoped():
    first_resource = create_resource()
    second_resource = create_resource()

    category = create_category()

    first_resource.add_category(category)

    assert first_resource.categories == [
        category
    ]

    assert second_resource.categories == []


def test_resource_categories_return_a_copy_of_internal_storage():
    resource = create_resource()
    category = create_category()

    resource.add_category(category)

    categories = resource.categories
    categories.clear()

    assert resource.categories == [
        category
    ]


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------


def test_resource_rejects_non_category_object():
    resource = create_resource()

    try:
        resource.add_category("structural")
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-category object to raise TypeError"
        )


def test_get_category_requires_string_id():
    resource = create_resource()

    try:
        resource.get_category(123)
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string category ID to raise TypeError"
        )


def test_remove_category_requires_string_id():
    resource = create_resource()

    try:
        resource.remove_category(123)
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string category ID to raise TypeError"
        )


def test_has_category_requires_string_id():
    resource = create_resource()

    try:
        resource.has_category(123)
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string category ID to raise TypeError"
        )


# ----------------------------------------------------------------------
# Independence
# ----------------------------------------------------------------------


def test_category_does_not_change_resource_classification():
    resource = create_resource()

    classification = resource.classification

    category = create_category()

    resource.add_category(category)

    assert resource.classification is classification


def test_category_does_not_change_semantic_tags():
    resource = create_resource()

    category = create_category()

    resource.add_category(category)

    assert resource.tags == []


def test_removing_category_does_not_remove_semantic_tags():
    resource = create_resource()

    category = create_category()

    resource.add_category(category)

    resource.remove_category("structural")

    assert resource.tags == []
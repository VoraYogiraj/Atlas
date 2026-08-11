from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.semantic_tags.tag import AtlasSemanticTag


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification() -> AtlasClassification:
    return AtlasClassification(
        id="building-element",
        name="Building Element",
    )


def create_resource() -> AtlasResource:
    return AtlasResource(
        classification=create_classification(),
        name="North Wall",
    )


def create_tag(
    *,
    id: str = "load-bearing",
    name: str = "Load Bearing",
    description: str = "",
) -> AtlasSemanticTag:
    return AtlasSemanticTag(
        id=id,
        name=name,
        description=description,
    )


# ----------------------------------------------------------------------
# Semantic Tag Identity
# ----------------------------------------------------------------------


def test_semantic_tag_has_id():
    tag = create_tag()

    assert tag.id == "load-bearing"


def test_semantic_tag_has_name():
    tag = create_tag()

    assert tag.name == "Load Bearing"


def test_semantic_tag_has_description():
    tag = create_tag(
        description="Structural load-bearing element."
    )

    assert tag.description == (
        "Structural load-bearing element."
    )


def test_semantic_tag_repr():
    tag = create_tag()

    representation = repr(tag)

    assert "AtlasSemanticTag" in representation
    assert "load-bearing" in representation


# ----------------------------------------------------------------------
# Semantic Tag Immutability
# ----------------------------------------------------------------------


def test_semantic_tag_is_immutable():
    tag = create_tag()

    try:
        tag.id = "different"
    except (
        AttributeError,
        TypeError,
        Exception,
    ):
        pass
    else:
        raise AssertionError(
            "Semantic tags must be immutable"
        )


# ----------------------------------------------------------------------
# Resource Tag Collection
# ----------------------------------------------------------------------


def test_resource_starts_without_tags():
    resource = create_resource()

    assert resource.tags == []


def test_resource_add_tag():
    resource = create_resource()
    tag = create_tag()

    result = resource.add_tag(
        tag
    )

    assert result is tag
    assert resource.tags == [
        tag
    ]


def test_resource_get_tag():
    resource = create_resource()
    tag = create_tag()

    resource.add_tag(
        tag
    )

    assert resource.get_tag(
        "load-bearing"
    ) is tag


def test_resource_has_tag():
    resource = create_resource()
    tag = create_tag()

    resource.add_tag(
        tag
    )

    assert resource.has_tag(
        "load-bearing"
    ) is True


def test_resource_has_tag_returns_false_when_missing():
    resource = create_resource()

    assert resource.has_tag(
        "load-bearing"
    ) is False


def test_resource_remove_tag():
    resource = create_resource()
    tag = create_tag()

    resource.add_tag(
        tag
    )

    removed = resource.remove_tag(
        "load-bearing"
    )

    assert removed is tag
    assert resource.tags == []


def test_resource_remove_missing_tag_returns_none():
    resource = create_resource()

    assert resource.remove_tag(
        "load-bearing"
    ) is None


# ----------------------------------------------------------------------
# Multiple Tags
# ----------------------------------------------------------------------


def test_resource_supports_multiple_tags():
    resource = create_resource()

    structural = create_tag(
        id="structural",
        name="Structural",
    )

    load_bearing = create_tag(
        id="load-bearing",
        name="Load Bearing",
    )

    exterior = create_tag(
        id="exterior",
        name="Exterior",
    )

    resource.add_tag(
        structural
    )

    resource.add_tag(
        load_bearing
    )

    resource.add_tag(
        exterior
    )

    assert resource.tags == [
        structural,
        load_bearing,
        exterior,
    ]


def test_resource_tags_preserve_insertion_order():
    resource = create_resource()

    first = create_tag(
        id="first",
        name="First",
    )

    second = create_tag(
        id="second",
        name="Second",
    )

    third = create_tag(
        id="third",
        name="Third",
    )

    resource.add_tag(first)
    resource.add_tag(second)
    resource.add_tag(third)

    assert resource.tags == [
        first,
        second,
        third,
    ]


# ----------------------------------------------------------------------
# Duplicate Tags
# ----------------------------------------------------------------------


def test_resource_rejects_duplicate_tag_id():
    resource = create_resource()

    first = create_tag(
        id="structural",
        name="Structural",
    )

    second = create_tag(
        id="structural",
        name="Different Meaning",
    )

    resource.add_tag(
        first
    )

    try:
        resource.add_tag(
            second
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate tag ID to raise ValueError"
        )


def test_resource_duplicate_tag_does_not_replace_existing_tag():
    resource = create_resource()

    first = create_tag(
        id="structural",
        name="Structural",
    )

    second = create_tag(
        id="structural",
        name="Different Meaning",
    )

    resource.add_tag(
        first
    )

    try:
        resource.add_tag(
            second
        )
    except ValueError:
        pass

    assert resource.get_tag(
        "structural"
    ) is first


# ----------------------------------------------------------------------
# Tag Independence
# ----------------------------------------------------------------------


def test_same_tag_can_be_shared_by_multiple_resources():
    first_resource = create_resource()
    second_resource = create_resource()

    tag = create_tag()

    first_resource.add_tag(
        tag
    )

    second_resource.add_tag(
        tag
    )

    assert first_resource.get_tag(
        "load-bearing"
    ) is tag

    assert second_resource.get_tag(
        "load-bearing"
    ) is tag


def test_removing_tag_from_one_resource_does_not_affect_another():
    first_resource = create_resource()
    second_resource = create_resource()

    tag = create_tag()

    first_resource.add_tag(
        tag
    )

    second_resource.add_tag(
        tag
    )

    first_resource.remove_tag(
        "load-bearing"
    )

    assert first_resource.has_tag(
        "load-bearing"
    ) is False

    assert second_resource.has_tag(
        "load-bearing"
    ) is True


# ----------------------------------------------------------------------
# Tag Collection Isolation
# ----------------------------------------------------------------------


def test_resource_tags_are_resource_scoped():
    first_resource = create_resource()
    second_resource = create_resource()

    tag = create_tag()

    first_resource.add_tag(
        tag
    )

    assert first_resource.tags == [
        tag
    ]

    assert second_resource.tags == []


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------


def test_resource_rejects_non_tag_object():
    resource = create_resource()

    try:
        resource.add_tag(
            "load-bearing"
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-tag object to raise TypeError"
        )


def test_get_tag_requires_string_id():
    resource = create_resource()

    try:
        resource.get_tag(
            123
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string tag ID to raise TypeError"
        )


def test_remove_tag_requires_string_id():
    resource = create_resource()

    try:
        resource.remove_tag(
            123
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string tag ID to raise TypeError"
        )


def test_has_tag_requires_string_id():
    resource = create_resource()

    try:
        resource.has_tag(
            123
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected non-string tag ID to raise TypeError"
        )
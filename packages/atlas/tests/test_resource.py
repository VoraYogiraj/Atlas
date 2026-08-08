from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.properties.property import AtlasProperty


def create_resource() -> AtlasResource:
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    return AtlasResource(
        classification=classification,
        name="North Wall",
    )


def test_resource_has_id():
    resource = create_resource()

    assert resource.aid is not None


def test_resource_properties():
    resource = create_resource()

    height = AtlasProperty(
        id="height",
        name="Height",
        value=3000,
        data_type="integer",
        unit="mm",
    )

    resource.set_property(height)

    assert resource.get_property("height") == height
    assert resource.get_property("height").value == 3000


def test_remove_property():
    resource = create_resource()

    height = AtlasProperty(
        id="height",
        name="Height",
        value=3000,
        data_type="integer",
        unit="mm",
    )

    resource.set_property(height)

    removed = resource.remove_property("height")

    assert removed == height
    assert resource.get_property("height") is None


def test_resource_name():
    resource = create_resource()

    assert resource.name == "North Wall"


def test_resource_classification():
    resource = create_resource()

    assert resource.classification.name == "Wall"


def test_resource_lifecycle():
    resource = create_resource()

    assert resource.lifecycle is AtlasLifecycle.CREATED


def test_resource_activation():
    resource = create_resource()

    resource.activate()

    assert resource.lifecycle is AtlasLifecycle.ACTIVE


def test_resource_archiving():
    resource = create_resource()

    resource.activate()
    resource.archive()

    assert resource.lifecycle is AtlasLifecycle.ARCHIVED


def test_resource_deletion():
    resource = create_resource()

    resource.activate()
    resource.delete()

    assert resource.lifecycle is AtlasLifecycle.DELETED


def test_invalid_lifecycle_transition():
    resource = create_resource()

    try:
        resource.delete()
    except ValueError as error:
        assert "created -> deleted" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for invalid lifecycle transition"
        )


def test_deleted_resource_cannot_transition():
    resource = create_resource()

    resource.activate()
    resource.delete()

    try:
        resource.activate()
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when transitioning a deleted Resource"
        )
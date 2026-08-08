from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
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

    assert resource.lifecycle == "created"
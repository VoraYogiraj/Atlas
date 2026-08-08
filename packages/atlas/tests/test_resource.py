from atlas.core.resource import AtlasResource


def test_resource_has_id():
    resource = AtlasResource(classification="Wall")

    assert resource.aid is not None


def test_resource_properties():
    resource = AtlasResource(classification="Wall")

    resource.set_property("height", 3000)

    assert resource.get_property("height") == 3000


def test_resource_name():
    resource = AtlasResource(
        classification="Wall",
        name="North Wall",
    )

    assert resource.name == "North Wall"


def test_resource_classification():
    resource = AtlasResource(classification="Wall")

    assert resource.classification == "Wall"


def test_resource_lifecycle():
    resource = AtlasResource(classification="Wall")

    assert resource.lifecycle == "created"
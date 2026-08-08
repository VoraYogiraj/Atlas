from atlas.properties.property import AtlasProperty


def test_property_creation():
    prop = AtlasProperty(
        id="height",
        name="Height",
        value=3000,
        data_type="integer",
        unit="mm",
    )

    assert prop.name == "Height"
    assert prop.value == 3000
    assert prop.unit == "mm"


def test_property_has_value():
    prop = AtlasProperty(
        id="height",
        name="Height",
        value=3000,
        data_type="integer",
    )

    assert prop.has_value


def test_property_without_value():
    prop = AtlasProperty(
        id="height",
        name="Height",
        value=None,
        data_type="integer",
    )

    assert not prop.has_value
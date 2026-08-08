from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.relationships.relationship import AtlasRelationship


def create_resource(name: str) -> AtlasResource:
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    return AtlasResource(
        classification=classification,
        name=name,
    )


def test_relationship_creation():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.source == wall
    assert relationship.target == door


def test_self_reference():
    wall = create_resource("Wall")

    relationship = AtlasRelationship(
        id="self",
        relationship_type="references",
        source=wall,
        target=wall,
    )

    assert relationship.is_self_reference


def test_involves():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.involves(wall)
    assert relationship.involves(door)
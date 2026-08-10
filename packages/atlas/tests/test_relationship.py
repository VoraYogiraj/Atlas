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


# ----------------------------------------------------------------------
# Relationship Creation
# ----------------------------------------------------------------------


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


# ----------------------------------------------------------------------
# Relationship Validation
# ----------------------------------------------------------------------


def test_relationship_rejects_empty_id():
    wall = create_resource("Wall")
    door = create_resource("Door")

    try:
        AtlasRelationship(
            id="",
            relationship_type="contains",
            source=wall,
            target=door,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty relationship id to raise ValueError"
        )


def test_relationship_rejects_whitespace_id():
    wall = create_resource("Wall")
    door = create_resource("Door")

    try:
        AtlasRelationship(
            id="   ",
            relationship_type="contains",
            source=wall,
            target=door,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace relationship id to raise ValueError"
        )


def test_relationship_rejects_empty_type():
    wall = create_resource("Wall")
    door = create_resource("Door")

    try:
        AtlasRelationship(
            id="contains",
            relationship_type="",
            source=wall,
            target=door,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty relationship type to raise ValueError"
        )


def test_relationship_rejects_whitespace_type():
    wall = create_resource("Wall")
    door = create_resource("Door")

    try:
        AtlasRelationship(
            id="contains",
            relationship_type="   ",
            source=wall,
            target=door,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected whitespace relationship type to raise ValueError"
        )


# ----------------------------------------------------------------------
# Relationship Direction
# ----------------------------------------------------------------------


def test_relationship_is_directed():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.source is wall
    assert relationship.target is door


def test_relationship_does_not_reverse_source_and_target():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.source is not door
    assert relationship.target is not wall


def test_relationship_description_defaults_to_empty():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.description == ""


def test_relationship_description_is_preserved():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
        description="Wall contains the door opening.",
    )

    assert relationship.description == (
        "Wall contains the door opening."
    )


# ----------------------------------------------------------------------
# Relationship Direction Semantics
# ----------------------------------------------------------------------


def test_relationship_is_from_source():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.is_from(wall)
    assert not relationship.is_from(door)


def test_relationship_is_to_target():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.is_to(door)
    assert not relationship.is_to(wall)


def test_relationship_connects_source_to_target():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.connects(
        wall,
        door,
    )


def test_relationship_does_not_connect_target_to_source():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert not relationship.connects(
        door,
        wall,
    )


def test_relationship_connects_uses_resource_identity():
    wall = create_resource("Wall")
    door = create_resource("Door")

    relationship = AtlasRelationship(
        id="contains",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    assert relationship.connects(
        wall,
        door,
    )


def test_relationship_direction_does_not_change_involves():
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
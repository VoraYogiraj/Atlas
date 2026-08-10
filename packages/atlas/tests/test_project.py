from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.project import AtlasProject
from atlas.resource_registry import AtlasResourceRegistry
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


def add_project_resource(
    project: AtlasProject,
    resource: AtlasResource,
) -> AtlasResource:
    """
    Register a Resource's Classification with the Project when needed,
    then add the Resource through the Project API.

    This keeps the older project tests compatible with the new
    project-scoped classification integrity contract.
    """
    classification_id = resource.classification.id

    if not project.classifications.contains(classification_id):
        project.add_classification(resource.classification)

    return project.add_resource(resource)



# ----------------------------------------------------------------------
# Project Identity
# ----------------------------------------------------------------------


def test_project_has_id():
    project = AtlasProject(name="Residential Project")

    assert project.aid is not None


def test_project_name():
    project = AtlasProject(name="Residential Project")

    assert project.name == "Residential Project"


def test_project_name_can_be_changed():
    project = AtlasProject(name="Residential Project")

    project.name = "Commercial Project"

    assert project.name == "Commercial Project"


def test_project_rejects_empty_name():
    try:
        AtlasProject(name="")
    except ValueError as error:
        assert "name cannot be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for empty Project name"
        )


def test_project_rejects_whitespace_name():
    try:
        AtlasProject(name="   ")
    except ValueError as error:
        assert "name cannot be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Project name"
        )


# ----------------------------------------------------------------------
# Project Metadata
# ----------------------------------------------------------------------


def test_project_metadata():
    project = AtlasProject(name="Residential Project")

    project.metadata["location"] = "Surat"
    project.metadata["units"] = "mm"

    assert project.metadata["location"] == "Surat"
    assert project.metadata["units"] == "mm"


# ----------------------------------------------------------------------
# Resource Registry
# ----------------------------------------------------------------------


def test_project_owns_resource_registry():
    project = AtlasProject(name="Residential Project")

    assert isinstance(project.resources, AtlasResourceRegistry)
    assert project.resources.count == 0


def test_project_registry_is_stable():
    project = AtlasProject(name="Residential Project")

    registry = project.resources

    assert project.resources is registry


def test_projects_have_independent_registries():
    first = AtlasProject(name="Project A")
    second = AtlasProject(name="Project B")

    assert first.resources is not second.resources


# ----------------------------------------------------------------------
# Project → Registry → Resource Integration
# ----------------------------------------------------------------------


def test_project_can_register_resource():
    project = AtlasProject(name="Residential Project")
    resource = create_resource("North Wall")

    project.resources.register(resource)

    assert project.resources.count == 1
    assert project.resources.contains(resource.aid)


def test_project_can_retrieve_registered_resource():
    project = AtlasProject(name="Residential Project")
    resource = create_resource("North Wall")

    project.resources.register(resource)

    result = project.resources.get(resource.aid)

    assert result is resource


def test_project_can_require_registered_resource():
    project = AtlasProject(name="Residential Project")
    resource = create_resource("North Wall")

    project.resources.register(resource)

    result = project.resources.require(resource.aid)

    assert result is resource


def test_project_can_unregister_resource():
    project = AtlasProject(name="Residential Project")
    resource = create_resource("North Wall")

    project.resources.register(resource)

    removed = project.resources.unregister(resource.aid)

    assert removed is resource
    assert project.resources.count == 0
    assert not project.resources.contains(resource.aid)


def test_resources_are_isolated_between_projects():
    first = AtlasProject(name="Project A")
    second = AtlasProject(name="Project B")

    resource = create_resource("North Wall")

    first.resources.register(resource)

    assert first.resources.contains(resource.aid)
    assert not second.resources.contains(resource.aid)


def test_project_resource_count():
    project = AtlasProject(name="Residential Project")

    wall = create_resource("North Wall")
    south_wall = create_resource("South Wall")
    east_wall = create_resource("East Wall")

    project.resources.register(wall)
    project.resources.register(south_wall)
    project.resources.register(east_wall)

    assert project.resources.count == 3


def test_project_can_iterate_resources():
    project = AtlasProject(name="Residential Project")

    wall = create_resource("North Wall")
    south_wall = create_resource("South Wall")

    project.resources.register(wall)
    project.resources.register(south_wall)

    resources = list(project.resources)

    assert resources == [wall, south_wall]


# ----------------------------------------------------------------------
# Resource Graph
# ----------------------------------------------------------------------


def test_project_owns_resource_graph():
    project = AtlasProject(name="Residential Project")

    assert isinstance(project.graph, AtlasResourceGraph)
    assert project.graph.count == 0


def test_project_graph_is_stable():
    project = AtlasProject(name="Residential Project")

    graph = project.graph

    assert project.graph is graph


def test_projects_have_independent_graphs():
    first = AtlasProject(name="Project A")
    second = AtlasProject(name="Project B")

    assert first.graph is not second.graph


def test_project_resource_registry_and_graph_are_independent():
    project = AtlasProject(name="Residential Project")

    assert project.resources is not project.graph


# ----------------------------------------------------------------------
# Project → Graph → Resource Registry Integration
# ----------------------------------------------------------------------


def test_project_graph_uses_project_resource_registry():
    project = AtlasProject(
        name="Residential Project"
    )

    assert project.graph.resources is project.resources


def test_project_graph_can_query_project_resources():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource("North Wall")

    project.resources.register(wall)

    assert project.graph.resources.contains(
        wall.aid
    )


def test_project_graph_rejects_resource_from_another_project():
    first = AtlasProject(
        name="Project A"
    )

    second = AtlasProject(
        name="Project B"
    )

    wall = create_resource("North Wall")

    first.resources.register(wall)

    try:
        second.graph.neighbors(wall)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Project graph should reject resources "
            "belonging to another project"
        )


def test_project_graph_rejects_relationship_between_foreign_resources():
    first = AtlasProject(
        name="Project A"
    )

    second = AtlasProject(
        name="Project B"
    )

    first_wall = create_resource("North Wall")
    second_wall = create_resource("South Wall")

    first.resources.register(first_wall)
    second.resources.register(second_wall)

    relationship = AtlasRelationship(
        id="cross-project-relationship",
        relationship_type="connects",
        source=first_wall,
        target=second_wall,
    )

    try:
        first.graph.add_relationship(
            relationship
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Cross-project relationship should be rejected"
        )


# ----------------------------------------------------------------------
# Project Resource API
# ----------------------------------------------------------------------


def test_project_add_resource_registers_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    add_project_resource(project, wall)

    assert project.resources.contains(
        wall.aid
    )

    assert project.resources.count == 1


def test_project_add_resource_returns_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    result = add_project_resource(
        project,
        wall,
    )

    assert result is wall


def test_project_remove_resource_removes_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    add_project_resource(
        project,
        wall,
    )

    removed = project.remove_resource(
        wall
    )

    assert removed is wall

    assert not project.resources.contains(
        wall.aid
    )

    assert project.resources.count == 0


def test_project_remove_missing_resource_returns_none():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    assert project.remove_resource(
        wall
    ) is None


def test_project_add_resource_rejects_duplicate_resource():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    add_project_resource(
        project,
        wall,
    )

    try:
        project.add_resource(
            wall
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate Resource registration "
            "to raise ValueError"
        )


def test_project_resources_remain_owned_by_registry():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    result = add_project_resource(
        project,
        wall,
    )

    assert result is wall

    assert project.resources.get(
        wall.aid
    ) is wall


# ----------------------------------------------------------------------
# Project Relationship API
# ----------------------------------------------------------------------


def test_project_add_relationship_adds_to_graph():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    project.add_relationship(
        relationship
    )

    assert project.graph.contains(
        relationship
    )

    assert project.graph.count == 1


def test_project_add_relationship_returns_relationship():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    result = project.add_relationship(
        relationship
    )

    assert result is relationship


def test_project_add_relationship_rejects_duplicate():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    project.add_relationship(
        relationship
    )

    try:
        project.add_relationship(
            relationship
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate Relationship "
            "to raise ValueError"
        )


def test_project_add_relationship_rejects_foreign_source():
    first = AtlasProject(
        name="Project A"
    )

    second = AtlasProject(
        name="Project B"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    first.add_classification(
        wall.classification
    )

    second.add_classification(
        room.classification
    )

    first.add_resource(
        wall
    )

    second.add_resource(
        room
    )

    relationship = AtlasRelationship(
        id="cross-project-source",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    try:
        first.add_relationship(
            relationship
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected cross-project source "
            "to raise ValueError"
        )


def test_project_add_relationship_rejects_foreign_target():
    first = AtlasProject(
        name="Project A"
    )

    second = AtlasProject(
        name="Project B"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    first.add_classification(
        wall.classification
    )

    second.add_classification(
        room.classification
    )

    first.add_resource(
        wall
    )

    second.add_resource(
        room
    )

    relationship = AtlasRelationship(
        id="cross-project-target",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    try:
        first.add_relationship(
            relationship
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected cross-project target "
            "to raise ValueError"
        )


def test_project_remove_relationship_removes_from_graph():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    project.add_relationship(
        relationship
    )

    removed = project.remove_relationship(
        relationship
    )

    assert removed is relationship

    assert not project.graph.contains(
        relationship
    )

    assert project.graph.count == 0


def test_project_remove_missing_relationship_returns_none():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="missing-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    assert project.remove_relationship(
        relationship
    ) is None


def test_project_relationship_does_not_change_resource_count():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    project.add_relationship(
        relationship
    )

    assert project.resources.count == 2

    project.remove_relationship(
        relationship
    )

    assert project.resources.count == 2


def test_project_relationship_preserves_resource_ownership():
    project = AtlasProject(
        name="Residential Project"
    )

    wall = create_resource(
        "North Wall"
    )

    room = create_resource(
        "Living Room"
    )

    add_project_resource(project, wall)
    add_project_resource(project, room)

    relationship = AtlasRelationship(
        id="wall-room-relationship",
        relationship_type="bounds",
        source=wall,
        target=room,
    )

    project.add_relationship(
        relationship
    )

    assert project.resources.get(
        wall.aid
    ) is wall

    assert project.resources.get(
        room.aid
    ) is room


# ----------------------------------------------------------------------
# Representation
# ----------------------------------------------------------------------


def test_project_repr():
    project = AtlasProject(name="Residential Project")

    representation = repr(project)

    assert "AtlasProject" in representation
    assert "Residential Project" in representation
    assert "resources=0" in representation
    assert "relationships=0" in representation
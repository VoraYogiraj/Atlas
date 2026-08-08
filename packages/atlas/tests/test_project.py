from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.graph import AtlasResourceGraph
from atlas.project import AtlasProject
from atlas.resource_registry import AtlasResourceRegistry


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
# Representation
# ----------------------------------------------------------------------


def test_project_repr():
    project = AtlasProject(name="Residential Project")

    representation = repr(project)

    assert "AtlasProject" in representation
    assert "Residential Project" in representation
    assert "resources=0" in representation
    assert "relationships=0" in representation
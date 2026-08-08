from atlas.project import AtlasProject
from atlas.resource_registry import AtlasResourceRegistry


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


def test_project_metadata():
    project = AtlasProject(name="Residential Project")

    project.metadata["location"] = "Surat"
    project.metadata["units"] = "mm"

    assert project.metadata["location"] == "Surat"
    assert project.metadata["units"] == "mm"


def test_project_owns_resource_registry():
    project = AtlasProject(name="Residential Project")

    assert isinstance(project.resources, AtlasResourceRegistry)
    assert project.resources.count == 0


def test_project_registry_is_stable():
    project = AtlasProject(name="Residential Project")

    registry = project.resources

    assert project.resources is registry
    assert project.resources is registry


def test_projects_have_independent_registries():
    first = AtlasProject(name="Project A")
    second = AtlasProject(name="Project B")

    assert first.resources is not second.resources


def test_project_repr():
    project = AtlasProject(name="Residential Project")

    representation = repr(project)

    assert "AtlasProject" in representation
    assert "Residential Project" in representation
    assert "resources=0" in representation
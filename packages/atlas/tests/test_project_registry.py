from atlas.project import AtlasProject
from atlas.project_registry import AtlasProjectRegistry


def create_project(name: str) -> AtlasProject:
    return AtlasProject(name=name)


def test_registry_starts_empty():
    registry = AtlasProjectRegistry()

    assert registry.count == 0
    assert len(registry) == 0


def test_register_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    registry.register(project)

    assert registry.count == 1
    assert len(registry) == 1


def test_get_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    registry.register(project)

    result = registry.get(project.aid)

    assert result is project


def test_get_missing_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    assert registry.get(project.aid) is None


def test_require_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    registry.register(project)

    result = registry.require(project.aid)

    assert result is project


def test_require_missing_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    try:
        registry.require(project.aid)
    except KeyError as error:
        assert "Project not found" in str(error)
    else:
        raise AssertionError(
            "Expected KeyError for missing Project"
        )


def test_contains_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    assert not registry.contains(project.aid)

    registry.register(project)

    assert registry.contains(project.aid)


def test_unregister_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    registry.register(project)

    removed = registry.unregister(project.aid)

    assert removed is project
    assert registry.count == 0
    assert not registry.contains(project.aid)


def test_unregister_missing_project():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    assert registry.unregister(project.aid) is None


def test_duplicate_registration_is_rejected():
    registry = AtlasProjectRegistry()
    project = create_project("Residential Project")

    registry.register(project)

    try:
        registry.register(project)
    except ValueError as error:
        assert "already registered" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for duplicate registration"
        )


def test_registry_iteration():
    registry = AtlasProjectRegistry()

    first = create_project("Project A")
    second = create_project("Project B")

    registry.register(first)
    registry.register(second)

    projects = list(registry)

    assert projects == [first, second]


def test_clear_registry():
    registry = AtlasProjectRegistry()

    registry.register(create_project("Project A"))
    registry.register(create_project("Project B"))

    assert registry.count == 2

    registry.clear()

    assert registry.count == 0
# ----------------------------------------------------------------------
# Project → Resource integration
# ----------------------------------------------------------------------


def test_registered_project_can_manage_resources():
    registry = AtlasProjectRegistry()

    project = create_project("Residential Project")

    registry.register(project)

    assert registry.get(project.aid) is project
    assert project.resources.count == 0


def test_registered_project_resource_registry_is_independent():
    first = create_project("Project A")
    second = create_project("Project B")

    registry = AtlasProjectRegistry()

    registry.register(first)
    registry.register(second)

    assert registry.get(first.aid) is first
    assert registry.get(second.aid) is second
    assert first.resources is not second.resources


def test_registered_projects_keep_resource_spaces_isolated():
    from atlas.classification.classification import AtlasClassification
    from atlas.core.resource import AtlasResource

    registry = AtlasProjectRegistry()

    first = create_project("Project A")
    second = create_project("Project B")

    registry.register(first)
    registry.register(second)

    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    resource = AtlasResource(
        classification=classification,
        name="North Wall",
    )

    first.resources.register(resource)

    assert first.resources.contains(resource.aid)
    assert not second.resources.contains(resource.aid)


def test_project_registry_preserves_project_resource_hierarchy():
    from atlas.classification.classification import AtlasClassification
    from atlas.core.resource import AtlasResource

    registry = AtlasProjectRegistry()

    project = create_project("Residential Project")
    registry.register(project)

    classification = AtlasClassification(
        id="door",
        name="Door",
    )

    resource = AtlasResource(
        classification=classification,
        name="Main Door",
    )

    project.resources.register(resource)

    registered_project = registry.require(project.aid)
    registered_resource = registered_project.resources.require(
        resource.aid
    )

    assert registered_project is project
    assert registered_resource is resource


def test_unregistering_project_does_not_destroy_project_resources():
    from atlas.classification.classification import AtlasClassification
    from atlas.core.resource import AtlasResource

    registry = AtlasProjectRegistry()

    project = create_project("Residential Project")
    registry.register(project)

    classification = AtlasClassification(
        id="window",
        name="Window",
    )

    resource = AtlasResource(
        classification=classification,
        name="Living Room Window",
    )

    project.resources.register(resource)

    removed = registry.unregister(project.aid)

    assert removed is project
    assert project.resources.contains(resource.aid)
    assert project.resources.get(resource.aid) is resource
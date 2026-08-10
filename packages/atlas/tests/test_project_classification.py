from atlas.classification.classification import AtlasClassification
from atlas.project.project import AtlasProject


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_root() -> AtlasClassification:
    return AtlasClassification(
        id="physical",
        name="Physical Resource",
    )


def create_building(
    parent: AtlasClassification,
) -> AtlasClassification:
    return AtlasClassification(
        id="building",
        name="Building",
        parent=parent,
    )


# ----------------------------------------------------------------------
# Classification Registry
# ----------------------------------------------------------------------


def test_project_owns_classification_registry():
    project = AtlasProject(name="Test Project")

    assert project.classifications is not None


def test_project_classification_registry_is_stable():
    project = AtlasProject(name="Test Project")

    first = project.classifications
    second = project.classifications

    assert first is second


def test_projects_have_independent_classification_registries():
    first = AtlasProject(name="First")
    second = AtlasProject(name="Second")

    assert first.classifications is not second.classifications


def test_project_can_register_classification():
    project = AtlasProject(name="Test Project")

    root = create_root()

    result = project.add_classification(root)

    assert result is root
    assert project.classifications.contains(root.id)


def test_project_can_retrieve_classification():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    assert project.classifications.get(root.id) is root


def test_project_can_require_classification():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    assert project.classifications.require(root.id) is root


def test_project_can_remove_classification():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    removed = project.remove_classification(root.id)

    assert removed is root
    assert not project.classifications.contains(root.id)


def test_project_add_classification_rejects_duplicate():
    project = AtlasProject(name="Test Project")

    first = create_root()

    project.add_classification(first)

    duplicate = AtlasClassification(
        id="physical",
        name="Different Physical Resource",
    )

    try:
        project.add_classification(duplicate)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate classification "
            "to raise ValueError"
        )


# ----------------------------------------------------------------------
# Classification Hierarchy
# ----------------------------------------------------------------------


def test_project_owns_classification_hierarchy():
    project = AtlasProject(name="Test Project")

    assert project.classification_hierarchy is not None


def test_project_classification_hierarchy_is_stable():
    project = AtlasProject(name="Test Project")

    first = project.classification_hierarchy
    second = project.classification_hierarchy

    assert first is second


def test_projects_have_independent_classification_hierarchies():
    first = AtlasProject(name="First")
    second = AtlasProject(name="Second")

    assert (
        first.classification_hierarchy
        is not second.classification_hierarchy
    )


def test_project_add_root_classification_updates_hierarchy():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    assert project.classification_hierarchy.contains(root.id)


def test_project_add_child_classification_requires_parent():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    project.add_classification(root)
    project.add_classification(building)

    assert (
        project.classification_hierarchy.get(building.id)
        is building
    )


def test_project_classification_hierarchy_can_query_children():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    project.add_classification(root)
    project.add_classification(building)

    assert project.classification_hierarchy.children(root) == [
        building
    ]


def test_project_classification_hierarchy_can_query_parent():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    project.add_classification(root)
    project.add_classification(building)

    assert (
        project.classification_hierarchy.parent(building)
        is root
    )


def test_project_classification_hierarchy_rejects_unregistered_parent():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    try:
        project.add_classification(building)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unregistered classification parent "
            "to raise ValueError"
        )


# ----------------------------------------------------------------------
# Registry / Hierarchy Consistency
# ----------------------------------------------------------------------


def test_project_classification_registration_updates_both_contexts():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    assert project.classifications.get(root.id) is root
    assert project.classification_hierarchy.get(root.id) is root


def test_project_classification_count_matches():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    project.add_classification(root)
    project.add_classification(building)

    assert project.classifications.count == 2
    assert project.classification_hierarchy.count == 2


def test_project_remove_classification_updates_both_contexts():
    project = AtlasProject(name="Test Project")

    root = create_root()

    project.add_classification(root)

    removed = project.remove_classification(root.id)

    assert removed is root
    assert not project.classifications.contains(root.id)
    assert not project.classification_hierarchy.contains(root.id)


def test_project_cannot_remove_classification_with_children():
    project = AtlasProject(name="Test Project")

    root = create_root()
    building = create_building(root)

    project.add_classification(root)
    project.add_classification(building)

    try:
        project.remove_classification(root.id)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected parent classification with "
            "children to raise ValueError"
        )


def test_project_classification_spaces_are_isolated():
    first = AtlasProject(name="First")
    second = AtlasProject(name="Second")

    root = create_root()

    first.add_classification(root)

    assert first.classifications.contains(root.id)
    assert first.classification_hierarchy.contains(root.id)

    assert not second.classifications.contains(root.id)
    assert not second.classification_hierarchy.contains(root.id)
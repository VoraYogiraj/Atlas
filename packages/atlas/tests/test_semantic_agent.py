"""
ENG-032 — Semantic Agent

Tests the Atlas Semantic Agent contract.

The Semantic Agent:

    - inspects Resource Classification
    - inspects Classification paths
    - lists Semantic Tags
    - gets Semantic Tags
    - checks Semantic Tag membership
    - adds/removes Semantic Tags
    - lists Categories
    - gets Categories
    - checks Category membership
    - adds/removes Categories
    - produces a deterministic semantic context
    - preserves Project boundaries
    - does not infer semantic meaning
"""

import pytest

from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.categories.category import AtlasCategory
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.semantic_tags.tag import AtlasSemanticTag
from atlas.semantic_agent.semantic_agent import AtlasSemanticAgent


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_project(
    *,
    name: str = "Semantic Test Project",
) -> AtlasProject:
    return AtlasProject(name=name)


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
    parent: AtlasClassification | None = None,
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
        parent=parent,
    )


def register_classification(
    project: AtlasProject,
    classification: AtlasClassification,
) -> AtlasClassification:
    project.add_classification(
        classification
    )
    return classification


def create_resource(
    classification: AtlasClassification,
    *,
    name: str = "North Wall",
) -> AtlasResource:
    return AtlasResource(
        classification=classification,
        name=name,
    )


def create_tag(
    *,
    id: str = "structural",
    name: str = "Structural",
    description: str = "Structural engineering element",
) -> AtlasSemanticTag:
    return AtlasSemanticTag(
        id=id,
        name=name,
        description=description,
    )


def create_category(
    *,
    id: str = "envelope",
    name: str = "Building Envelope",
    description: str = "Building envelope resources",
) -> AtlasCategory:
    return AtlasCategory(
        id=id,
        name=name,
        description=description,
    )


def create_context(
    project: AtlasProject | None = None,
    *,
    metadata: dict | None = None,
) -> AtlasAgentContext:
    return AtlasAgentContext(
        project=project,
        metadata=dict(
            metadata or {}
        ),
    )


def create_request(
    *,
    request_id: str = "request-001",
    action: str = "get_classification",
    project: AtlasProject | None = None,
    metadata: dict | None = None,
) -> AtlasAgentRequest:
    return AtlasAgentRequest(
        id=request_id,
        action=action,
        context=create_context(
            project,
            metadata=metadata,
        ),
    )


def create_agent() -> AtlasSemanticAgent:
    return AtlasSemanticAgent()


def prepare_resource(
    *,
    project: AtlasProject | None = None,
    classification: AtlasClassification | None = None,
    resource_name: str = "North Wall",
) -> tuple[
    AtlasProject,
    AtlasClassification,
    AtlasResource,
]:
    project = project or create_project()

    classification = (
        classification
        or create_classification()
    )

    if (
        project.get_classification(
            classification.id
        )
        is None
    ):
        project.add_classification(
            classification
        )

    resource = create_resource(
        classification,
        name=resource_name,
    )

    project.add_resource(
        resource
    )

    return (
        project,
        classification,
        resource,
    )


# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------


def test_semantic_agent_has_default_id():
    agent = create_agent()

    assert agent.id == "semantic-agent"


def test_semantic_agent_has_default_name():
    agent = create_agent()

    assert agent.name == "Semantic Agent"


def test_semantic_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


# ----------------------------------------------------------------------
# Project / Resource Context
# ----------------------------------------------------------------------


def test_semantic_agent_requires_project_context():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=None,
            metadata={},
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_semantic_agent_requires_resource_metadata():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=project,
            metadata={},
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_semantic_agent_requires_atlas_resource_metadata():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=project,
            metadata={
                "resource": "not-a-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_semantic_agent_requires_resource_belonging_to_project():
    first_project = create_project(
        name="Project A",
    )

    second_project = create_project(
        name="Project B",
    )

    classification = register_classification(
        first_project,
        create_classification(),
    )

    resource = create_resource(
        classification,
        name="Project A Wall",
    )

    first_project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=second_project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Classification
# ----------------------------------------------------------------------


def test_semantic_agent_get_classification():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is classification


def test_semantic_agent_get_classification_preserves_identity():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    original_id = classification.id

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.output.id == original_id


def test_semantic_agent_get_classification_does_not_modify_resource():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    original_classification = resource.classification

    agent = create_agent()

    agent.execute(
        create_request(
            action="get_classification",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert resource.classification is original_classification


# ----------------------------------------------------------------------
# Classification Hierarchy
# ----------------------------------------------------------------------


def test_semantic_agent_get_classification_path_for_root():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification_path",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == (
        "Wall",
    )


def test_semantic_agent_get_classification_path_for_nested_classification():
    project = create_project()

    physical = register_classification(
        project,
        create_classification(
            id="physical",
            name="Physical Resource",
        ),
    )

    building_element = register_classification(
        project,
        create_classification(
            id="building-element",
            name="Building Element",
            parent=physical,
        ),
    )

    wall = register_classification(
        project,
        create_classification(
            id="wall",
            name="Wall",
            parent=building_element,
        ),
    )

    resource = create_resource(
        wall,
        name="North Wall",
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_classification_path",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == (
        "Physical Resource",
        "Building Element",
        "Wall",
    )


# ----------------------------------------------------------------------
# Semantic Tags
# ----------------------------------------------------------------------


def test_semantic_agent_list_semantic_tags_empty():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_semantic_tags",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


def test_semantic_agent_list_semantic_tags():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    structural = create_tag(
        id="structural",
        name="Structural",
    )

    exterior = create_tag(
        id="exterior",
        name="Exterior",
    )

    resource.add_semantic_tag(
        structural
    )

    resource.add_semantic_tag(
        exterior
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_semantic_tags",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        structural,
        exterior,
    ]


def test_semantic_agent_list_semantic_tags_returns_new_list():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    structural = create_tag()

    resource.add_semantic_tag(
        structural
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_semantic_tags",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    result.output.clear()

    assert resource.tags == [
        structural
    ]


def test_semantic_agent_get_semantic_tag():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    resource.add_semantic_tag(
        tag
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "structural",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is tag


def test_semantic_agent_get_missing_semantic_tag_returns_none():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "missing",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


def test_semantic_agent_has_semantic_tag_true():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    resource.add_semantic_tag(
        tag
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="has_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "structural",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_semantic_agent_has_semantic_tag_false():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="has_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "structural",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


def test_semantic_agent_add_semantic_tag():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag": tag,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is tag
    assert resource.get_semantic_tag(
        "structural"
    ) is tag


def test_semantic_agent_add_semantic_tag_rejects_invalid_type():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag": "not-a-tag",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_semantic_agent_add_duplicate_semantic_tag_fails():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    resource.add_semantic_tag(
        tag
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag": tag,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_semantic_agent_remove_semantic_tag():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    resource.add_semantic_tag(
        tag
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "structural",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is tag
    assert resource.get_semantic_tag(
        "structural"
    ) is None


def test_semantic_agent_remove_missing_semantic_tag_returns_none():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "missing",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


# ----------------------------------------------------------------------
# Categories
# ----------------------------------------------------------------------


def test_semantic_agent_list_categories_empty():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_categories",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


def test_semantic_agent_list_categories():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    structural = create_category(
        id="structural",
        name="Structural",
    )

    envelope = create_category(
        id="envelope",
        name="Building Envelope",
    )

    resource.add_category(
        structural
    )

    resource.add_category(
        envelope
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_categories",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        structural,
        envelope,
    ]


def test_semantic_agent_list_categories_returns_new_list():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    resource.add_category(
        category
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_categories",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    result.output.clear()

    assert resource.categories == [
        category
    ]


def test_semantic_agent_get_category():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    resource.add_category(
        category
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "envelope",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is category


def test_semantic_agent_get_missing_category_returns_none():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "missing",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


def test_semantic_agent_has_category_true():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    resource.add_category(
        category
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="has_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "envelope",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_semantic_agent_has_category_false():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="has_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "envelope",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


def test_semantic_agent_add_category():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_category",
            project=project,
            metadata={
                "resource": resource,
                "category": category,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is category
    assert resource.get_category(
        "envelope"
    ) is category


def test_semantic_agent_add_category_rejects_invalid_type():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_category",
            project=project,
            metadata={
                "resource": resource,
                "category": "not-a-category",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_semantic_agent_add_duplicate_category_fails():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    resource.add_category(
        category
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_category",
            project=project,
            metadata={
                "resource": resource,
                "category": category,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_semantic_agent_remove_category():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    resource.add_category(
        category
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "envelope",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is category
    assert resource.get_category(
        "envelope"
    ) is None


def test_semantic_agent_remove_missing_category_returns_none():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "missing",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


# ----------------------------------------------------------------------
# Semantic Context
# ----------------------------------------------------------------------


def test_semantic_agent_get_semantic_context():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    structural = create_tag(
        id="structural",
        name="Structural",
    )

    exterior = create_tag(
        id="exterior",
        name="Exterior",
    )

    envelope = create_category(
        id="envelope",
        name="Building Envelope",
    )

    resource.add_semantic_tag(
        structural
    )

    resource.add_semantic_tag(
        exterior
    )

    resource.add_category(
        envelope
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert result.output["classification"] is (
        classification
    )

    assert result.output["classification_path"] == (
        "Wall",
    )

    assert result.output["semantic_tags"] == [
        structural,
        exterior,
    ]

    assert result.output["categories"] == [
        envelope,
    ]


def test_semantic_agent_get_semantic_context_empty_memberships():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert result.output["classification"] is (
        classification
    )

    assert result.output["classification_path"] == (
        "Wall",
    )

    assert result.output["semantic_tags"] == []
    assert result.output["categories"] == []


def test_semantic_agent_context_is_deterministic():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()
    category = create_category()

    resource.add_semantic_tag(
        tag
    )

    resource.add_category(
        category
    )

    agent = create_agent()

    first = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    second = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert first.output == second.output


# ----------------------------------------------------------------------
# Independence
# ----------------------------------------------------------------------


def test_adding_tag_does_not_change_classification():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()

    agent = create_agent()

    agent.execute(
        create_request(
            action="add_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag": tag,
            },
        )
    )

    assert resource.classification is classification


def test_adding_category_does_not_change_classification():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    category = create_category()

    agent = create_agent()

    agent.execute(
        create_request(
            action="add_category",
            project=project,
            metadata={
                "resource": resource,
                "category": category,
            },
        )
    )

    assert resource.classification is classification


def test_tag_and_category_are_independent():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()
    category = create_category()

    agent = create_agent()

    agent.execute(
        create_request(
            action="add_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag": tag,
            },
        )
    )

    agent.execute(
        create_request(
            action="add_category",
            project=project,
            metadata={
                "resource": resource,
                "category": category,
            },
        )
    )

    assert resource.has_semantic_tag(
        "structural"
    )

    assert resource.has_category(
        "envelope"
    )


def test_removing_tag_does_not_remove_category():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()
    category = create_category()

    resource.add_semantic_tag(tag)
    resource.add_category(category)

    agent = create_agent()

    agent.execute(
        create_request(
            action="remove_semantic_tag",
            project=project,
            metadata={
                "resource": resource,
                "tag_id": "structural",
            },
        )
    )

    assert resource.has_category(
        "envelope"
    )


def test_removing_category_does_not_remove_tag():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    tag = create_tag()
    category = create_category()

    resource.add_semantic_tag(tag)
    resource.add_category(category)

    agent = create_agent()

    agent.execute(
        create_request(
            action="remove_category",
            project=project,
            metadata={
                "resource": resource,
                "category_id": "envelope",
            },
        )
    )

    assert resource.has_semantic_tag(
        "structural"
    )


# ----------------------------------------------------------------------
# No Inference
# ----------------------------------------------------------------------


def test_semantic_agent_does_not_infer_tag_from_classification():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output["semantic_tags"] == []


def test_semantic_agent_does_not_infer_category_from_classification():
    (
        project,
        classification,
        resource,
    ) = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output["categories"] == []


# ----------------------------------------------------------------------
# Unsupported Actions
# ----------------------------------------------------------------------


def test_semantic_agent_rejects_unknown_action():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="infer_semantics",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_semantic_agent_rejects_ai_inference_action():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="generate_semantic_tags",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Missing Metadata
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "action,key,value",
    [
        (
            "get_semantic_tag",
            "tag_id",
            None,
        ),
        (
            "has_semantic_tag",
            "tag_id",
            None,
        ),
        (
            "remove_semantic_tag",
            "tag_id",
            None,
        ),
        (
            "get_category",
            "category_id",
            None,
        ),
        (
            "has_category",
            "category_id",
            None,
        ),
        (
            "remove_category",
            "category_id",
            None,
        ),
    ],
)
def test_semantic_agent_requires_identifier_metadata(
    action: str,
    key: str,
    value: object,
):
    project, classification, resource = prepare_resource()

    metadata = {
        "resource": resource,
    }

    if value is not None:
        metadata[key] = value

    agent = create_agent()

    result = agent.execute(
        create_request(
            action=action,
            project=project,
            metadata=metadata,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Traceability
# ----------------------------------------------------------------------


def test_semantic_agent_preserves_request_id():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            request_id="semantic-request-123",
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.request_id == (
        "semantic-request-123"
    )


def test_semantic_agent_result_contains_agent_id():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.agent_id == (
        "semantic-agent"
    )


def test_semantic_agent_result_is_agent_result():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )


# ----------------------------------------------------------------------
# Non-AI Implementation
# ----------------------------------------------------------------------


def test_semantic_agent_does_not_require_ai_provider():
    project, classification, resource = prepare_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_semantic_context",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
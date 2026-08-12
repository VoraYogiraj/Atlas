"""
ENG-031 — Registry Agent

Tests the Atlas Registry Agent contract.

The Registry Agent:

    - operates within an AtlasProject
    - retrieves Resources
    - requires Resources
    - checks Resource existence
    - queries Resources by Classification
    - reports Resource count
    - lists Resources in registry order
    - does not mutate the Resource domain
    - preserves Agent Request/Result traceability
"""

import pytest

from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.registry_agent.registry_agent import AtlasRegistryAgent


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_project(
    *,
    name: str = "Registry Test Project",
) -> AtlasProject:
    return AtlasProject(name=name)


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
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
    action: str = "get_resource",
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


def create_agent() -> AtlasRegistryAgent:
    return AtlasRegistryAgent()


# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------


def test_registry_agent_has_default_id():
    agent = create_agent()

    assert agent.id == "registry-agent"


def test_registry_agent_has_default_name():
    agent = create_agent()

    assert agent.name == "Registry Agent"


def test_registry_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


# ----------------------------------------------------------------------
# Get Resource
# ----------------------------------------------------------------------


def test_registry_agent_get_resource():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource


def test_registry_agent_get_missing_resource_returns_none():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_resource",
            project=project,
            metadata={
                "resource_id": "missing-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None
    assert result.error is None


def test_registry_agent_get_requires_project():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_resource",
            project=None,
            metadata={
                "resource_id": "missing-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_registry_agent_get_requires_resource_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_resource",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


# ----------------------------------------------------------------------
# Require Resource
# ----------------------------------------------------------------------


def test_registry_agent_require_resource():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="require_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource


def test_registry_agent_require_missing_resource_fails():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="require_resource",
            project=project,
            metadata={
                "resource_id": "missing-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_registry_agent_require_requires_project():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="require_resource",
            project=None,
            metadata={
                "resource_id": "missing-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Contains Resource
# ----------------------------------------------------------------------


def test_registry_agent_contains_registered_resource():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="contains_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_registry_agent_contains_missing_resource():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="contains_resource",
            project=project,
            metadata={
                "resource_id": "missing-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


def test_registry_agent_contains_requires_resource_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="contains_resource",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Classification Queries
# ----------------------------------------------------------------------


def test_registry_agent_returns_resources_for_classification():
    project = create_project()

    wall = register_classification(
        project,
        create_classification(
            id="wall",
            name="Wall",
        ),
    )

    door = register_classification(
        project,
        create_classification(
            id="door",
            name="Door",
        ),
    )

    north_wall = create_resource(
        wall,
        name="North Wall",
    )

    south_wall = create_resource(
        wall,
        name="South Wall",
    )

    entrance_door = create_resource(
        door,
        name="Entrance Door",
    )

    project.add_resource(
        north_wall
    )
    project.add_resource(
        south_wall
    )
    project.add_resource(
        entrance_door
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=project,
            metadata={
                "classification_id": "wall",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert result.output == [
        north_wall,
        south_wall,
    ]


def test_registry_agent_classification_query_preserves_registry_order():
    project = create_project()

    wall = register_classification(
        project,
        create_classification(),
    )

    first = create_resource(
        wall,
        name="First Wall",
    )

    second = create_resource(
        wall,
        name="Second Wall",
    )

    third = create_resource(
        wall,
        name="Third Wall",
    )

    project.add_resource(first)
    project.add_resource(second)
    project.add_resource(third)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=project,
            metadata={
                "classification_id": "wall",
            },
        )
    )

    assert result.output == [
        first,
        second,
        third,
    ]


def test_registry_agent_empty_classification_query_returns_empty_list():
    project = create_project()

    register_classification(
        project,
        create_classification(),
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=project,
            metadata={
                "classification_id": "wall",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


def test_registry_agent_classification_query_requires_project():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=None,
            metadata={
                "classification_id": "wall",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_registry_agent_classification_query_requires_classification_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_registry_agent_rejects_empty_classification_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resources_for_classification",
            project=project,
            metadata={
                "classification_id": "",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


# ----------------------------------------------------------------------
# Resource Count
# ----------------------------------------------------------------------


def test_registry_agent_reports_zero_resource_count():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resource_count",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == 0


def test_registry_agent_reports_resource_count():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    first = create_resource(
        classification,
        name="First Wall",
    )

    second = create_resource(
        classification,
        name="Second Wall",
    )

    project.add_resource(first)
    project.add_resource(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resource_count",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == 2


# ----------------------------------------------------------------------
# List Resources
# ----------------------------------------------------------------------


def test_registry_agent_lists_resources():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    first = create_resource(
        classification,
        name="First Wall",
    )

    second = create_resource(
        classification,
        name="Second Wall",
    )

    project.add_resource(first)
    project.add_resource(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_resources",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        first,
        second,
    ]


def test_registry_agent_list_resources_preserves_registry_order():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resources = [
        create_resource(
            classification,
            name="Wall One",
        ),
        create_resource(
            classification,
            name="Wall Two",
        ),
        create_resource(
            classification,
            name="Wall Three",
        ),
    ]

    for resource in resources:
        project.add_resource(
            resource
        )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_resources",
            project=project,
        )
    )

    assert result.output == resources


def test_registry_agent_list_resources_returns_new_list():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_resources",
            project=project,
        )
    )

    result.output.clear()

    assert project.resource_count == 1
    assert project.get_resource(
        resource.aid
    ) is resource


def test_registry_agent_list_empty_project():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_resources",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


# ----------------------------------------------------------------------
# Project Boundary
# ----------------------------------------------------------------------


def test_registry_agent_is_project_scoped():
    first_project = create_project(
        name="Project A",
    )

    second_project = create_project(
        name="Project B",
    )

    first_classification = register_classification(
        first_project,
        create_classification(
            id="wall",
            name="Wall",
        ),
    )

    second_classification = register_classification(
        second_project,
        create_classification(
            id="wall",
            name="Wall",
        ),
    )

    first_resource = create_resource(
        first_classification,
        name="Project A Wall",
    )

    second_resource = create_resource(
        second_classification,
        name="Project B Wall",
    )

    first_project.add_resource(
        first_resource
    )

    second_project.add_resource(
        second_resource
    )

    agent = create_agent()

    first_result = agent.execute(
        create_request(
            action="list_resources",
            project=first_project,
        )
    )

    second_result = agent.execute(
        create_request(
            action="list_resources",
            project=second_project,
        )
    )

    assert first_result.output == [
        first_resource
    ]

    assert second_result.output == [
        second_resource
    ]


def test_registry_agent_does_not_cross_project_lookup():
    first_project = create_project(
        name="Project A",
    )

    second_project = create_project(
        name="Project B",
    )

    classification_a = register_classification(
        first_project,
        create_classification(
            id="wall",
            name="Wall",
        ),
    )

    classification_b = register_classification(
        second_project,
        create_classification(
            id="wall",
            name="Wall",
        ),
    )

    resource = create_resource(
        classification_a,
        name="Project A Wall",
    )

    first_project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_resource",
            project=second_project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


# ----------------------------------------------------------------------
# No Mutation
# ----------------------------------------------------------------------


def test_registry_agent_does_not_modify_resource():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification,
        name="Original Wall",
    )

    project.add_resource(
        resource
    )

    original_name = resource.name
    original_classification = resource.classification
    original_aid = resource.aid

    agent = create_agent()

    agent.execute(
        create_request(
            action="get_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    agent.execute(
        create_request(
            action="contains_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    agent.execute(
        create_request(
            action="list_resources",
            project=project,
        )
    )

    assert resource.name == original_name
    assert (
        resource.classification
        is original_classification
    )
    assert resource.aid == original_aid


def test_registry_agent_does_not_remove_resources():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    agent.execute(
        create_request(
            action="get_resource",
            project=project,
            metadata={
                "resource_id": resource.aid,
            },
        )
    )

    agent.execute(
        create_request(
            action="resource_count",
            project=project,
        )
    )

    assert (
        project.get_resource(resource.aid)
        is resource
    )


# ----------------------------------------------------------------------
# Missing Project
# ----------------------------------------------------------------------


def test_registry_agent_requires_project_for_count():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resource_count",
            project=None,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.error is not None


def test_registry_agent_requires_project_for_list():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_resources",
            project=None,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.error is not None


# ----------------------------------------------------------------------
# Unsupported Actions
# ----------------------------------------------------------------------


def test_registry_agent_rejects_unknown_action():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="create_resource",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_registry_agent_does_not_mutate_on_unsupported_action():
    project = create_project()

    classification = register_classification(
        project,
        create_classification(),
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="delete_resource",
            project=project,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED

    assert (
        project.get_resource(
            resource.aid
        )
        is resource
    )


# ----------------------------------------------------------------------
# Traceability
# ----------------------------------------------------------------------


def test_registry_agent_preserves_request_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            request_id="registry-request-123",
            action="resource_count",
            project=project,
        )
    )

    assert result.request_id == (
        "registry-request-123"
    )


def test_registry_agent_result_contains_agent_id():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resource_count",
            project=project,
        )
    )

    assert result.agent_id == (
        "registry-agent"
    )


def test_registry_agent_does_not_require_ai_provider():
    project = create_project()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="resource_count",
            project=project,
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )
"""
ENG-030 — Resource Agent

Tests the Atlas Resource Agent contract.

The Resource Agent:

    - operates within an AtlasProject
    - creates Resources
    - retrieves Resources
    - requires Resources
    - updates Resource names
    - deletes Resources
    - preserves Project integrity
    - uses the ENG-028 Agent Runtime contract
    - returns traceable AtlasAgentResult objects
"""

import pytest

from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.resource_registry import AtlasResourceRegistry
from atlas.resource_agent.resource_agent import AtlasResourceAgent


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_project(
    *,
    name: str = "Residential Project",
) -> AtlasProject:
    return AtlasProject(
        name=name,
    )


def register_wall_classification(
    project: AtlasProject,
) -> AtlasClassification:
    classification = create_classification()

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
    action: str = "create_resource",
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


def create_agent() -> AtlasResourceAgent:
    return AtlasResourceAgent()


# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------


def test_resource_agent_has_default_id():
    agent = create_agent()

    assert agent.id == "resource-agent"


def test_resource_agent_has_default_name():
    agent = create_agent()

    assert agent.name == "Resource Agent"


def test_resource_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


# ----------------------------------------------------------------------
# Create Resource
# ----------------------------------------------------------------------


def test_resource_agent_creates_resource():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource

    assert project.get_resource(
        resource.aid
    ) is resource


def test_resource_agent_create_preserves_resource_identity():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    original_id = resource.aid

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.output.aid == original_id


def test_resource_agent_create_requires_project_context():
    classification = create_classification()

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=None,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_resource_agent_create_requires_resource_metadata():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_resource_agent_create_rejects_non_resource_metadata():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": "not-a-resource",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_resource_agent_create_preserves_project_classification_integrity():
    project = create_project()

    classification = create_classification()

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED

    assert (
        project.get_resource(
            resource.aid
        )
        is None
    )


def test_resource_agent_create_duplicate_resource_fails():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


# ----------------------------------------------------------------------
# Get Resource
# ----------------------------------------------------------------------


def test_resource_agent_get_resource():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="get_resource",
        project=project,
        metadata={
            "resource_id": resource.aid,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource


def test_resource_agent_get_missing_resource_returns_success_with_none():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="get_resource",
        project=project,
        metadata={
            "resource_id": "missing-resource",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None
    assert result.error is None


def test_resource_agent_get_requires_project_context():
    agent = create_agent()

    request = create_request(
        action="get_resource",
        project=None,
        metadata={
            "resource_id": "missing-resource",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_resource_agent_get_requires_resource_id():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="get_resource",
        project=project,
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Require Resource
# ----------------------------------------------------------------------


def test_resource_agent_require_resource():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="require_resource",
        project=project,
        metadata={
            "resource_id": resource.aid,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource


def test_resource_agent_require_missing_resource_fails():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="require_resource",
        project=project,
        metadata={
            "resource_id": "missing-resource",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


# ----------------------------------------------------------------------
# Update Resource
# ----------------------------------------------------------------------


def test_resource_agent_updates_resource_name():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification,
        name="North Wall",
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=project,
        metadata={
            "resource": resource,
            "name": "Updated Wall",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource
    assert resource.name == "Updated Wall"


def test_resource_agent_update_preserves_resource_identity():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification,
        name="North Wall",
    )

    project.add_resource(
        resource
    )

    original_id = resource.aid

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=project,
        metadata={
            "resource": resource,
            "name": "Updated Wall",
        },
    )

    result = agent.execute(
        request
    )

    assert result.output.aid == original_id


def test_resource_agent_update_requires_project_context():
    classification = create_classification()

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=None,
        metadata={
            "resource": resource,
            "name": "Updated Wall",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


def test_resource_agent_update_requires_resource():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=project,
        metadata={
            "name": "Updated Wall",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


def test_resource_agent_update_requires_name():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


def test_resource_agent_update_rejects_foreign_resource():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    foreign_project = create_project(
        name="Foreign Project",
    )

    foreign_classification = create_classification(
        id="foreign-wall",
        name="Foreign Wall",
    )

    foreign_project.add_classification(
        foreign_classification
    )

    resource = create_resource(
        foreign_classification,
        name="Foreign Wall",
    )

    foreign_project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="update_resource",
        project=project,
        metadata={
            "resource": resource,
            "name": "Should Fail",
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert resource.name == "Foreign Wall"


# ----------------------------------------------------------------------
# Delete Resource
# ----------------------------------------------------------------------


def test_resource_agent_deletes_resource():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    project.add_resource(
        resource
    )

    agent = create_agent()

    request = create_request(
        action="delete_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is resource

    assert (
        project.get_resource(
            resource.aid
        )
        is None
    )


def test_resource_agent_delete_missing_resource_returns_none():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="delete_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


def test_resource_agent_delete_requires_project_context():
    classification = create_classification()

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="delete_resource",
        project=None,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


def test_resource_agent_delete_requires_resource():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="delete_resource",
        project=project,
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED


# ----------------------------------------------------------------------
# Relationship Integrity During Delete
# ----------------------------------------------------------------------


def test_resource_agent_delete_removes_resource_relationships():
    from atlas.relationships.relationship import AtlasRelationship

    project = create_project()

    classification = register_wall_classification(
        project
    )

    door_classification = AtlasClassification(
        id="door",
        name="Door",
    )

    project.add_classification(
        door_classification
    )

    wall = create_resource(
        classification,
        name="Wall",
    )

    door = create_resource(
        door_classification,
        name="Door",
    )

    project.add_resource(wall)
    project.add_resource(door)

    relationship = AtlasRelationship(
        id="wall-door",
        relationship_type="contains",
        source=wall,
        target=door,
    )

    project.add_relationship(
        relationship
    )

    assert project.relationship_count == 1

    agent = create_agent()

    request = create_request(
        action="delete_resource",
        project=project,
        metadata={
            "resource": wall,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert project.resource_count == 1
    assert project.relationship_count == 0


# ----------------------------------------------------------------------
# Unsupported Actions
# ----------------------------------------------------------------------


def test_resource_agent_rejects_unknown_action():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="unknown_operation",
        project=project,
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


# ----------------------------------------------------------------------
# Traceability
# ----------------------------------------------------------------------


def test_resource_agent_preserves_request_id():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        request_id="resource-request-123",
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.request_id == (
        "resource-request-123"
    )


def test_resource_agent_result_contains_agent_id():
    agent = create_agent()

    project = create_project()

    request = create_request(
        action="get_resource",
        project=project,
        metadata={
            "resource_id": "missing",
        },
    )

    result = agent.execute(
        request
    )

    assert result.agent_id == "resource-agent"


# ----------------------------------------------------------------------
# Non-AI Implementation
# ----------------------------------------------------------------------


def test_resource_agent_does_not_require_ai_provider():
    project = create_project()

    agent = create_agent()

    request = create_request(
        action="get_resource",
        project=project,
        metadata={
            "resource_id": "missing",
        },
    )

    result = agent.execute(
        request
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )


# ----------------------------------------------------------------------
# Resource Registry Integration
# ----------------------------------------------------------------------


def test_resource_agent_uses_project_resource_registry():
    project = create_project()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert (
        project.resources.get(resource.aid)
        is resource
    )


def test_resource_agent_does_not_use_unrelated_registry():
    project = create_project()

    unrelated_registry = AtlasResourceRegistry()

    classification = register_wall_classification(
        project
    )

    resource = create_resource(
        classification
    )

    agent = create_agent()

    request = create_request(
        action="create_resource",
        project=project,
        metadata={
            "resource": resource,
            "registry": unrelated_registry,
        },
    )

    result = agent.execute(
        request
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert unrelated_registry.get(
        resource.aid
    ) is None
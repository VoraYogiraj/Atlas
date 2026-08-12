"""
ENG-033 — Relationship Agent

Tests the Atlas Relationship Agent contract.

The Relationship Agent:

    - creates Relationships
    - queries Relationships
    - handles direction
    - queries by type
    - finds neighbors
    - checks direct connectivity
    - traverses the graph
    - checks reachability
    - removes Relationships
    - preserves Project / Graph integrity
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
from atlas.relationships.relationship import AtlasRelationship
from atlas.relationship_agent.relationship_agent import (
    AtlasRelationshipAgent,
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_project(
    *,
    name: str = "Relationship Test Project",
) -> AtlasProject:
    return AtlasProject(
        name=name,
    )


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def prepare_project(
    *,
    resource_names: tuple[str, ...] = (
        "Building",
        "Floor",
        "Room",
        "Wall",
        "Door",
    ),
) -> tuple[
    AtlasProject,
    dict[str, AtlasResource],
]:
    project = create_project()

    classification = create_classification()

    project.add_classification(
        classification
    )

    resources: dict[str, AtlasResource] = {}

    for name in resource_names:
        resource = AtlasResource(
            classification=classification,
            name=name,
        )

        project.add_resource(
            resource
        )

        resources[name] = resource

    return project, resources


def create_relationship(
    *,
    id: str = "relationship-001",
    relationship_type: str = "contains",
    source: AtlasResource,
    target: AtlasResource,
    description: str = "",
) -> AtlasRelationship:
    return AtlasRelationship(
        id=id,
        relationship_type=relationship_type,
        source=source,
        target=target,
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
    action: str = "add_relationship",
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


def create_agent() -> AtlasRelationshipAgent:
    return AtlasRelationshipAgent()


# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------


def test_relationship_agent_has_default_id():
    agent = create_agent()

    assert agent.id == "relationship-agent"


def test_relationship_agent_has_default_name():
    agent = create_agent()

    assert agent.name == "Relationship Agent"


def test_relationship_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


# ----------------------------------------------------------------------
# Project Context
# ----------------------------------------------------------------------


def test_relationship_agent_requires_project():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=None,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


# ----------------------------------------------------------------------
# Add Relationship
# ----------------------------------------------------------------------


def test_relationship_agent_adds_relationship():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is relationship
    assert project.relationship_count == 1


def test_relationship_agent_add_preserves_direction():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.output.source is resources["Building"]
    assert result.output.target is resources["Floor"]


def test_relationship_agent_add_requires_relationship():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_relationship_agent_add_rejects_invalid_relationship_type():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project,
            metadata={
                "relationship": "not-a-relationship",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_relationship_agent_add_rejects_foreign_source():
    project_a, resources_a = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    project_b, resources_b = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    relationship = create_relationship(
        source=resources_b["Building"],
        target=resources_a["Floor"],
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project_a,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert project_a.relationship_count == 0


def test_relationship_agent_add_rejects_foreign_target():
    project_a, resources_a = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    project_b, resources_b = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    relationship = create_relationship(
        source=resources_a["Building"],
        target=resources_b["Floor"],
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project_a,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert project_a.relationship_count == 0


def test_relationship_agent_add_duplicate_fails():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="add_relationship",
            project=project,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert project.relationship_count == 1


# ----------------------------------------------------------------------
# Relationships Between Resources
# ----------------------------------------------------------------------


def test_relationship_agent_get_relationships_between():
    project, resources = prepare_project()

    contains = create_relationship(
        id="contains",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    supports = create_relationship(
        id="supports",
        relationship_type="supports",
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_relationships_between",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        contains,
        supports,
    ]


def test_relationship_agent_get_between_ignores_direction():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Floor"],
        target=resources["Building"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_relationships_between",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        relationship
    ]


def test_relationship_agent_get_between_requires_first_resource():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_relationships_between",
            project=project,
            metadata={
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_relationship_agent_get_between_requires_second_resource():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_relationships_between",
            project=project,
            metadata={
                "first_resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Resource Relationship Queries
# ----------------------------------------------------------------------


def test_relationship_agent_relationships_for_resource():
    project, resources = prepare_project()

    contains = create_relationship(
        id="contains",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    supports = create_relationship(
        id="supports",
        relationship_type="supports",
        source=resources["Room"],
        target=resources["Floor"],
    )

    project.add_relationship(contains)
    project.add_relationship(supports)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_for_resource",
            project=project,
            metadata={
                "resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        contains,
        supports,
    ]


def test_relationship_agent_outgoing_relationships():
    project, resources = prepare_project()

    outgoing = create_relationship(
        id="outgoing",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    incoming = create_relationship(
        id="incoming",
        relationship_type="supports",
        source=resources["Room"],
        target=resources["Building"],
    )

    project.add_relationship(outgoing)
    project.add_relationship(incoming)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="outgoing_relationships",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        outgoing
    ]


def test_relationship_agent_incoming_relationships():
    project, resources = prepare_project()

    outgoing = create_relationship(
        id="outgoing",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    incoming = create_relationship(
        id="incoming",
        relationship_type="supports",
        source=resources["Room"],
        target=resources["Building"],
    )

    project.add_relationship(outgoing)
    project.add_relationship(incoming)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="incoming_relationships",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        incoming
    ]


def test_relationship_agent_relationships_for_resource_empty():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_for_resource",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


# ----------------------------------------------------------------------
# Relationship Type Queries
# ----------------------------------------------------------------------


def test_relationship_agent_relationships_by_type():
    project, resources = prepare_project()

    contains_one = create_relationship(
        id="contains-one",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    supports = create_relationship(
        id="supports",
        relationship_type="supports",
        source=resources["Floor"],
        target=resources["Room"],
    )

    contains_two = create_relationship(
        id="contains-two",
        relationship_type="contains",
        source=resources["Room"],
        target=resources["Wall"],
    )

    project.add_relationship(contains_one)
    project.add_relationship(supports)
    project.add_relationship(contains_two)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_by_type",
            project=project,
            metadata={
                "relationship_type": "contains",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        contains_one,
        contains_two,
    ]


def test_relationship_agent_relationships_by_unknown_type_returns_empty():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_by_type",
            project=project,
            metadata={
                "relationship_type": "supports",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


def test_relationship_agent_relationships_by_type_rejects_empty_type():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_by_type",
            project=project,
            metadata={
                "relationship_type": "",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_relationship_agent_relationships_by_type_requires_type():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_by_type",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Neighbors
# ----------------------------------------------------------------------


def test_relationship_agent_neighbors():
    project, resources = prepare_project()

    building_floor = create_relationship(
        id="building-floor",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    room_building = create_relationship(
        id="room-building",
        relationship_type="belongs_to",
        source=resources["Room"],
        target=resources["Building"],
    )

    project.add_relationship(
        building_floor
    )

    project.add_relationship(
        room_building
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="neighbors",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        resources["Floor"],
        resources["Room"],
    ]


def test_relationship_agent_neighbors_preserves_multiple_edges():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="supports",
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="neighbors",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert result.output == [
        resources["Floor"],
        resources["Floor"],
    ]


def test_relationship_agent_neighbors_preserves_outgoing_then_incoming():
    project, resources = prepare_project()

    outgoing = create_relationship(
        id="outgoing",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    incoming = create_relationship(
        id="incoming",
        relationship_type="belongs_to",
        source=resources["Room"],
        target=resources["Building"],
    )

    project.add_relationship(outgoing)
    project.add_relationship(incoming)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="neighbors",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        resources["Floor"],
        resources["Room"],
    ]


# ----------------------------------------------------------------------
# Connected
# ----------------------------------------------------------------------


def test_relationship_agent_connected_true():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="connected",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_relationship_agent_connected_false():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="connected",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


def test_relationship_agent_connected_is_direct_only():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="connected",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Room"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


# ----------------------------------------------------------------------
# Traversal
# ----------------------------------------------------------------------


def test_relationship_agent_traverse_depth_zero():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="traverse",
            project=project,
            metadata={
                "resource": resources["Building"],
                "max_depth": 0,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        resources["Building"]
    ]


def test_relationship_agent_traverse_depth_one():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="traverse",
            project=project,
            metadata={
                "resource": resources["Building"],
                "max_depth": 1,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        resources["Building"],
        resources["Floor"],
    ]


def test_relationship_agent_traverse_depth_two():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    third = create_relationship(
        id="third",
        relationship_type="contains",
        source=resources["Room"],
        target=resources["Wall"],
    )

    project.add_relationship(first)
    project.add_relationship(second)
    project.add_relationship(third)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="traverse",
            project=project,
            metadata={
                "resource": resources["Building"],
                "max_depth": 2,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        resources["Building"],
        resources["Floor"],
        resources["Room"],
    ]


def test_relationship_agent_traverse_unlimited_depth():
    project, resources = prepare_project()

    relationships = [
        create_relationship(
            id="one",
            relationship_type="contains",
            source=resources["Building"],
            target=resources["Floor"],
        ),
        create_relationship(
            id="two",
            relationship_type="contains",
            source=resources["Floor"],
            target=resources["Room"],
        ),
        create_relationship(
            id="three",
            relationship_type="contains",
            source=resources["Room"],
            target=resources["Wall"],
        ),
        create_relationship(
            id="four",
            relationship_type="contains",
            source=resources["Wall"],
            target=resources["Door"],
        ),
    ]

    for relationship in relationships:
        project.add_relationship(
            relationship
        )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="traverse",
            project=project,
            metadata={
                "resource": resources["Building"],
                "max_depth": None,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert result.output == [
        resources["Building"],
        resources["Floor"],
        resources["Room"],
        resources["Wall"],
        resources["Door"],
    ]


def test_relationship_agent_traverse_rejects_negative_depth():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="traverse",
            project=project,
            metadata={
                "resource": resources["Building"],
                "max_depth": -1,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Reachability
# ----------------------------------------------------------------------


def test_relationship_agent_reachable_true():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="reachable",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Room"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_relationship_agent_reachable_false():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="reachable",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Door"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is False


def test_relationship_agent_reachable_self():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="reachable",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is True


def test_relationship_agent_reachable_does_not_require_direct_edge():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    direct = agent.execute(
        create_request(
            action="connected",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Room"],
            },
        )
    )

    reachable = agent.execute(
        create_request(
            action="reachable",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Room"],
            },
        )
    )

    assert direct.output is False
    assert reachable.output is True


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def test_relationship_agent_removes_relationship():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    assert project.relationship_count == 1

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_relationship",
            project=project,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is relationship
    assert project.relationship_count == 0


def test_relationship_agent_remove_missing_returns_none():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_relationship",
            project=project,
            metadata={
                "relationship": relationship,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None


def test_relationship_agent_remove_requires_relationship():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="remove_relationship",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Count
# ----------------------------------------------------------------------


def test_relationship_agent_reports_zero_count():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == 0


def test_relationship_agent_reports_count():
    project, resources = prepare_project()

    first = create_relationship(
        id="first",
        relationship_type="contains",
        source=resources["Building"],
        target=resources["Floor"],
    )

    second = create_relationship(
        id="second",
        relationship_type="contains",
        source=resources["Floor"],
        target=resources["Room"],
    )

    project.add_relationship(first)
    project.add_relationship(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == 2


# ----------------------------------------------------------------------
# Project Boundary
# ----------------------------------------------------------------------


def test_relationship_agent_is_project_scoped():
    project_a, resources_a = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    project_b, resources_b = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    relationship_a = create_relationship(
        source=resources_a["Building"],
        target=resources_a["Floor"],
    )

    relationship_b = create_relationship(
        id="relationship-b",
        source=resources_b["Building"],
        target=resources_b["Floor"],
    )

    project_a.add_relationship(
        relationship_a
    )

    project_b.add_relationship(
        relationship_b
    )

    agent = create_agent()

    result_a = agent.execute(
        create_request(
            action="relationship_count",
            project=project_a,
        )
    )

    result_b = agent.execute(
        create_request(
            action="relationship_count",
            project=project_b,
        )
    )

    assert result_a.output == 1
    assert result_b.output == 1


def test_relationship_agent_rejects_foreign_resource_query():
    project_a, resources_a = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    project_b, resources_b = prepare_project(
        resource_names=(
            "Building",
            "Floor",
        ),
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationships_for_resource",
            project=project_a,
            metadata={
                "resource": resources_b["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Unsupported Actions
# ----------------------------------------------------------------------


def test_relationship_agent_rejects_unknown_action():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="infer_relationships",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_relationship_agent_rejects_ai_inference_action():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="predict_relationships",
            project=project,
            metadata={
                "resource": resources["Building"],
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Traceability
# ----------------------------------------------------------------------


def test_relationship_agent_preserves_request_id():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            request_id="relationship-request-123",
            action="relationship_count",
            project=project,
        )
    )

    assert result.request_id == (
        "relationship-request-123"
    )


def test_relationship_agent_result_contains_agent_id():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert result.agent_id == (
        "relationship-agent"
    )


def test_relationship_agent_result_is_agent_result():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )


# ----------------------------------------------------------------------
# Non-AI Implementation
# ----------------------------------------------------------------------


def test_relationship_agent_does_not_require_ai_provider():
    project, resources = prepare_project()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED


# ----------------------------------------------------------------------
# No Duplicate Graph Implementation
# ----------------------------------------------------------------------


def test_relationship_agent_uses_project_graph():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="connected",
            project=project,
            metadata={
                "first_resource": resources["Building"],
                "second_resource": resources["Floor"],
            },
        )
    )

    assert result.output is True


def test_relationship_agent_does_not_duplicate_graph_state():
    project, resources = prepare_project()

    relationship = create_relationship(
        source=resources["Building"],
        target=resources["Floor"],
    )

    project.add_relationship(
        relationship
    )

    agent = create_agent()

    first = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    second = agent.execute(
        create_request(
            action="relationship_count",
            project=project,
        )
    )

    assert first.output == 1
    assert second.output == 1
    assert project.relationship_count == 1
"""
ENG-035 — Multi-Agent Coordination

Tests the Atlas Multi-Agent Coordination contract.

The coordination layer:

    - delegates through the Orchestrator
    - preserves parent/child request lineage
    - preserves coordination IDs
    - tracks delegation depth
    - enforces maximum delegation depth
    - propagates Agent failures
    - rejects unknown Agents
    - preserves original Request immutability
    - executes sequentially
    - allows one Agent workflow to delegate to another
"""

import pytest

from atlas.agents.agent import AtlasAgent
from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.runtime import AtlasAgentRuntime
from atlas.agents.status import AtlasAgentStatus
from atlas.coordination.coordinator import AtlasAgentCoordinator
from atlas.orchestrator.orchestrator import AtlasOrchestrator


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_context(
    *,
    metadata: dict | None = None,
) -> AtlasAgentContext:
    return AtlasAgentContext(
        metadata=dict(
            metadata or {}
        ),
    )


def create_request(
    *,
    request_id: str = "request-001",
    action: str = "inspect",
    metadata: dict | None = None,
) -> AtlasAgentRequest:
    return AtlasAgentRequest(
        id=request_id,
        action=action,
        context=create_context(
            metadata=metadata,
        ),
    )


class EchoAgent(AtlasAgent):
    """Deterministic Agent used by coordination tests."""

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.COMPLETED,
            output={
                "request_id": request.id,
                "action": request.action,
                "metadata": request.context.metadata,
            },
            error=None,
        )


class FailingAgent(AtlasAgent):
    """Agent that returns a deterministic FAILED result."""

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.FAILED,
            output=None,
            error="delegated agent failed",
        )


class RaisingAgent(AtlasAgent):
    """Agent that raises during execution."""

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        raise RuntimeError(
            "delegated agent exception"
        )


class RecordingAgent(AtlasAgent):
    """Agent that records request execution order."""

    def __init__(
        self,
        *,
        id: str,
        name: str,
        events: list[tuple[str, str]],
    ) -> None:
        super().__init__(
            id=id,
            name=name,
        )
        self._events = events

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        self._events.append(
            (
                self.id,
                request.action,
            )
        )

        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.COMPLETED,
            output=request.action,
            error=None,
        )


def create_runtime(
    *agents: AtlasAgent,
) -> AtlasAgentRuntime:
    runtime = AtlasAgentRuntime()

    for agent in agents:
        runtime.register_agent(
            agent
        )

    return runtime


def create_orchestrator(
    runtime: AtlasAgentRuntime,
) -> AtlasOrchestrator:
    return AtlasOrchestrator(
        runtime=runtime,
    )


def create_coordinator(
    runtime: AtlasAgentRuntime,
    *,
    max_delegation_depth: int = 8,
) -> AtlasAgentCoordinator:
    orchestrator = create_orchestrator(
        runtime
    )

    return AtlasAgentCoordinator(
        orchestrator=orchestrator,
        max_delegation_depth=max_delegation_depth,
    )


# ----------------------------------------------------------------------
# Identity / Configuration
# ----------------------------------------------------------------------


def test_coordinator_has_default_max_delegation_depth():
    runtime = create_runtime()

    coordinator = create_coordinator(
        runtime
    )

    assert coordinator.max_delegation_depth == 8


def test_coordinator_accepts_custom_max_delegation_depth():
    runtime = create_runtime()

    coordinator = create_coordinator(
        runtime,
        max_delegation_depth=3,
    )

    assert coordinator.max_delegation_depth == 3


def test_coordinator_rejects_negative_max_delegation_depth():
    runtime = create_runtime()

    with pytest.raises(ValueError):
        create_coordinator(
            runtime,
            max_delegation_depth=-1,
        )


# ----------------------------------------------------------------------
# Direct Delegation
# ----------------------------------------------------------------------


def test_coordinator_delegates_to_registered_agent():
    agent = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    request = create_request(
        request_id="root-request",
        action="inspect_resource",
    )

    result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=request,
        delegated_by="orchestrator-agent",
    )

    assert result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert result.agent_id == (
        "resource-agent"
    )

    assert result.request_id == (
        request.id
    )


def test_coordinator_uses_orchestrator_runtime():
    agent = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    runtime = create_runtime(
        agent
    )

    orchestrator = create_orchestrator(
        runtime
    )

    coordinator = AtlasAgentCoordinator(
        orchestrator=orchestrator,
    )

    result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=create_request(),
        delegated_by="orchestrator-agent",
    )

    assert result.agent_id == (
        "semantic-agent"
    )


# ----------------------------------------------------------------------
# Coordination Metadata
# ----------------------------------------------------------------------


def test_coordinator_adds_delegation_metadata():
    agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    request = create_request(
        request_id="root-request",
    )

    result = coordinator.delegate(
        target_agent_id="registry-agent",
        request=request,
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.COMPLETED
    )

    metadata = result.output["metadata"]

    assert metadata["parent_request_id"] == (
        "root-request"
    )

    assert metadata["delegated_by"] == (
        "semantic-agent"
    )

    # Root request is depth 0.
    # Its delegated child request is depth 1.
    assert metadata["delegation_depth"] == 1


def test_coordinator_supports_coordination_id():
    agent = EchoAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=create_request(),
        delegated_by="semantic-agent",
        coordination_id="coordination-001",
    )

    assert result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert result.output["metadata"][
        "coordination_id"
    ] == "coordination-001"


def test_coordinator_preserves_existing_coordination_id():
    agent = EchoAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    request = create_request(
        metadata={
            "coordination_id": "existing-coordination",
        }
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=request,
        delegated_by="semantic-agent",
    )

    assert result.output["metadata"][
        "coordination_id"
    ] == "existing-coordination"


# ----------------------------------------------------------------------
# Delegation Depth
# ----------------------------------------------------------------------


def test_coordinator_first_delegation_has_depth_one():
    agent = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(),
        delegated_by="orchestrator-agent",
    )

    assert result.output["metadata"][
        "delegation_depth"
    ] == 1


def test_coordinator_increments_existing_delegation_depth():
    agent = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    request = create_request(
        metadata={
            "delegation_depth": 2,
        }
    )

    result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=request,
        delegated_by="resource-agent",
    )

    assert result.output["metadata"][
        "delegation_depth"
    ] == 3


def test_coordinator_rejects_depth_at_limit():
    agent = EchoAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime,
        max_delegation_depth=3,
    )

    request = create_request(
        metadata={
            "delegation_depth": 3,
        }
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=request,
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.output is None
    assert result.error is not None


def test_coordinator_allows_depth_below_limit():
    agent = EchoAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime,
        max_delegation_depth=3,
    )

    request = create_request(
        metadata={
            "delegation_depth": 2,
        }
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=request,
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert result.output["metadata"][
        "delegation_depth"
    ] == 3


# ----------------------------------------------------------------------
# Parent / Child Request Lineage
# ----------------------------------------------------------------------


def test_coordinator_preserves_parent_request_id():
    agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    root_request = create_request(
        request_id="root-request",
    )

    result = coordinator.delegate(
        target_agent_id="registry-agent",
        request=root_request,
        delegated_by="semantic-agent",
    )

    assert result.output["metadata"][
        "parent_request_id"
    ] == "root-request"


def test_coordinator_records_delegating_agent():
    agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="registry-agent",
        request=create_request(),
        delegated_by="semantic-agent",
    )

    assert result.output["metadata"][
        "delegated_by"
    ] == "semantic-agent"


def test_coordinator_rejects_missing_delegating_agent():
    agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="registry-agent",
        request=create_request(),
        delegated_by="",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.output is None


# ----------------------------------------------------------------------
# Unknown Agent
# ----------------------------------------------------------------------


def test_coordinator_unknown_agent_fails():
    runtime = create_runtime()

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="missing-agent",
        request=create_request(),
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.output is None
    assert result.error is not None


def test_coordinator_does_not_guess_unknown_agent():
    registry_agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    semantic_agent = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    runtime = create_runtime(
        registry_agent,
        semantic_agent,
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="unknown-agent",
        request=create_request(),
        delegated_by="orchestrator-agent",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.output is None


# ----------------------------------------------------------------------
# Failure Propagation
# ----------------------------------------------------------------------


def test_coordinator_propagates_failed_result():
    agent = FailingAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=create_request(),
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.agent_id == (
        "validation-agent"
    )

    assert result.error == (
        "delegated agent failed"
    )


def test_coordinator_converts_raised_agent_exception_to_failed_result():
    agent = RaisingAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=create_request(),
        delegated_by="semantic-agent",
    )

    assert result.status is (
        AtlasAgentStatus.FAILED
    )

    assert result.agent_id == (
        "validation-agent"
    )

    assert result.error == (
        "delegated agent exception"
    )


# ----------------------------------------------------------------------
# Request Immutability
# ----------------------------------------------------------------------


def test_coordinator_does_not_modify_original_request():
    agent = EchoAgent(
        id="registry-agent",
        name="Registry Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    request = create_request(
        request_id="immutable-request",
        action="inspect",
        metadata={
            "source": "original",
        },
    )

    original_id = request.id
    original_action = request.action
    original_context = request.context
    original_metadata = dict(
        request.context.metadata
    )

    coordinator.delegate(
        target_agent_id="registry-agent",
        request=request,
        delegated_by="semantic-agent",
    )

    assert request.id == original_id
    assert request.action == original_action
    assert request.context is original_context
    assert request.context.metadata == (
        original_metadata
    )


# ----------------------------------------------------------------------
# Sequential Coordination
# ----------------------------------------------------------------------


def test_coordinator_supports_sequential_delegation():
    events: list[tuple[str, str]] = []

    first = RecordingAgent(
        id="resource-agent",
        name="Resource Agent",
        events=events,
    )

    second = RecordingAgent(
        id="semantic-agent",
        name="Semantic Agent",
        events=events,
    )

    runtime = create_runtime(
        first,
        second,
    )

    coordinator = create_coordinator(
        runtime
    )

    first_result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(
            request_id="request-001",
            action="get_resource",
        ),
        delegated_by="orchestrator-agent",
        coordination_id="coordination-001",
    )

    second_result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=create_request(
            request_id="request-002",
            action="get_semantic_context",
            metadata={
                "coordination_id": "coordination-001",
            },
        ),
        delegated_by="resource-agent",
        coordination_id="coordination-001",
    )

    assert first_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert second_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert events == [
        (
            "resource-agent",
            "get_resource",
        ),
        (
            "semantic-agent",
            "get_semantic_context",
        ),
    ]


def test_coordinator_preserves_shared_coordination_id_across_steps():
    first = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    second = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    runtime = create_runtime(
        first,
        second,
    )

    coordinator = create_coordinator(
        runtime
    )

    coordination_id = "coordination-123"

    first_result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(
            request_id="request-001",
        ),
        delegated_by="orchestrator-agent",
        coordination_id=coordination_id,
    )

    second_result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=create_request(
            request_id="request-002",
            metadata={
                "coordination_id": coordination_id,
            },
        ),
        delegated_by="resource-agent",
        coordination_id=coordination_id,
    )

    assert first_result.output["metadata"][
        "coordination_id"
    ] == coordination_id

    assert second_result.output["metadata"][
        "coordination_id"
    ] == coordination_id


# ----------------------------------------------------------------------
# Multi-Step Agent Workflow
# ----------------------------------------------------------------------


def test_multi_agent_workflow_can_delegate_resource_to_semantic():
    resource_agent = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    semantic_agent = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    runtime = create_runtime(
        resource_agent,
        semantic_agent,
    )

    coordinator = create_coordinator(
        runtime
    )

    root_request = create_request(
        request_id="root-request",
        action="inspect_resource",
    )

    resource_result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=root_request,
        delegated_by="orchestrator-agent",
        coordination_id="coordination-001",
    )

    semantic_request = create_request(
        request_id="semantic-request",
        action="inspect_semantics",
        metadata={
            "source_request_id": (
                resource_result.request_id
            ),
        },
    )

    semantic_result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=semantic_request,
        delegated_by="resource-agent",
        coordination_id="coordination-001",
    )

    assert resource_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert semantic_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert semantic_result.output[
        "metadata"
    ]["source_request_id"] == (
        "root-request"
    )


def test_multi_agent_workflow_can_reach_validation():
    resource_agent = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    semantic_agent = EchoAgent(
        id="semantic-agent",
        name="Semantic Agent",
    )

    validation_agent = EchoAgent(
        id="validation-agent",
        name="Validation Agent",
    )

    runtime = create_runtime(
        resource_agent,
        semantic_agent,
        validation_agent,
    )

    coordinator = create_coordinator(
        runtime
    )

    coordination_id = "coordination-validation"

    resource_result = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(
            request_id="resource-request",
            action="get_resource",
        ),
        delegated_by="orchestrator-agent",
        coordination_id=coordination_id,
    )

    semantic_result = coordinator.delegate(
        target_agent_id="semantic-agent",
        request=create_request(
            request_id="semantic-request",
            action="get_semantic_context",
            metadata={
                "source_request_id": (
                    resource_result.request_id
                ),
            },
        ),
        delegated_by="resource-agent",
        coordination_id=coordination_id,
    )

    validation_result = coordinator.delegate(
        target_agent_id="validation-agent",
        request=create_request(
            request_id="validation-request",
            action="validate_resource",
            metadata={
                "source_request_id": (
                    semantic_result.request_id
                ),
            },
        ),
        delegated_by="semantic-agent",
        coordination_id=coordination_id,
    )

    assert resource_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert semantic_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert validation_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert validation_result.output[
        "metadata"
    ]["source_request_id"] == (
        "semantic-request"
    )


# ----------------------------------------------------------------------
# Deterministic Behavior
# ----------------------------------------------------------------------


def test_coordinator_is_deterministic():
    agent = EchoAgent(
        id="resource-agent",
        name="Resource Agent",
    )

    runtime = create_runtime(
        agent
    )

    coordinator = create_coordinator(
        runtime
    )

    first = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(
            request_id="request-001",
            action="inspect",
        ),
        delegated_by="orchestrator-agent",
        coordination_id="coordination-001",
    )

    second = coordinator.delegate(
        target_agent_id="resource-agent",
        request=create_request(
            request_id="request-001",
            action="inspect",
        ),
        delegated_by="orchestrator-agent",
        coordination_id="coordination-001",
    )

    assert first.status == second.status
    assert first.agent_id == second.agent_id
    assert first.request_id == second.request_id
    assert first.output == second.output
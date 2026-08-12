"""
ENG-028 — Agent Runtime Core

Tests the common Atlas Agent Runtime contract.

Components:

    AtlasAgentStatus
    AtlasAgentContext
    AtlasAgentRequest
    AtlasAgentResult
    AtlasAgent
    AtlasAgentRuntime
"""

from dataclasses import FrozenInstanceError

import pytest

from atlas.agents.agent import AtlasAgent
from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.runtime import AtlasAgentRuntime
from atlas.agents.status import AtlasAgentStatus


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


class EchoAgent(AtlasAgent):
    """
    Simple deterministic Agent used by the runtime tests.
    """

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.COMPLETED,
            output=request.action,
            error=None,
        )


class FailingAgent(AtlasAgent):
    """
    Agent used to verify failure handling.
    """

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        raise RuntimeError(
            "Agent execution failed"
        )


def create_context() -> AtlasAgentContext:
    return AtlasAgentContext()


def create_request(
    *,
    request_id: str = "request-001",
    action: str = "create_resource",
    context: AtlasAgentContext | None = None,
) -> AtlasAgentRequest:
    return AtlasAgentRequest(
        id=request_id,
        action=action,
        context=context or create_context(),
    )


def create_agent(
    *,
    agent_id: str = "resource-agent",
    name: str = "Resource Agent",
) -> AtlasAgent:
    return EchoAgent(
        id=agent_id,
        name=name,
    )


# ----------------------------------------------------------------------
# Agent Status
# ----------------------------------------------------------------------


def test_agent_status_has_idle():
    assert AtlasAgentStatus.IDLE.value == "idle"


def test_agent_status_has_running():
    assert AtlasAgentStatus.RUNNING.value == "running"


def test_agent_status_has_completed():
    assert AtlasAgentStatus.COMPLETED.value == "completed"


def test_agent_status_has_failed():
    assert AtlasAgentStatus.FAILED.value == "failed"


def test_agent_status_has_expected_members():
    assert list(AtlasAgentStatus) == [
        AtlasAgentStatus.IDLE,
        AtlasAgentStatus.RUNNING,
        AtlasAgentStatus.COMPLETED,
        AtlasAgentStatus.FAILED,
    ]


# ----------------------------------------------------------------------
# Agent Context
# ----------------------------------------------------------------------


def test_agent_context_can_be_created():
    context = AtlasAgentContext()

    assert context is not None


def test_agent_context_can_hold_project():
    project = object()

    context = AtlasAgentContext(
        project=project,
    )

    assert context.project is project


def test_agent_context_can_hold_resource_registry():
    registry = object()

    context = AtlasAgentContext(
        resource_registry=registry,
    )

    assert context.resource_registry is registry


def test_agent_context_can_hold_resource_graph():
    graph = object()

    context = AtlasAgentContext(
        resource_graph=graph,
    )

    assert context.resource_graph is graph


def test_agent_context_can_hold_classification_registry():
    registry = object()

    context = AtlasAgentContext(
        classification_registry=registry,
    )

    assert (
        context.classification_registry
        is registry
    )


def test_agent_context_can_hold_classification_hierarchy():
    hierarchy = object()

    context = AtlasAgentContext(
        classification_hierarchy=hierarchy,
    )

    assert (
        context.classification_hierarchy
        is hierarchy
    )


def test_agent_context_can_hold_validation_engine():
    engine = object()

    context = AtlasAgentContext(
        validation_engine=engine,
    )

    assert context.validation_engine is engine


def test_agent_context_can_hold_metadata():
    context = AtlasAgentContext(
        metadata={
            "source": "test",
        },
    )

    assert context.metadata == {
        "source": "test",
    }


def test_agent_context_metadata_is_isolated():
    metadata = {
        "source": "test",
    }

    context = AtlasAgentContext(
        metadata=metadata,
    )

    metadata["changed"] = True

    assert context.metadata == {
        "source": "test",
    }


# ----------------------------------------------------------------------
# Agent Request
# ----------------------------------------------------------------------


def test_agent_request_has_id():
    request = create_request()

    assert request.id == "request-001"


def test_agent_request_has_action():
    request = create_request()

    assert request.action == "create_resource"


def test_agent_request_has_context():
    context = create_context()

    request = create_request(
        context=context,
    )

    assert request.context is context


def test_agent_request_is_immutable():
    request = create_request()

    with pytest.raises(
        (FrozenInstanceError, AttributeError, TypeError)
    ):
        request.action = "different"


def test_agent_request_context_is_immutable():
    context = create_context()

    request = create_request(
        context=context,
    )

    with pytest.raises(
        (FrozenInstanceError, AttributeError, TypeError)
    ):
        request.context = AtlasAgentContext()


# ----------------------------------------------------------------------
# Agent Result
# ----------------------------------------------------------------------


def test_agent_result_has_id():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    assert result.id == "result-001"


def test_agent_result_has_request_id():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    assert result.request_id == "request-001"


def test_agent_result_has_agent_id():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    assert result.agent_id == "resource-agent"


def test_agent_result_has_status():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    assert result.status is AtlasAgentStatus.COMPLETED


def test_agent_result_has_output():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    assert result.output == "created-resource"


def test_agent_result_has_error():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.FAILED,
        output=None,
        error="Agent execution failed",
    )

    assert result.error == "Agent execution failed"


def test_agent_result_is_immutable():
    result = AtlasAgentResult(
        id="result-001",
        request_id="request-001",
        agent_id="resource-agent",
        status=AtlasAgentStatus.COMPLETED,
        output="created-resource",
        error=None,
    )

    with pytest.raises(
        (FrozenInstanceError, AttributeError, TypeError)
    ):
        result.output = "different"


# ----------------------------------------------------------------------
# Atlas Agent
# ----------------------------------------------------------------------


def test_agent_has_id():
    agent = create_agent()

    assert agent.id == "resource-agent"


def test_agent_has_name():
    agent = create_agent()

    assert agent.name == "Resource Agent"


def test_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


def test_agent_can_execute_request():
    agent = create_agent()
    request = create_request()

    result = agent.execute(
        request
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.request_id == request.id
    assert result.agent_id == agent.id
    assert result.status is AtlasAgentStatus.COMPLETED


def test_agent_result_is_traceable_to_request():
    agent = create_agent()

    request = create_request(
        request_id="request-123",
    )

    result = agent.execute(
        request
    )

    assert result.request_id == "request-123"


def test_agent_result_is_traceable_to_agent():
    agent = create_agent(
        agent_id="semantic-agent",
    )

    request = create_request()

    result = agent.execute(
        request
    )

    assert result.agent_id == "semantic-agent"


# ----------------------------------------------------------------------
# Agent Runtime Registration
# ----------------------------------------------------------------------


def test_agent_runtime_starts_without_agents():
    runtime = AtlasAgentRuntime()

    assert runtime.agents == []


def test_agent_runtime_register_agent():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    result = runtime.register_agent(
        agent
    )

    assert result is agent
    assert runtime.agents == [
        agent
    ]


def test_agent_runtime_preserves_registration_order():
    runtime = AtlasAgentRuntime()

    first = create_agent(
        agent_id="first-agent",
        name="First Agent",
    )

    second = create_agent(
        agent_id="second-agent",
        name="Second Agent",
    )

    third = create_agent(
        agent_id="third-agent",
        name="Third Agent",
    )

    runtime.register_agent(first)
    runtime.register_agent(second)
    runtime.register_agent(third)

    assert runtime.agents == [
        first,
        second,
        third,
    ]


def test_agent_runtime_rejects_duplicate_agent_id():
    runtime = AtlasAgentRuntime()

    first = create_agent(
        agent_id="duplicate",
    )

    second = create_agent(
        agent_id="duplicate",
        name="Different Agent",
    )

    runtime.register_agent(first)

    with pytest.raises(ValueError):
        runtime.register_agent(second)


def test_agent_runtime_get_agent():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    assert (
        runtime.get_agent("resource-agent")
        is agent
    )


def test_agent_runtime_get_missing_agent_returns_none():
    runtime = AtlasAgentRuntime()

    assert (
        runtime.get_agent("missing-agent")
        is None
    )


def test_agent_runtime_unregister_agent():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    removed = runtime.unregister_agent(
        "resource-agent"
    )

    assert removed is agent
    assert runtime.agents == []


def test_agent_runtime_unregister_missing_agent_returns_none():
    runtime = AtlasAgentRuntime()

    assert (
        runtime.unregister_agent(
            "missing-agent"
        )
        is None
    )


def test_agent_runtime_agents_returns_copy():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    agents = runtime.agents
    agents.clear()

    assert runtime.agents == [
        agent
    ]


# ----------------------------------------------------------------------
# Agent Runtime Execution
# ----------------------------------------------------------------------


def test_agent_runtime_execute():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    request = create_request()

    result = runtime.execute(
        "resource-agent",
        request,
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.agent_id == "resource-agent"
    assert result.request_id == request.id
    assert result.status is AtlasAgentStatus.COMPLETED


def test_agent_runtime_execute_preserves_output():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    request = create_request(
        action="validate_resource",
    )

    result = runtime.execute(
        "resource-agent",
        request,
    )

    assert result.output == "validate_resource"


def test_agent_runtime_execute_unknown_agent_raises_key_error():
    runtime = AtlasAgentRuntime()
    request = create_request()

    with pytest.raises(KeyError):
        runtime.execute(
            "missing-agent",
            request,
        )


def test_agent_failure_produces_failed_result():
    class RuntimeFailingAgent(AtlasAgent):
        def execute(
            self,
            request: AtlasAgentRequest,
        ) -> AtlasAgentResult:
            raise RuntimeError(
                "boom"
            )

    runtime = AtlasAgentRuntime()

    agent = RuntimeFailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    request = create_request()

    result = runtime.execute(
        "failing-agent",
        request,
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.agent_id == "failing-agent"
    assert result.request_id == request.id
    assert result.error == "boom"


def test_agent_failure_does_not_unregister_agent():
    class RuntimeFailingAgent(AtlasAgent):
        def execute(
            self,
            request: AtlasAgentRequest,
        ) -> AtlasAgentResult:
            raise RuntimeError(
                "boom"
            )

    runtime = AtlasAgentRuntime()

    agent = RuntimeFailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    result = runtime.execute(
        "failing-agent",
        create_request(),
    )

    assert result.status is AtlasAgentStatus.FAILED

    assert (
        runtime.get_agent("failing-agent")
        is agent
    )


def test_successful_execution_leaves_agent_completed():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    runtime.execute(
        "resource-agent",
        create_request(),
    )

    assert (
        agent.status
        is AtlasAgentStatus.COMPLETED
    )


def test_failed_execution_leaves_agent_failed():
    class RuntimeFailingAgent(AtlasAgent):
        def execute(
            self,
            request: AtlasAgentRequest,
        ) -> AtlasAgentResult:
            raise RuntimeError(
                "boom"
            )

    runtime = AtlasAgentRuntime()

    agent = RuntimeFailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    runtime.execute(
        "failing-agent",
        create_request(),
    )

    assert (
        agent.status
        is AtlasAgentStatus.FAILED
    )


# ----------------------------------------------------------------------
# Runtime Independence
# ----------------------------------------------------------------------


def test_agent_runtime_does_not_require_ai_provider():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    result = runtime.execute(
        "resource-agent",
        create_request(),
    )

    assert result.status is AtlasAgentStatus.COMPLETED


def test_agent_runtime_does_not_modify_request():
    runtime = AtlasAgentRuntime()
    agent = create_agent()

    runtime.register_agent(
        agent
    )

    request = create_request()

    original_id = request.id
    original_action = request.action
    original_context = request.context

    runtime.execute(
        "resource-agent",
        request,
    )

    assert request.id == original_id
    assert request.action == original_action
    assert request.context is original_context


# ----------------------------------------------------------------------
# Multiple Agent Execution
# ----------------------------------------------------------------------


def test_runtime_can_execute_multiple_registered_agents():
    runtime = AtlasAgentRuntime()

    resource_agent = create_agent(
        agent_id="resource-agent",
        name="Resource Agent",
    )

    semantic_agent = create_agent(
        agent_id="semantic-agent",
        name="Semantic Agent",
    )

    runtime.register_agent(
        resource_agent
    )

    runtime.register_agent(
        semantic_agent
    )

    first = runtime.execute(
        "resource-agent",
        create_request(
            request_id="request-001",
        ),
    )

    second = runtime.execute(
        "semantic-agent",
        create_request(
            request_id="request-002",
        ),
    )

    assert first.agent_id == "resource-agent"
    assert first.request_id == "request-001"

    assert second.agent_id == "semantic-agent"
    assert second.request_id == "request-002"
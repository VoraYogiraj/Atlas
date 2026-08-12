"""
ENG-029 — Orchestrator Agent

Tests the Atlas Orchestrator Agent contract.

The Orchestrator:

    - routes requests to registered Agents
    - uses AtlasAgentRuntime
    - preserves Request traceability
    - preserves Result traceability
    - propagates unknown-Agent failures
    - propagates failed Agent Results
    - does not mutate Requests or Results
"""

import pytest

from atlas.agents.agent import AtlasAgent
from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.runtime import AtlasAgentRuntime
from atlas.agents.status import AtlasAgentStatus
from atlas.orchestrator.orchestrator import AtlasOrchestrator


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


class EchoAgent(AtlasAgent):
    """Deterministic Agent used for Orchestrator tests."""

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
                "action": request.action,
                "context": request.context,
            },
            error=None,
        )


class FailingAgent(AtlasAgent):
    """Agent that returns a failed execution result."""

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
            error="Agent execution failed",
        )


def create_context() -> AtlasAgentContext:
    return AtlasAgentContext(
        metadata={
            "source": "test",
        }
    )


def create_request(
    *,
    request_id: str = "request-001",
    action: str = "create_resource",
) -> AtlasAgentRequest:
    return AtlasAgentRequest(
        id=request_id,
        action=action,
        context=create_context(),
    )


def create_runtime() -> AtlasAgentRuntime:
    return AtlasAgentRuntime()


def create_echo_agent(
    *,
    agent_id: str = "resource-agent",
    name: str = "Resource Agent",
) -> AtlasAgent:
    return EchoAgent(
        id=agent_id,
        name=name,
    )


def create_orchestrator(
    runtime: AtlasAgentRuntime | None = None,
) -> AtlasOrchestrator:
    return AtlasOrchestrator(
        runtime=runtime or create_runtime(),
    )


# ----------------------------------------------------------------------
# Orchestrator Identity
# ----------------------------------------------------------------------


def test_orchestrator_has_default_id():
    orchestrator = create_orchestrator()

    assert orchestrator.id == "orchestrator-agent"


def test_orchestrator_has_default_name():
    orchestrator = create_orchestrator()

    assert orchestrator.name == "Orchestrator Agent"


# ----------------------------------------------------------------------
# Runtime Ownership
# ----------------------------------------------------------------------


def test_orchestrator_exposes_runtime():
    runtime = create_runtime()

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    assert orchestrator.runtime is runtime


def test_orchestrator_uses_existing_runtime():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.agent_id == "resource-agent"


def test_orchestrator_does_not_create_duplicate_agent_registry():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    assert orchestrator.runtime is runtime
    assert orchestrator.runtime.agents == [
        agent
    ]


# ----------------------------------------------------------------------
# Dispatch
# ----------------------------------------------------------------------


def test_orchestrator_dispatches_request_to_target_agent():
    runtime = create_runtime()

    agent = create_echo_agent(
        agent_id="resource-agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.agent_id == "resource-agent"


def test_orchestrator_dispatch_returns_runtime_result():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    runtime_result = runtime.execute(
        "resource-agent",
        request,
    )

    assert result.request_id == runtime_result.request_id
    assert result.agent_id == runtime_result.agent_id
    assert result.status == runtime_result.status


def test_orchestrator_dispatch_preserves_request_id():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request(
        request_id="request-123",
    )

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.request_id == "request-123"


def test_orchestrator_dispatch_preserves_request_action():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request(
        action="validate_resource",
    )

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.output["action"] == (
        "validate_resource"
    )


def test_orchestrator_dispatch_preserves_request_context():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.output["context"] is request.context


# ----------------------------------------------------------------------
# Unknown Agent
# ----------------------------------------------------------------------


def test_orchestrator_unknown_agent_raises_key_error():
    runtime = create_runtime()

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    with pytest.raises(KeyError):
        orchestrator.dispatch(
            "missing-agent",
            request,
        )


def test_orchestrator_does_not_guess_unknown_agent():
    runtime = create_runtime()

    resource_agent = create_echo_agent(
        agent_id="resource-agent",
    )

    semantic_agent = create_echo_agent(
        agent_id="semantic-agent",
    )

    runtime.register_agent(
        resource_agent
    )

    runtime.register_agent(
        semantic_agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    with pytest.raises(KeyError):
        orchestrator.dispatch(
            "unknown-agent",
            request,
        )


# ----------------------------------------------------------------------
# Failed Agent
# ----------------------------------------------------------------------


def test_orchestrator_returns_failed_result_unchanged():
    runtime = create_runtime()

    agent = FailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request()

    result = orchestrator.dispatch(
        "failing-agent",
        request,
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.agent_id == "failing-agent"
    assert result.request_id == request.id
    assert result.error == "Agent execution failed"


def test_orchestrator_does_not_convert_failed_to_completed():
    runtime = create_runtime()

    agent = FailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    result = orchestrator.dispatch(
        "failing-agent",
        create_request(),
    )

    assert result.status is AtlasAgentStatus.FAILED


def test_orchestrator_does_not_unregister_failed_agent():
    runtime = create_runtime()

    agent = FailingAgent(
        id="failing-agent",
        name="Failing Agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    orchestrator.dispatch(
        "failing-agent",
        create_request(),
    )

    assert (
        runtime.get_agent("failing-agent")
        is agent
    )


# ----------------------------------------------------------------------
# Request Immutability
# ----------------------------------------------------------------------


def test_orchestrator_does_not_modify_request():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request(
        request_id="request-immutable",
        action="create_resource",
    )

    original_id = request.id
    original_action = request.action
    original_context = request.context

    orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert request.id == original_id
    assert request.action == original_action
    assert request.context is original_context


# ----------------------------------------------------------------------
# Result Preservation
# ----------------------------------------------------------------------


def test_orchestrator_preserves_result_agent_id():
    runtime = create_runtime()

    agent = create_echo_agent(
        agent_id="semantic-agent",
        name="Semantic Agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    result = orchestrator.dispatch(
        "semantic-agent",
        create_request(),
    )

    assert result.agent_id == "semantic-agent"


def test_orchestrator_preserves_result_request_id():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = create_request(
        request_id="trace-request",
    )

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.request_id == "trace-request"


def test_orchestrator_preserves_result_output():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    result = orchestrator.dispatch(
        "resource-agent",
        create_request(
            action="inspect_resource",
        ),
    )

    assert result.output["action"] == (
        "inspect_resource"
    )


# ----------------------------------------------------------------------
# Multiple Agents
# ----------------------------------------------------------------------


def test_orchestrator_can_dispatch_to_multiple_agents():
    runtime = create_runtime()

    resource_agent = create_echo_agent(
        agent_id="resource-agent",
        name="Resource Agent",
    )

    semantic_agent = create_echo_agent(
        agent_id="semantic-agent",
        name="Semantic Agent",
    )

    validation_agent = create_echo_agent(
        agent_id="validation-agent",
        name="Validation Agent",
    )

    runtime.register_agent(
        resource_agent
    )

    runtime.register_agent(
        semantic_agent
    )

    runtime.register_agent(
        validation_agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    first = orchestrator.dispatch(
        "resource-agent",
        create_request(
            request_id="request-001",
            action="create_resource",
        ),
    )

    second = orchestrator.dispatch(
        "semantic-agent",
        create_request(
            request_id="request-002",
            action="classify_resource",
        ),
    )

    third = orchestrator.dispatch(
        "validation-agent",
        create_request(
            request_id="request-003",
            action="validate_resource",
        ),
    )

    assert first.agent_id == "resource-agent"
    assert second.agent_id == "semantic-agent"
    assert third.agent_id == "validation-agent"

    assert first.request_id == "request-001"
    assert second.request_id == "request-002"
    assert third.request_id == "request-003"


def test_orchestrator_dispatches_sequentially():
    runtime = create_runtime()

    events: list[str] = []

    class TrackingAgent(AtlasAgent):
        def execute(
            self,
            request: AtlasAgentRequest,
        ) -> AtlasAgentResult:
            events.append(
                request.action
            )

            return AtlasAgentResult(
                id=f"result-{request.id}",
                request_id=request.id,
                agent_id=self.id,
                status=AtlasAgentStatus.COMPLETED,
                output=request.action,
                error=None,
            )

    first = TrackingAgent(
        id="first-agent",
        name="First Agent",
    )

    second = TrackingAgent(
        id="second-agent",
        name="Second Agent",
    )

    runtime.register_agent(first)
    runtime.register_agent(second)

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    orchestrator.dispatch(
        "first-agent",
        create_request(
            request_id="request-001",
            action="first",
        ),
    )

    orchestrator.dispatch(
        "second-agent",
        create_request(
            request_id="request-002",
            action="second",
        ),
    )

    assert events == [
        "first",
        "second",
    ]


# ----------------------------------------------------------------------
# No Domain Logic
# ----------------------------------------------------------------------


def test_orchestrator_does_not_require_resource_domain_objects():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    request = AtlasAgentRequest(
        id="request-no-domain",
        action="ping",
        context=AtlasAgentContext(),
    )

    result = orchestrator.dispatch(
        "resource-agent",
        request,
    )

    assert result.status is AtlasAgentStatus.COMPLETED


def test_orchestrator_does_not_require_ai_provider():
    runtime = create_runtime()

    agent = create_echo_agent()

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    result = orchestrator.dispatch(
        "resource-agent",
        create_request(),
    )

    assert result.status is AtlasAgentStatus.COMPLETED


# ----------------------------------------------------------------------
# Specialized Agent Isolation
# ----------------------------------------------------------------------


def test_orchestrator_routes_without_implementing_domain_behavior():
    runtime = create_runtime()

    class DomainTrackingAgent(AtlasAgent):
        def execute(
            self,
            request: AtlasAgentRequest,
        ) -> AtlasAgentResult:
            return AtlasAgentResult(
                id=f"result-{request.id}",
                request_id=request.id,
                agent_id=self.id,
                status=AtlasAgentStatus.COMPLETED,
                output="domain-operation",
                error=None,
            )

    agent = DomainTrackingAgent(
        id="domain-agent",
        name="Domain Agent",
    )

    runtime.register_agent(
        agent
    )

    orchestrator = create_orchestrator(
        runtime=runtime,
    )

    result = orchestrator.dispatch(
        "domain-agent",
        create_request(),
    )

    assert result.output == "domain-operation"


# ----------------------------------------------------------------------
# Orchestrator Stable Identity
# ----------------------------------------------------------------------


def test_orchestrator_id_is_stable():
    first = AtlasOrchestrator(
        runtime=AtlasAgentRuntime(),
    )

    second = AtlasOrchestrator(
        runtime=AtlasAgentRuntime(),
    )

    assert first.id == second.id


def test_orchestrator_name_is_stable():
    first = AtlasOrchestrator(
        runtime=AtlasAgentRuntime(),
    )

    second = AtlasOrchestrator(
        runtime=AtlasAgentRuntime(),
    )

    assert first.name == second.name
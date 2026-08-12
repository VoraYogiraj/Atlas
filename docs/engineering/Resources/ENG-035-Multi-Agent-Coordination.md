# ENG-035 — Multi-Agent Coordination

**Document ID:** ENG-035  
**Title:** Multi-Agent Coordination  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-028, ENG-029, ENG-030, ENG-031, ENG-032, ENG-033, ENG-034

---

# Purpose

This specification defines the Multi-Agent Coordination Model used by Atlas.

ENG-035 extends the existing Agent Runtime and Orchestrator so that
multiple specialized Atlas Agents can participate in one coordinated
execution.

The goal is to allow an Agent workflow to request work from another Agent
through the Orchestrator while preserving:

- Request traceability
- Result traceability
- Project and execution context
- Agent boundaries
- Deterministic execution
- Failure propagation
- Explicit delegation

---

# Scope

This specification defines:

- Agent delegation
- Coordination requests
- Coordination results
- Orchestrator-mediated Agent-to-Agent execution
- Delegation depth
- Parent-child request relationships
- Execution trace
- Sequential coordination
- Failure propagation
- Cycle prevention

This specification does not define:

- Autonomous AI reasoning
- LLM planning
- Machine-learning inference
- Persistent Agent memory
- Agent personality
- Long-term conversations
- Distributed Agent networking
- Cloud execution

---

# Definition

**Multi-Agent Coordination** is the controlled execution of multiple Atlas
Agents as part of one logical operation.

An Agent may request that another Agent perform a specialized operation.

The request is routed through the Orchestrator.

Agents must not directly invoke arbitrary Agent implementations.

---

# Core Principle

Agent-to-Agent collaboration shall use:

```text
Agent
  ↓
Orchestrator
  ↓
Target Agent
  ↓
Agent Result
  ↓
Orchestrator
  ↓
Calling workflow

Direct:

Agent A → Agent B

calls are outside ENG-035.

Architecture
                         Orchestrator
                              |
                    Coordination Layer
                              |
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
   Resource Agent       Semantic Agent       Validation Agent
         ↓                    ↓                    ↓
      Atlas Core          Semantic Model       Validation Engine

The Orchestrator remains the coordination authority.

Relationship to ENG-028

ENG-028 provides:

AtlasAgent
AtlasAgentContext
AtlasAgentRequest
AtlasAgentResult
AtlasAgentRuntime
AtlasAgentStatus

ENG-035 extends their use without replacing them.

Relationship to ENG-029

ENG-029 provides:

AtlasOrchestrator.dispatch()

ENG-035 extends the Orchestrator with coordination operations.

The Orchestrator remains the only component authorized to route delegated
Agent execution.

Coordination Request

A coordinated request shall preserve the existing AtlasAgentRequest.

Additional coordination metadata shall be represented in the request
Context metadata rather than changing the immutable core request structure
in ENG-035 v0.1.

The following metadata keys are defined:

parent_request_id
delegated_by
delegation_depth

Optional:

coordination_id
Parent Request

A delegated request may reference the logical request that caused the
delegation.

Example:

parent_request_id = request-001

This allows a coordinated execution chain to be reconstructed.

Delegated By

A delegated request shall identify the Agent that requested the delegation.

Example:

delegated_by = semantic-agent

This identifies the immediate requesting Agent.

Delegation Depth

Every delegated request shall contain a depth value.

Top-level:

delegation_depth = 0

First delegation:

delegation_depth = 1

Second delegation:

delegation_depth = 2

The Orchestrator shall enforce a configurable maximum delegation depth.

Default Delegation Depth

ENG-035 v0.1 shall use:

max_delegation_depth = 8

as the default.

The value shall be configurable on the Orchestrator.

Delegation Cycle Prevention

The Orchestrator shall prevent unbounded delegation chains.

When:

delegation_depth >= max_delegation_depth

the delegated request shall fail.

The Orchestrator shall return:

FAILED

with an explanatory error.

Coordination ID

A Coordination ID identifies one logical multi-Agent execution.

Example:

coordination_id = coordination-001

All delegated requests belonging to the same coordinated execution may
share the same Coordination ID.

Trace

The coordination trace is:

Request A
   |
   +--> Agent A
           |
           +--> Request B
                    |
                    +--> Agent B
                             |
                             +--> Result B
           |
           +--> Result A

The system must preserve:

request_id
parent_request_id
delegated_by
coordination_id
delegation_depth
agent_id
Coordination Result

An AtlasAgentResult remains the primary result type.

ENG-035 does not replace AtlasAgentResult.

The Orchestrator may attach coordination metadata to the result through an
execution trace maintained by the coordination layer.

Agent Delegation

An Agent shall be able to request delegated execution through an explicit
coordination interface supplied through its execution environment.

The Agent itself shall not access the runtime registry directly.

Coordination Interface

ENG-035 introduces the concept:

AtlasAgentCoordinator

The Coordinator shall provide:

delegate()

to execute another Agent through the Orchestrator.

Delegate Operation

Conceptually:

coordinator.delegate(
    target_agent_id,
    request,
)

The Coordinator shall:

Validate the target Agent.
Validate delegation depth.
Attach parent coordination metadata.
Dispatch through the Orchestrator.
Return the resulting AtlasAgentResult.
Preserve the coordination trace.
Sequential Coordination

ENG-035 v0.1 supports deterministic sequential coordination.

Example:

Semantic Agent
      |
      ↓
Registry Agent
      |
      ↓
Validation Agent

Each delegated operation completes before the next operation begins.

Parallel execution is outside v0.1.

Example

User request:

"Check this wall."

Coordination:

Orchestrator
    |
    ↓
Semantic Agent
    |
    ↓ delegate
Registry Agent
    |
    ↓ result
Semantic Agent
    |
    ↓ delegate
Validation Agent
    |
    ↓ result
Orchestrator

The Orchestrator can then combine the resulting Agent Results.

Failure Propagation

If a delegated Agent returns:

FAILED

the failure remains a failure.

The Coordinator shall not silently convert it into:

COMPLETED

The calling workflow may decide whether to continue.

Unknown Agent

Delegating to an unknown Agent shall fail through the existing Runtime
contract.

The Coordinator shall not guess another Agent.

Request Immutability

Delegation shall not mutate the original AtlasAgentRequest.

A delegated request may contain additional coordination metadata, but the
original Request object remains unchanged.

Result Immutability

Existing AtlasAgentResult objects remain immutable.

Coordination metadata must not mutate the Result object after execution.

Execution Context

The existing AtlasAgentContext remains the shared execution context.

A delegated Agent may receive the same Project, Resource Registry, Graph,
Classification Registries, Validation Engine, and metadata context.

Ownership is never transferred.

Domain Isolation

ENG-035 shall not move domain logic into the Orchestrator.

For example:

Resource logic
    → Resource Agent

Semantic logic
    → Semantic Agent

Relationship logic
    → Relationship Agent

Validation logic
    → Validation Agent

The Orchestrator coordinates.

Specialized Agents execute.

Atlas domain objects remain authoritative.

Deterministic Coordination

ENG-035 v0.1 is deterministic.

The system does not automatically:

choose an Agent using an LLM
generate plans
infer missing steps
invent delegation targets
perform autonomous reasoning

Delegation targets are explicit.

Future AI Coordination

Future versions may allow an AI planner to determine:

Which Agent should execute?
What sequence should execute?
What information should be passed?
When should execution stop?

The deterministic coordination layer defined by ENG-035 should remain the
execution substrate beneath that future planner.

Example Multi-Agent Workflow
User
 ↓
Orchestrator
 ↓
Resource Agent
 ↓
Registry Agent
 ↓
Semantic Agent
 ↓
Relationship Agent
 ↓
Validation Agent
 ↓
Orchestrator
 ↓
Final Result

Each Agent performs only its specialized responsibility.

Coordination Trace Example
coordination-001

request-001
  Agent: orchestrator
  depth: 0

request-002
  Agent: resource-agent
  parent: request-001
  depth: 1

request-003
  Agent: semantic-agent
  parent: request-002
  depth: 2

request-004
  Agent: validation-agent
  parent: request-003
  depth: 3

This provides a reconstructable execution chain.

Security Boundary

ENG-035 v0.1 does not define authentication or authorization.

However, Agent delegation must remain explicit through the Orchestrator.

Future versions may introduce:

Agent capabilities
Permission checks
Delegation policies
Resource access policies
Human approval requirements
Observability

Future execution tracing may record:

Coordination ID
Parent Request
Child Request
Agent ID
Action
Start time
Completion time
Status
Error
Delegation depth

ENG-035 v0.1 defines the logical trace relationship but does not require a
persistent telemetry subsystem.

Limits

ENG-035 v0.1 defines:

Sequential execution
Explicit delegation
Maximum depth
Request lineage
Result propagation

It does not define:

Parallel agents
Agent memory
Planning models
LLM reasoning
Persistent traces
Distributed execution
Phase 7 Evolution

The Phase 7 architecture becomes:

Agent Runtime
      ↓
Orchestrator
      ↓
Multi-Agent Coordination
      ↓
Specialized Agents

This turns the initial Agent Runtime into a coordinated execution model.

Relationship to Future Reasoning

ENG-035 is the deterministic execution foundation for future Atlas
reasoning.

Future intelligent reasoning may produce:

Plan
 ↓
Delegation
 ↓
Agent Execution
 ↓
Evidence
 ↓
Next Delegation
 ↓
Conclusion

ENG-035 provides the execution mechanism.

The AI reasoning layer decides what should be executed.

Future Evolution

Future versions may introduce:

Agent capability discovery
Agent planning
Parallel delegation
Conditional delegation
Agent memory
Shared working memory
Evidence aggregation
Confidence scoring
Human approval
AI planner
Multi-step reasoning
Goal-directed execution
Closing Statement

Specialized Agents provide expertise.

The Orchestrator provides coordination.

ENG-035 establishes the controlled mechanism through which Agents can
collaborate without directly depending on one another.

This separation allows Atlas to evolve from:

Independent Agents

into:

Coordinated Engineering Intelligence

while preserving the deterministic Atlas core underneath.
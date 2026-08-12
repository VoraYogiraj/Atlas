# ENG-029 — Orchestrator Agent

**Document ID:** ENG-029  
**Title:** Orchestrator Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-028 — Agent Runtime Core

---

# Purpose

This specification defines the Orchestrator Agent used by the Atlas Agent
Runtime.

The Orchestrator coordinates execution between specialized Atlas Agents.

The Orchestrator does not implement domain-specific Resource, Registry,
Semantic, Relationship, or Validation logic.

Instead, it determines which registered Agent should receive an
Agent Request and dispatches that request through the Atlas Agent Runtime.

---

# Scope

This specification defines:

- Orchestrator identity
- Agent routing
- Agent dispatch
- Request traceability
- Result traceability
- Agent lookup
- Unknown-agent handling
- Execution failure propagation
- Orchestrator independence

This specification does not define:

- Resource Agent behavior
- Registry Agent behavior
- Semantic Agent behavior
- Relationship Agent behavior
- Validation Agent behavior
- Agent planning
- Multi-step planning
- LLM reasoning
- Automatic task decomposition
- Agent memory
- Agent negotiation
- Parallel orchestration
- Workflow persistence

---

# Definition

The **Orchestrator Agent** is the top-level coordination component of the
Atlas Agent Runtime.

Its responsibility is to route an Agent Request to the appropriate
registered specialized Agent.

The Orchestrator coordinates.

It does not perform the domain operation itself.

---

# Architecture

The v0.1 architecture is:

```text
                 Orchestrator
                      |
                      v
               Agent Runtime
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
     Resource      Registry      Semantic
       Agent         Agent         Agent
        |             |             |
        +-------------+-------------+
                      |
                      v
                Agent Result

Relationship and Validation Agents participate in the same runtime model.

Relationship to ENG-028

ENG-028 defines:

AtlasAgent
AtlasAgentContext
AtlasAgentRequest
AtlasAgentResult
AtlasAgentStatus
AtlasAgentRuntime

ENG-029 builds orchestration on top of those primitives.

The Orchestrator shall use the existing Agent Runtime rather than
implementing a second Agent registry or execution mechanism.

Orchestrator Identity

The Orchestrator shall have a stable Agent ID.

Recommended identifier:

orchestrator-agent

The Orchestrator shall also expose a human-readable name:

Orchestrator Agent
Agent Routing

The Orchestrator shall route a request using an explicit target Agent ID.

A routing request shall contain:

target_agent_id
request

Example:

orchestrator.dispatch(
    "resource-agent",
    request,
)

The Orchestrator shall not infer an Agent target from arbitrary Resource
data in ENG-029 v0.1.

Dispatch

Dispatch performs the following:

Resolve the target Agent.
Submit the Request to the Agent Runtime.
Receive the Agent Result.
Return the Agent Result to the caller.

The Orchestrator shall not directly invoke specialized Agent implementation
methods when an AtlasAgentRuntime is available.

Request Traceability

The original Agent Request shall be passed unchanged to the target Agent.

The Orchestrator shall preserve:

Request ID
Action
Context

The Orchestrator shall not rewrite the Request ID.

Result Traceability

The returned Agent Result shall preserve:

Agent ID
Request ID
Status
Output
Error

The Orchestrator shall not silently discard execution metadata.

Unknown Agent

If the requested target Agent does not exist in the Runtime:

KeyError

shall be raised.

The Orchestrator shall not:

create an Agent automatically
guess another Agent
silently ignore the request
Agent Failure

If the target Agent execution produces a FAILED Agent Result, the
Orchestrator shall return that Result unchanged.

The Orchestrator shall not:

convert FAILED to COMPLETED
retry automatically
unregister the Agent
modify the error

Automatic retry and recovery are outside the scope of ENG-029 v0.1.

Orchestrator Independence

The Orchestrator shall not contain domain logic for:

Resources
Classifications
Properties
Relationships
Semantic Tags
Categories
Validation
Constraints

Those responsibilities remain within Atlas domain services and specialized
Agents.

Runtime Ownership

The Orchestrator shall hold a reference to an existing
AtlasAgentRuntime.

It shall not create a second independent Agent registry.

Example:

runtime = AtlasAgentRuntime()

orchestrator = AtlasOrchestrator(
    runtime=runtime,
)
Registration

ENG-029 does not introduce a second registration system for specialized
Agents.

Agents continue to be registered through:

runtime.register_agent(agent)

The Orchestrator resolves those Agents through the Runtime.

Orchestrator Execution

The initial Orchestrator API shall expose:

id
name
runtime
dispatch()

Example:

result = orchestrator.dispatch(
    "resource-agent",
    request,
)
Dispatch Result

dispatch() shall return:

AtlasAgentResult

The result returned by the Runtime shall be returned unchanged.

This ensures end-to-end traceability.

Synchronous Execution

ENG-029 v0.1 uses synchronous dispatch.

For one dispatch:

Request
   |
   v
Orchestrator
   |
   v
Runtime
   |
   v
Target Agent
   |
   v
Result
   |
   v
Orchestrator
   |
   v
Caller

Asynchronous and parallel dispatch are future capabilities.

Multiple Dispatches

An Orchestrator may dispatch multiple Requests sequentially.

Example:

Request A → Resource Agent
Request B → Registry Agent
Request C → Validation Agent

Each execution produces its own Agent Result.

Results remain traceable through their individual Request IDs.

Request Immutability

The Orchestrator shall not mutate an Agent Request.

The Request returned to the target Agent shall preserve the same object
identity or equivalent immutable content.

Result Immutability

The Orchestrator shall not mutate an Agent Result.

The Result returned by dispatch() shall be the same result produced by the
runtime.

Specialized Agents

The Phase 7 Agent Architecture defines:

Orchestrator Agent
Resource Agent
Registry Agent
Semantic Agent
Relationship Agent
Validation Agent

ENG-029 defines only the coordination layer.

The specialized Agents will be defined by future milestones.

Future Evolution

Future versions may introduce:

Automatic task routing
Intent classification
Task decomposition
Multi-agent workflows
Parallel execution
Agent planning
Retry strategies
Failure recovery
Human approval
Agent priorities
Capability matching
LLM-based orchestration
Agent collaboration
Agent memory

These capabilities are outside the scope of ENG-029 v0.1.

Example
User Request
     |
     v
Orchestrator
     |
     | target = validation-agent
     v
AtlasAgentRuntime
     |
     v
Validation Agent
     |
     v
AgentResult
     |
     v
Orchestrator
     |
     v
Caller

The Orchestrator does not perform validation itself.

It only coordinates execution.

Closing Statement

The Orchestrator Agent is the coordination layer of the Atlas Agent
Runtime.

The Runtime executes Agents.

Specialized Agents perform domain operations.

The Orchestrator connects Requests to the appropriate Agent while
preserving traceability, isolation, and a clean separation of
responsibilities.
# ENG-028 — Agent Runtime Core

**Document ID:** ENG-028  
**Title:** Agent Runtime Core  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-001, ENG-003, ENG-004, ENG-005, ENG-006, ENG-008, ENG-026, ENG-027

---

# Purpose

This specification defines the core runtime model used by Atlas Agents.

The Atlas Agent Runtime provides the common execution contract required by
specialized agents.

The runtime is independent of any specific AI provider or model.

An Agent may be implemented using:

- deterministic application logic
- an AI model
- a local model
- a remote model
- a human-in-the-loop implementation
- a future agent implementation

The runtime provides a stable contract regardless of implementation method.

---

# Scope

This specification defines:

- Agent identity
- Agent status
- Agent context
- Agent requests
- Agent results
- Agent execution
- Agent registration
- Agent lookup
- Agent removal
- Execution ordering
- Failure handling
- Runtime independence

This specification does not define:

- Specific AI providers
- LLM prompting
- Model selection
- Tool calling protocols
- Orchestrator intelligence
- Specialized Resource Agent behavior
- Specialized Registry Agent behavior
- Specialized Semantic Agent behavior
- Specialized Relationship Agent behavior
- Specialized Validation Agent behavior
- Networking
- Persistence

---

# Agent Runtime Model

The Atlas Agent Runtime follows:

```text
Agent Request
      |
      v
Agent Runtime
      |
      v
Atlas Agent
      |
      v
Agent Result

The Runtime is responsible for execution.

The Agent is responsible for its own domain-specific behavior.

Agent

An Atlas Agent is an executable component capable of receiving an
Agent Request and producing an Agent Result.

An Agent has:

Agent
│
├── id
├── name
└── execute(request)
Agent Identity

Every Agent shall have a stable identifier.

Example:

resource-agent

The Agent ID is used for:

Registration
Lookup
Execution
Result attribution

Two Agents with the same ID represent the same runtime identity.

Agent Name

Every Agent shall have a human-readable name.

Example:

Resource Agent

The Agent name is descriptive and does not replace the stable Agent ID.

Agent Status

Atlas Agents shall expose a runtime status.

The initial status model is:

IDLE
RUNNING
COMPLETED
FAILED

Status meanings:

IDLE

The Agent is registered and available for execution.

RUNNING

The Agent is currently executing a request.

COMPLETED

The most recent execution completed successfully.

FAILED

The most recent execution failed.

Agent Context

An Agent Context provides access to the Atlas execution environment.

The context may provide:

Project
Resource Registry
Resource Graph
Classification Registry
Classification Hierarchy
Validation Engine
shared metadata

The context does not transfer ownership of these objects to the Agent.

Agents operate within the existing Atlas domain model.

Agent Request

An Agent Request represents one execution request.

A Request contains:

AgentRequest
│
├── id
├── action
└── context
Request ID

Every Agent Request has a unique identifier.

The Request ID allows an execution to be traced.

Action

The action identifies the operation requested from the Agent.

Example:

create_resource
validate_resource
find_relationships
Context

The Request may provide execution-specific context.

Context is immutable for the lifetime of the Request.

Agent Result

An Agent Result represents the outcome of one Agent execution.

A Result contains:

AgentResult
│
├── id
├── request_id
├── agent_id
├── status
├── output
└── error
Result ID

Every Agent Result has a unique identifier.

Request ID

The Request ID identifies the execution that produced the Result.

Agent ID

The Agent ID identifies the Agent that produced the Result.

Status

The Result status corresponds to the execution outcome.

Output

Output contains the successful execution result.

Output may be any Atlas-compatible value.

Error

Error contains execution failure information when execution fails.

A successful Result shall not require an error.

A failed Result shall contain error information.

Result Immutability

Agent Results shall be immutable after creation.

The following fields shall not change:

ID
Request ID
Agent ID
Status
Output
Error

A new execution shall produce a new Result.

Agent Request Immutability

Agent Requests shall be immutable after creation.

The following fields shall not change:

ID
Action
Context
Agent Runtime

The Agent Runtime is represented by:

AtlasAgentRuntime

The Runtime manages registered Agents and executes Requests.

The Runtime shall support:

register_agent()
unregister_agent()
get_agent()
agents
execute()
Agent Registration

Agents must be explicitly registered with the Runtime.

Example:

runtime = AtlasAgentRuntime()

runtime.register_agent(agent)

An Agent with an existing ID shall not be registered twice.

Duplicate registration shall raise:

ValueError
Agent Removal

The Runtime shall support Agent removal by ID.

Example:

runtime.unregister_agent("resource-agent")

Removing an existing Agent shall return the removed Agent.

Removing a missing Agent shall return:

None
Agent Lookup

The Runtime shall support Agent lookup:

runtime.get_agent("resource-agent")

A missing Agent shall return:

None
Agent Collection

The Runtime shall expose registered Agents through:

agents

Agents shall preserve registration order.

The returned collection shall not expose the Runtime's internal mutable
storage.

Agent Execution

The Runtime shall support:

runtime.execute(
    agent_id,
    request,
)

Execution shall:

Locate the Agent.
Execute the Request.
Produce an Agent Result.
Associate the Result with the Agent and Request.
Return the Result.
Execution Lifecycle

An Agent execution follows:

IDLE
  |
  v
RUNNING
  |
  +------> COMPLETED
  |
  +------> FAILED

The Runtime shall not allow two simultaneous state transitions for the same
execution.

Successful Execution

When an Agent executes successfully:

Result.status == COMPLETED

The Result shall contain:

Agent ID
Request ID
Output

Error should be absent or None.

Failed Execution

When an Agent raises an execution error:

Result.status == FAILED

The Result shall contain:

Agent ID
Request ID
Error

The Runtime shall not silently treat execution failures as success.

Missing Agent

Executing an unknown Agent ID shall raise:

KeyError

The Runtime shall not construct or execute an unknown Agent automatically.

Agent Execution Independence

The Runtime shall not require any specific AI provider.

An Agent may use arbitrary internal implementation logic.

The Runtime only depends on the Agent execution contract.

Domain Independence

The core Agent Runtime shall not contain Resource-specific business logic.

For example:

AtlasAgentRuntime

must not directly implement:

Resource creation
Classification logic
Relationship logic
Validation rules
Constraint evaluation

Those behaviors belong to specialized Agents or Atlas domain services.

Context Independence

The Runtime shall provide the execution environment but shall not transfer
ownership of Atlas domain objects to Agents.

Agents consume the existing Atlas domain model.

Agent Result Traceability

Every Result shall be traceable to:

Agent
   +
Request

This allows Atlas to reconstruct the execution history of an operation.

Error Isolation

An Agent failure shall not automatically unregister the Agent.

Example:

Resource Agent
    |
    v
execution
    |
    X
   FAILED

The Agent remains registered and may be executed again.

Retry

Automatic retry is outside the scope of ENG-028 v0.1.

A caller may explicitly issue a new Agent Request.

Concurrency

Concurrent Agent execution is outside the scope of ENG-028 v0.1.

The initial Runtime may execute Agents synchronously.

Future versions may introduce asynchronous and parallel execution.

Persistence

Agent state persistence is outside the scope of ENG-028.

This capability belongs to the future persistence architecture.

Security

Agent authentication and authorization are outside the scope of ENG-028.

Future enterprise and collaboration phases may introduce Agent permissions.

Architecture

The v0.1 architecture is:

Atlas Agent Runtime
        |
        +----------------------+
        |                      |
        v                      v
 Agent Registry          Execution Context
        |                      |
        +----------+-----------+
                   |
                   v
              Atlas Agent
                   |
                   v
              Agent Result
Proposed Package Structure
atlas/
└── agents/
    ├── __init__.py
    ├── status.py
    ├── context.py
    ├── request.py
    ├── result.py
    ├── agent.py
    └── runtime.py

The initial public API shall expose:

AtlasAgentStatus
AtlasAgentContext
AtlasAgentRequest
AtlasAgentResult
AtlasAgent
AtlasAgentRuntime
Example

A Resource Agent may eventually receive:

Request
    id:
        request-001

    action:
        create_resource

    context:
        Project = Residential Project

The Agent executes the requested operation and returns:

Result
    id:
        result-001

    request_id:
        request-001

    agent_id:
        resource-agent

    status:
        COMPLETED

    output:
        created-resource

The specific Resource Agent behavior is outside the scope of ENG-028.

Specialized Agents

ENG-028 provides the common runtime foundation for future specialized
Agents.

The V0.1 Agent Architecture includes:

Orchestrator Agent
Resource Agent
Registry Agent
Semantic Agent
Relationship Agent
Validation Agent

Each specialized Agent shall be implemented against the common ENG-028
runtime contract.

Future Evolution

Future versions may introduce:

Async execution
Parallel execution
Agent priorities
Agent capabilities
Tool registration
Agent messaging
Agent collaboration
Agent planning
Agent memory
Agent permissions
Human approval
Agent observability
Execution history
Agent orchestration
Model providers
LLM integration

These capabilities are outside the scope of ENG-028 v0.1.

Relationship to Other Specifications

ENG-028 depends on:

Atlas Resource model
Resource Registry
Resource Graph
Semantic Engine
Validation Engine
Constraint Model

ENG-028 provides the runtime layer through which future specialized
Agents operate on the existing Atlas domain model.

Closing Statement

The Atlas Agent Runtime provides a stable execution contract for AI and
non-AI Agents.

The Runtime executes.

Agents provide domain behavior.

Atlas Resources remain the shared engineering model.

This separation allows Atlas to evolve from a deterministic engineering
engine into an agent-based engineering intelligence platform without
coupling the core domain model to any particular AI provider.
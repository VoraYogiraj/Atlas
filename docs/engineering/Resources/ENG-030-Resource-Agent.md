# ENG-030 — Resource Agent

**Document ID:** ENG-030  
**Title:** Resource Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-001, ENG-010, ENG-011, ENG-028, ENG-029

---

# Purpose

This specification defines the Resource Agent used by the Atlas Agent
Runtime.

The Resource Agent provides agent-based access to the core Resource
management operations already implemented by AtlasProject.

The Resource Agent does not replace AtlasProject, AtlasResourceRegistry,
or AtlasResource.

It acts as an agent-facing coordination layer over the existing Resource
domain services.

---

# Scope

This specification defines:

- Resource Agent identity
- Resource creation
- Resource lookup
- Resource requirement lookup
- Resource update
- Resource removal
- Project ownership
- Request action dispatch
- Agent Result generation
- Resource-domain error handling
- Project integrity preservation

This specification does not define:

- Resource schema changes
- Resource classification logic
- Resource validation rules
- Relationship creation logic
- Semantic reasoning
- Constraint evaluation
- Persistence
- AI model behavior
- Natural-language planning

---

# Definition

The **Resource Agent** is a specialized Atlas Agent responsible for
Resource-domain operations.

It exposes Resource operations through the Agent Runtime while delegating
actual domain integrity to `AtlasProject`.

---

# Architecture

The v0.1 architecture is:

```text
Agent Request
      |
      v
Resource Agent
      |
      v
AtlasProject
      |
      +-------------------+
      |                   |
      v                   v
Resource Registry     Resource Graph
      |
      v
Atlas Resource

The Resource Agent is not a second Resource Registry.

Relationship to ENG-028

ENG-028 defines the common Agent Runtime:

AtlasAgent
AtlasAgentRequest
AtlasAgentResult
AtlasAgentContext
AtlasAgentRuntime

ENG-030 specializes that runtime for Resource operations.

Relationship to AtlasProject

The Resource Agent shall use AtlasProject as the authoritative
Resource-domain boundary.

The Resource Agent shall not directly modify the Project's internal
registries.

The following Project operations are the authoritative domain operations:

add_resource()
get_resource()
require_resource()
remove_resource()
Identity

The Resource Agent shall use:

id:
resource-agent

name:
Resource Agent
Supported Actions

ENG-030 v0.1 supports:

create_resource
get_resource
require_resource
update_resource
delete_resource
Action Context

The execution context shall provide access to an AtlasProject.

Example:

AtlasAgentContext(
    project=project,
)

The Resource Agent shall reject execution when the required Project
context is unavailable.

Request Data

Resource operation data shall be supplied through the Agent Request
context metadata.

The following metadata keys are defined by ENG-030:

create_resource
resource

The value shall be an AtlasResource.

Example:

AtlasAgentContext(
    project=project,
    metadata={
        "resource": resource,
    },
)
get_resource
resource_id

The value shall be an AtlasID.

require_resource
resource_id

The value shall be an AtlasID.

update_resource
resource

The value shall be an existing AtlasResource instance.

delete_resource
resource

The value shall be an existing AtlasResource instance.

Create Resource

The create_resource action shall delegate to:

project.add_resource(resource)

The Project remains responsible for verifying that the Resource's
Classification is registered.

A successful operation returns:

COMPLETED

with the created Resource as output.

The same Resource instance shall be returned.

Create Resource Failure

If the Project rejects the Resource, the Resource Agent shall return:

FAILED

with an explanatory error.

The Resource Agent shall not bypass Project validation.

Get Resource

The get_resource action shall delegate to:

project.get_resource(resource_id)

A successful lookup returns:

COMPLETED

with the Resource as output.

A missing Resource returns:

COMPLETED

with:

output = None

The lookup operation itself is not considered an execution failure merely
because the Resource does not exist.

Require Resource

The require_resource action shall delegate to:

project.require_resource(resource_id)

A successful lookup returns:

COMPLETED

with the Resource as output.

A missing Resource shall produce:

FAILED

with the corresponding lookup error.

Update Resource

ENG-030 v0.1 treats Resource updates as mutation of an existing Resource
through the existing public Resource API.

The Resource Agent shall support updating:

name

through:

resource.name = value

The update metadata shall contain:

resource
name

Example:

AtlasAgentContext(
    project=project,
    metadata={
        "resource": resource,
        "name": "Updated Wall",
    },
)

The Resource must already belong to the Project.

A Resource that is not registered with the Project shall not be updated by
the Resource Agent.

Update Resource Result

A successful update returns:

COMPLETED

with the updated Resource as output.

The same Resource instance is retained.

Delete Resource

The delete_resource action shall delegate to:

project.remove_resource(resource)

The Project is responsible for removing Relationships before unregistering
the Resource.

A successful deletion returns:

COMPLETED

with the removed Resource as output.

Delete Missing Resource

Deleting a Resource that is not registered with the Project shall return:

COMPLETED

with:

output = None

because the Project's removal API already represents absence with None.

Project Integrity

The Resource Agent shall preserve all Project integrity rules.

In particular:

Resource
    |
    +-- Classification must be registered
    |
    +-- Resource belongs to Project Registry
    |
    +-- Relationships belong to Project Graph

The Resource Agent must never directly insert a Resource into the Registry
while bypassing AtlasProject.add_resource().

Ownership

The Resource Agent does not own Resources.

Resources remain owned by the Project's Resource Registry.

The Agent merely performs operations against the Project.

Resource Identity

The Resource Agent shall never generate or replace an existing
AtlasResource.aid.

Resource identity remains owned by AtlasResource.

Agent Result

Every Resource Agent execution shall return an AtlasAgentResult.

The result shall preserve:

agent_id
request_id
status
output
error

The Result shall be generated through the ENG-028 runtime contract.

Errors

The Resource Agent shall return FAILED results for execution errors.

Examples include:

Missing Project context
Invalid Resource input
Classification not registered
Missing required Resource
Invalid Resource update target
Invalid operation metadata

The Agent shall not silently convert domain failures into successful
results.

Unsupported Actions

An unknown action shall produce:

FAILED

with an explanatory error.

The Resource Agent shall not guess an operation from an unknown action.

Non-Resource Responsibilities

The Resource Agent shall not directly implement:

Classification hierarchy
Classification registration
Relationships
Graph traversal
Semantic Tags
Categories
Validation
Constraints

Those capabilities remain with their existing domain services and future
specialized Agents.

Non-AI Implementation

The Resource Agent does not require an AI provider.

ENG-030 v0.1 is deterministic.

An AI-powered Resource Agent may be introduced later, but it must operate
through the same Resource-domain contract.

Execution Model

Example:

Agent Request
    action = create_resource
    context = Project + Resource
          |
          v
Resource Agent
          |
          v
AtlasProject.add_resource()
          |
          v
AtlasAgentResult
Traceability

Every Resource operation remains traceable through:

Agent Request
      |
      v
Resource Agent
      |
      v
AtlasProject operation
      |
      v
Agent Result

The Request ID remains unchanged.

Future Evolution

Future versions may introduce:

Bulk Resource creation
Bulk updates
Resource search
Natural-language Resource creation
Resource templates
Resource cloning
Transactional updates
Resource versioning
AI-assisted Resource editing

These capabilities are outside the scope of ENG-030 v0.1.

Relationship to Phase 7

ENG-030 implements the Resource Agent in the Phase 7 Agent Architecture:

Orchestrator Agent
        |
        v
Resource Agent
        |
        v
AtlasProject

The Resource Agent is the first domain-specialized Agent built on the
ENG-028 Agent Runtime and coordinated by the ENG-029 Orchestrator.

Closing Statement

The Resource Agent provides an agent-facing interface to Atlas Resource
operations without duplicating the Resource domain model.

AtlasProject remains the authoritative owner of Resource integrity.

The Resource Agent coordinates.

AtlasProject enforces.

AtlasResource represents.

AtlasResourceRegistry stores.

This separation keeps the Agent Runtime modular while allowing future
AI-powered Resource operations to evolve without weakening the Atlas core.
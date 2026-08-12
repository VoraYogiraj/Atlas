# ENG-031 — Registry Agent

**Document ID:** ENG-031  
**Title:** Registry Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-008, ENG-010, ENG-021, ENG-028, ENG-029

---

# Purpose

This specification defines the Registry Agent used by the Atlas Agent
Runtime.

The Registry Agent provides agent-facing access to Resource Registry
operations.

The Registry Agent does not replace AtlasResourceRegistry or AtlasProject.

It provides controlled query and registry operations through the existing
Atlas domain model.

---

# Scope

This specification defines:

- Registry Agent identity
- Resource lookup
- Required Resource lookup
- Resource existence checks
- Classification queries
- Resource counting
- Resource listing
- Project-scoped registry access
- Registry result traceability

This specification does not define:

- Resource creation
- Resource updates
- Resource deletion
- Relationship management
- Classification registration
- Semantic reasoning
- Validation
- Constraint evaluation
- Persistence
- AI model behavior

Resource mutation is owned by ENG-030 — Resource Agent.

---

# Definition

The **Registry Agent** is a specialized Atlas Agent responsible for
querying and inspecting the Resource Registry.

It provides registry information through the Agent Runtime without creating
a second registry.

---

# Architecture

```text
Agent Request
      |
      v
Registry Agent
      |
      v
AtlasProject
      |
      v
AtlasResourceRegistry
      |
      v
Registry Result

The Registry Agent is read-oriented in ENG-031 v0.1.

Relationship to ENG-028

ENG-028 defines the common Agent Runtime.

The Registry Agent implements that runtime for Resource Registry
operations.

It uses:

AtlasAgent
AtlasAgentRequest
AtlasAgentResult
AtlasAgentContext
AtlasAgentStatus
Relationship to ENG-029

The Orchestrator may route registry requests to the Registry Agent.

Orchestrator
      |
      v
Registry Agent
      |
      v
AtlasProject
      |
      v
Resource Registry
Relationship to ENG-030

ENG-030 owns Resource mutations.

Resource Agent
    |
    +-- create
    +-- update
    +-- delete

ENG-031 owns registry queries.

Registry Agent
    |
    +-- get
    +-- require
    +-- contains
    +-- classify query
    +-- count
    +-- list

The two agents therefore have distinct responsibilities.

Identity

The Registry Agent shall use:

id:
registry-agent

name:
Registry Agent
Project Context

Registry operations require an AtlasProject in Agent Context.

Example:

AtlasAgentContext(
    project=project,
)

The Registry Agent shall not operate against a global registry.

Supported Actions

ENG-031 v0.1 supports:

get_resource
require_resource
contains_resource
resources_for_classification
resource_count
list_resources
get_resource

The get_resource action shall delegate to:

project.get_resource(resource_id)

Metadata:

resource_id

A found Resource produces:

COMPLETED

with the Resource as output.

A missing Resource produces:

COMPLETED

with:

output = None

A missing Resource is not itself an execution failure.

require_resource

The require_resource action shall delegate to:

project.require_resource(resource_id)

A found Resource produces:

COMPLETED

with the Resource as output.

A missing Resource produces:

FAILED

with an explanatory error.

contains_resource

The contains_resource action shall determine whether a Resource is
registered in the Project Registry.

Metadata:

resource_id

The operation returns:

COMPLETED

with:

output = True

or:

output = False
resources_for_classification

The resources_for_classification action shall delegate to the Project's
classification query:

project.resources_for_classification(
    classification_id
)

Metadata:

classification_id

The output is a list of Resources.

Resource order shall match Project Registry order.

resource_count

The resource_count action shall return:

project.resource_count

The output is an integer.

list_resources

The list_resources action shall return Resources in Registry order.

The Agent shall not expose the Registry's internal dictionary.

The output shall be a new list.

Mutating the returned list shall not modify the Registry.

Project Boundary

The Registry Agent shall query only the Project supplied through Agent
Context.

A Resource registered in another Project shall not appear in the current
Project's registry queries.

Registry Ownership

The Registry Agent does not own the Resource Registry.

The Project owns the registry.

The Registry Agent only queries it through the Project/domain API.

No Mutation

ENG-031 v0.1 is query-oriented.

The Registry Agent shall not:

Create Resources
Modify Resources
Delete Resources
Modify Resource Classification
Modify Relationships
Modify Semantic Tags
Modify Categories
Modify Properties
Modify Lifecycle
Missing Project

If an Agent Request does not contain an AtlasProject in its context, the
Registry Agent shall return:

FAILED

with an explanatory error.

Missing Metadata

Required operation metadata must be present.

Missing required metadata produces:

FAILED

with an explanatory error.

Unsupported Action

An unsupported action produces:

FAILED

with an explanatory error.

The Registry Agent shall not infer an alternative action.

Traceability

Every Registry Agent Result shall preserve:

agent_id
request_id
status
output
error

The Request ID shall remain unchanged.

Non-AI Implementation

ENG-031 v0.1 is deterministic.

The Registry Agent does not require an AI model or AI provider.

Future AI-powered registry reasoning may be introduced above the
deterministic registry API.

Registry Integrity

The Registry Agent must use the existing Registry/Project APIs rather than
directly mutating internal state.

This preserves:

Project boundaries
Registry integrity
Classification integrity
Resource identity
Resource ordering
Future Evolution

Future versions may introduce:

Resource search
Full-text search
Semantic search
Category filtering
Tag filtering
Multi-criteria queries
Pagination
Sorting
Query planning
Graph-aware queries
AI-powered registry search

These capabilities are outside the scope of ENG-031 v0.1.

Relationship to Phase 7

ENG-031 implements the Registry Agent in the Phase 7 Agent Architecture:

Orchestrator Agent
        |
        v
Registry Agent
        |
        v
AtlasProject
        |
        v
AtlasResourceRegistry

The Registry Agent is the registry-query specialist of the Atlas Agent
Runtime.

Closing Statement

The Registry Agent provides controlled agent access to registered Atlas
Resources.

The Project owns the registry.

The Resource Registry stores and indexes Resources.

The Registry Agent queries.

The Resource Agent mutates.

This separation prevents duplicate domain logic and preserves the integrity
of the Atlas Resource Engine while enabling future AI-assisted registry
intelligence.
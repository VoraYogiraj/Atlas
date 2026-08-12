# ENG-033 — Relationship Agent

**Document ID:** ENG-033  
**Title:** Relationship Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-005, ENG-011, ENG-012, ENG-013, ENG-014, ENG-022, ENG-028, ENG-029

---

# Purpose

This specification defines the Relationship Agent used by the Atlas Agent
Runtime.

The Relationship Agent provides agent-facing access to the Atlas
Relationship and Resource Graph model.

It allows Agents to:

- Create Relationships
- Inspect Relationships
- Query Relationships
- Navigate the Resource Graph
- Traverse connected Resources
- Determine graph reachability
- Remove Relationships

The Relationship Agent does not replace AtlasRelationship,
AtlasResourceGraph, or AtlasProject.

---

# Scope

This specification defines:

- Relationship Agent identity
- Relationship creation
- Relationship lookup
- Relationship queries
- Incoming Relationships
- Outgoing Relationships
- Relationship type queries
- Resource neighbors
- Graph traversal
- Graph reachability
- Relationship removal
- Project-scoped graph operations
- Traceable Agent Results

This specification does not define:

- Automatic relationship inference
- AI relationship prediction
- Natural-language graph reasoning
- Semantic inference
- Validation
- Constraints
- Persistence
- Relationship ontology generation

---

# Definition

The **Relationship Agent** is a specialized Atlas Agent responsible for
managing and querying directed engineering Relationships between Atlas
Resources.

It operates through the existing AtlasProject and Resource Graph APIs.

---

# Architecture

```text
Orchestrator
      |
      v
Relationship Agent
      |
      v
AtlasProject
      |
      v
AtlasResourceGraph
      |
      v
AtlasRelationship

The Agent does not create a second graph.

Relationship to ENG-028

ENG-028 defines the common Agent Runtime.

ENG-033 specializes that runtime for the Atlas relationship and graph domain.

Relationship to ENG-029

The Orchestrator routes relationship requests to the Relationship Agent.

Orchestrator
      |
      v
Relationship Agent
      |
      v
AtlasProject
      |
      v
Resource Graph
Relationship to ENG-030

The Resource Agent owns Resource lifecycle operations.

The Relationship Agent owns Relationship operations.

Resource Agent
    |
    +-- create Resource
    +-- update Resource
    +-- delete Resource

Relationship Agent
    |
    +-- create Relationship
    +-- query Relationship
    +-- remove Relationship
    +-- traverse Graph
Identity

The Relationship Agent shall use:

id:
relationship-agent

name:
Relationship Agent
Project Context

Relationship operations require an AtlasProject in Agent Context.

Example:

AtlasAgentContext(
    project=project,
)

The Relationship Agent shall operate only against the supplied Project.

Request Metadata

The following metadata keys are defined.

Relationship operations
relationship
Resource-specific queries
resource
Two-resource queries
first_resource
second_resource
Relationship type queries
relationship_type
Traversal
resource
max_depth
Supported Actions

ENG-033 v0.1 supports:

add_relationship
get_relationships_between
relationships_for_resource
outgoing_relationships
incoming_relationships
relationships_by_type
neighbors
connected
traverse
reachable
remove_relationship
relationship_count
add_relationship

The add_relationship action shall delegate to:

project.add_relationship(relationship)

The Project and Graph shall remain responsible for:

Endpoint Resource ownership
Duplicate Relationship detection
Graph integrity
Project boundaries

A successful operation returns:

COMPLETED

with the registered Relationship as output.

get_relationships_between

Metadata:

first_resource
second_resource

The operation shall return:

project.graph.get_between(...)

through the appropriate Project-level relationship API.

Relationship direction shall not restrict this query.

The returned Relationships shall preserve graph registration order.

relationships_for_resource

Metadata:

resource

Returns all Relationships involving the Resource.

Direction is ignored.

The Resource must belong to the Project.

outgoing_relationships

Metadata:

resource

Returns Relationships where the Resource is the source.

Incoming Relationships are excluded.

incoming_relationships

Metadata:

resource

Returns Relationships where the Resource is the target.

Outgoing Relationships are excluded.

relationships_by_type

Metadata:

relationship_type

Returns all Relationships of the specified type.

Relationship registration order shall be preserved.

Empty or whitespace-only relationship types shall produce a FAILED result.

neighbors

Metadata:

resource

Returns connected Resources.

Relationship direction does not restrict connectivity.

The output shall preserve the graph's existing neighbor ordering semantics.

The Relationship Agent shall not deduplicate the result when using the
existing neighbors() API.

connected

Metadata:

first_resource
second_resource

Returns:

True

when the two Resources share a direct Relationship.

Returns:

False

otherwise.

This operation checks direct connectivity only.

It does not perform multi-hop traversal.

traverse

Metadata:

resource
max_depth

Returns Resources discovered by breadth-first graph traversal.

The starting Resource is always included.

max_depth semantics remain those defined by the existing graph:

0
    starting Resource only

1
    starting Resource + direct neighbors

2
    up to two Relationship hops

None
    all reachable Resources

Invalid negative depth values shall produce a FAILED result.

reachable

Metadata:

first_resource
second_resource

Returns:

True

when the target Resource is reachable from the source through the graph.

Traversal remains direction-independent according to the existing graph
model.

A Resource is reachable from itself.

remove_relationship

Metadata:

relationship

The operation shall delegate to:

project.remove_relationship(
    relationship
)

Returns the removed Relationship.

If the Relationship does not exist, the operation returns:

COMPLETED
output = None
relationship_count

Returns:

project.relationship_count

The result is an integer.

Project Integrity

The Relationship Agent shall never directly mutate the Resource Graph's
internal Relationship collection.

All Relationship mutations must pass through AtlasProject.

The existing Project and Graph layers remain responsible for:

Resource membership
Relationship endpoint validity
Duplicate detection
Relationship registration
Relationship removal
Resource Ownership

The Relationship Agent does not own Resources.

The Resource Registry remains the owner of Resource identity and membership.

The graph only connects Resources that belong to its Project.

Relationship Direction

Atlas Relationships are directed.

Example:

Wall
  |
  | contains
  v
Door

The Relationship Agent must preserve:

source
target
relationship_type

Direction must never be silently reversed.

Query Semantics

The Relationship Agent must preserve the existing graph semantics.

In particular:

relationships_for_resource
    → incoming + outgoing

outgoing_relationships
    → source only

incoming_relationships
    → target only

connected
    → direct relationship only

reachable
    → multi-hop traversal
Traversal Semantics

The Relationship Agent shall delegate traversal to the existing graph
implementation.

It shall not implement a second BFS algorithm.

The graph remains the authoritative traversal engine.

Unsupported Actions

Unknown actions shall return:

FAILED

with an explanatory error.

The Agent shall not infer another Relationship action.

Missing Project

Missing AtlasProject context shall produce:

FAILED

with an explanatory error.

Missing Metadata

Missing required metadata shall produce:

FAILED

with an explanatory error.

Invalid Resource

A Resource from another Project shall not be accepted for relationship
operations.

The existing Project and Graph validation rules remain authoritative.

Traceability

Every Relationship Agent operation shall return an
AtlasAgentResult preserving:

agent_id
request_id
status
output
error
Non-AI Implementation

ENG-033 v0.1 is deterministic.

It does not require an LLM or ML provider.

All relationship behavior is derived from the explicit Resource Graph.

Future AI Evolution

Future versions may introduce:

Relationship inference
Relationship recommendation
Missing relationship detection
Structural dependency reasoning
Semantic graph reasoning
Natural-language graph queries
Graph-based engineering reasoning
AI-generated relationship explanations
Relationship confidence scores

Future inferred Relationships must distinguish:

Explicit

from:

Inferred
Example
Building
   |
   | contains
   v
Floor
   |
   | contains
   v
Room
   |
   | contains
   v
Wall
   |
   | contains
   v
Door

The Relationship Agent may:

neighbors(Room)

returning directly connected Resources.

It may also:

traverse(Room, max_depth=2)

to discover connected Resources within two graph hops.

It may:

reachable(Room, Door)

to determine whether Door is reachable from Room through the graph.

Relationship to Phase 7

ENG-033 implements:

Orchestrator Agent
        |
        v
Relationship Agent
        |
        v
AtlasProject
        |
        v
AtlasResourceGraph
        |
        v
AtlasRelationship

The Relationship Agent provides the bridge between the Agent Runtime and
the Atlas Engineering Graph.

Future Evolution

Future versions may introduce:

Graph query planning
Graph pattern matching
Subgraph extraction
Dependency analysis
Impact analysis
Relationship inference
AI graph reasoning
Engineering graph explanations

These capabilities are outside ENG-033 v0.1.

Closing Statement

Relationships turn independent Atlas Resources into connected engineering
systems.

The Relationship Agent gives the Agent Runtime controlled access to that
graph.

AtlasProject owns the boundary.

AtlasResourceGraph manages connectivity.

AtlasRelationship represents the connection.

The Relationship Agent coordinates these capabilities without duplicating
the underlying graph engine.
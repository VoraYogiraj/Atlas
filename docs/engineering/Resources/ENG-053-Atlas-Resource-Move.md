# ENG-053 — Atlas Resource Move

**Status:** Proposed  
**Phase:** Phase 11 — Resource Editing  
**Depends On:** ENG-052 — Resource Create  
**Previous:** ENG-052 — Resource Create  
**Next:** ENG-054 — Atlas Resource Rotate

---

## 1. Purpose

ENG-053 introduces the **Move** capability within Phase 11 — Resource Editing.

Phase 11 is responsible for enabling users to edit canonical Atlas Resources.

The Phase 11 roadmap defines the capability sequence as:

1. Create
2. Move
3. Rotate
4. Scale
5. Delete
6. Duplicate

The Phase 11 deliverable is:

> Resources become editable.

ENG-053 is therefore the next capability after ENG-052 — Resource Create.

The historical roadmap establishes **Move** as a Phase 11 capability, but does not yet establish the exact canonical state semantics of what “moving a Resource” means.

This specification therefore defines the architectural contract and the unresolved semantic boundary that must be settled before the RED tests are frozen.

---

# 2. Architectural Position

The Atlas architecture is:

```text
Canonical Atlas Core
        ↓
Atlas Application Boundary
        ↓
Commands / Queries
        ↓
UI / 3D / Agents / External Interfaces

Engineering mutation must enter Atlas through the existing application boundary.

The application boundary must remain thin and must not become a second engineering model.

The intended flow is:

User / UI / Agent
        ↓
AtlasCommand
        ↓
AtlasApplication.execute()
        ↓
Canonical Atlas domain state
        ↓
Canonical Resource Registry / Project

ENG-053 must preserve this architecture.

3. Relationship to ENG-052

ENG-052 introduced Resource Create.

The established creation flow is:

AtlasCommand
    ↓
AtlasApplication
    ↓
AtlasResource
    ↓
AtlasProject.resources
    ↓
AtlasResourceRegistry

ENG-053 must extend the existing application boundary rather than introduce a competing mutation mechanism.

The operation must therefore be represented as an application command.

Proposed command identity:

move_resource

Example conceptual request:

AtlasCommand(
    name="move_resource",
    payload={
        ...
    },
)

The exact payload contract is intentionally not frozen until Resource Move semantics are established.

4. Canonical Resource Model

The current AtlasResource implementation establishes the following canonical state:

AtlasResource
├── AtlasID
├── Classification
├── Name
├── Properties
├── Relationships
├── Metadata
├── Semantic Tags
├── Categories
└── Lifecycle

The current Resource model does not define:

position
location
transform
geometry
translation
rotation
scale

ENG-053 must not invent these fields merely to satisfy the word "Move".

Adding spatial state directly to AtlasResource without an established architectural decision would change the canonical Resource model without specification authority.

5. Critical Semantic Boundary

ENG-053 must distinguish between:

AtlasResource

and:

AtlasSceneNode

The Phase 10 3D Workspace already contains transformation state on SceneNode.

ENG-051 — Basic Editing operates on:

AtlasScene
    ↓
AtlasSceneNode
    ↓
position / rotation / scale

That capability is presentation/workspace editing.

It does not establish that canonical Atlas Resources themselves own spatial transformation state.

Therefore:

ENG-051 Basic Editing
    ≠
ENG-053 Resource Move

ENG-053 must not silently implement Resource Move by delegating to:

AtlasBasicEditing.translate(...)

unless a later specification explicitly establishes that relationship.

6. Canonical Identity

Any Resource mutation introduced by ENG-053 must address the canonical Resource by:

AtlasID

The operation must not establish a new Resource identity.

The UI, Scene, Agent, or other caller must not create a parallel Resource representation.

The canonical identity chain remains:

AtlasID
    ↓
AtlasProject
    ↓
AtlasResourceRegistry
    ↓
AtlasResource

Viewport identifiers such as node_id remain presentation/Scene identities and must not replace AtlasID.

7. Registry Ownership

ENG-053 must mutate the existing canonical Resource managed by the Project/Resource Registry.

It must not:

create a duplicate Resource,
create a temporary Resource model,
create a Scene-owned Resource model,
create a second Resource Registry,
create a second Resource graph,
bypass the canonical Project,
bypass the canonical Resource Registry.

The Resource Registry remains the authoritative collection of Resources.

8. Application Boundary

ENG-053 must use the existing:

AtlasApplication.execute()

boundary.

Commands represent:

user or system intent

and do not themselves contain Atlas domain rules.

The command layer must remain declarative.

Conceptually:

AtlasCommand
    ↓
AtlasApplication
    ↓
Canonical domain mutation

The application layer must not evolve into a second domain model.

9. Resource Move Semantics
9.1 Established Fact

The roadmap establishes:

Phase 11
    Move

as the next Resource Editing capability.

9.2 Not Yet Established

The historical specification currently available does not establish whether Resource Move means:

changing canonical spatial coordinates,
changing a Resource hierarchy location,
changing a containment relationship,
changing an engineering property representing location,
changing a future spatial component,
changing another canonical Resource-associated state.

The current AtlasResource implementation provides no canonical spatial field.

Therefore these semantics must not be invented inside implementation code.

10. Semantic Decision Required Before RED

Before tests/test_resource_move.py is frozen, Atlas must establish:

A. What is being moved?

The specification must identify the canonical state affected by Move.

B. Who owns that state?

The owning domain object/component must be identified.

C. What identifies the target?

The operation must use canonical AtlasID identity.

D. What does the input represent?

The specification must explicitly establish whether movement is:

absolute,
relative/delta,
hierarchical,
or another defined operation.
E. What validation applies?

The specification must define which values are valid.

F. What is atomic?

Invalid Move requests must leave canonical state unchanged.

G. What other state may change?

The specification must identify whether relationships, properties, metadata, semantics, lifecycle, or other state are affected.

No additional state may be mutated implicitly.

11. Future-Ready Requirement

ENG-053 must be implemented as the smallest architecturally complete capability, not the smallest implementation capable of satisfying a test.

"Future-ready" means:

canonical ownership is correct;
AtlasID identity remains authoritative;
the Resource Registry remains canonical;
the Application boundary remains thin;
mutation semantics are explicit;
invalid operations are atomic;
behavior is deterministic;
the implementation can support later Rotate, Scale, Delete, Duplicate, validation, constraints, persistence, agents, UI, and AI without requiring a competing Resource model.

Future-ready does not mean implementing future systems prematurely.

The following are outside ENG-053 unless independently specified:

undo/redo,
history,
event sourcing,
transaction framework,
constraint engine,
validation runtime expansion,
persistence changes,
serialization changes,
AI/LLM behavior,
agent orchestration,
renderer behavior,
Three.js integration,
picking/raycasting,
multi-selection,
snapping.
12. Determinism

Given identical canonical state and identical Move input:

Resource State A
     +
Move Request X
     ↓
Resource State B

must always produce the same observable canonical result.

The result must not depend on:

renderer state,
UI state,
timing,
randomness,
external mutable state,
implicit Scene state.
13. Atomicity

ENG-053 must validate before mutation.

For an invalid request:

Initial Resource State
        ↓
Invalid Move
        ↓
same Resource State

No partial mutation is permitted.

Examples of invalid requests must leave the Resource unchanged.

Atomicity must include all state owned by the Move operation.

14. Resource Isolation

ENG-053 must not accidentally mutate unrelated Resource state.

Unless explicitly specified, Move must preserve:

AtlasID
classification
name
properties
relationships
metadata
semantic tags
categories
lifecycle

Only the explicitly specified Move-owned state may change.

15. Scene Independence

ENG-053 must not make the 3D Scene the canonical engineering model.

The existing separation remains:

Canonical Engineering State
        ↑
        │
Application Boundary
        │
        ↓
3D Workspace / Scene Presentation

A SceneNode may visually represent a Resource, but the viewport representation must not silently become the authoritative Resource state.

If a future architecture establishes a synchronization relationship between canonical spatial state and Scene state, that synchronization must be explicitly specified.

16. Selection Independence

Selection remains an application/workspace concern.

ENG-053 must not:

create selection state,
redefine selection,
require multi-selection,
mutate selection as a side effect.

A caller may obtain a Resource identity from selection and submit a Move command, but selection itself remains outside ENG-053.

17. Renderer Independence

ENG-053 must not depend on:

Three.js,
WebGL,
WebGPU,
OpenGL,
renderer-specific objects,
raycasters,
visual meshes,
viewport handles.

The canonical mutation must be testable without rendering technology.

18. Agent / AI Independence

ENG-053 must be deterministic without:

LLMs,
AI,
agents,
orchestration,
inference,
prompts.

Future agents may issue a valid Move command.

They must not redefine Move semantics.

The canonical deterministic Atlas model remains authoritative.

19. Proposed Public Application Surface

The application boundary is expected to expose the capability through:

AtlasCommand(
    name="move_resource",
    payload={...},
)

The command name is proposed for ENG-053.

The exact payload schema must be frozen only after the canonical Move semantics are established.

No convenience API should be introduced merely to duplicate AtlasApplication.execute().

20. Focused Test Contract

The focused test file shall be:

tests/test_resource_move.py

Focused command:

pytest tests/test_resource_move.py -q

The RED contract must verify, at minimum:

Construction / Command Surface
move_resource can be represented as an AtlasCommand.
The command remains immutable according to the existing command contract.
Application Boundary
Move executes through AtlasApplication.execute().
Unknown/invalid command types remain rejected.
Existing command behavior remains unchanged.
Canonical Identity
Targeting uses AtlasID.
The canonical Resource identity does not change.
Canonical Ownership
The operation mutates the established Move-owned state.
No second Resource representation is created.
Mutation
Valid Move changes exactly the state defined by the specification.
Unrelated Resource state remains unchanged.
Missing Resource
Unknown Resource identity is rejected using the established Project/Registry lookup semantics.
The canonical state remains unchanged.
Invalid Input
Invalid Move input is rejected.
Invalid operations are atomic.
Determinism
Identical initial state and identical Move request produce identical observable state.
Isolation
No SceneNode mutation occurs unless explicitly established by specification.
No Selection mutation occurs.
No renderer dependency exists.
No AI/agent dependency exists.
21. RED Phase Rule

The RED tests must be written against the finalized ENG-053 contract.

They must not be weakened merely to accommodate an implementation.

If implementation reality conflicts with the intended architectural contract:

Specification
    ↓
revise specification
    ↓
revise RED contract
    ↓
implementation

The reverse direction is prohibited:

implementation
    ↓
change specification

merely to make the tests pass.

22. Implementation Principle

The implementation must provide the smallest complete architectural slice necessary to establish Resource Move.

This means:

Required
    ↓
canonical state ownership
    +
command boundary
    +
canonical Resource resolution
    +
deterministic mutation
    +
atomic validation
    +
tests

It must not introduce speculative infrastructure.

The implementation should nevertheless leave clean boundaries for:

Move
  ↓
Rotate
  ↓
Scale
  ↓
Delete
  ↓
Duplicate

and for future:

Validation
Constraints
History
Persistence
Agents
UI
AI

without requiring a second Resource model.

23. Architecture Invariants

ENG-053 must preserve all existing Atlas invariants:

AtlasID remains canonical engineering identity.
AtlasProject remains the Resource ownership boundary.
AtlasResourceRegistry remains the canonical Resource registry.
AtlasApplication remains the application boundary.
Commands represent intent.
Domain rules remain outside commands.
Scene remains presentation/application state.
SceneNode remains distinct from AtlasResource.
Selection remains separate from mutation.
Renderer remains separate from canonical engineering state.
AI/agents remain consumers of deterministic Atlas semantics.
No competing Resource model is introduced.
24. Explicit Non-Goals

ENG-053 does not include:

Resource Create
Resource Rotate
Resource Scale
Resource Delete
Resource Duplicate
SceneNode transformation
Camera manipulation
Navigation
Selection
Gizmos
Picking
Raycasting
Rendering
Three.js integration
Undo/redo
History
Transactions
Persistence
Serialization
Import/export
Agent implementation
AI/LLM implementation
Constraint implementation
Validation-runtime expansion
25. Completion Criteria

ENG-053 is complete only when:

Specification
Move semantics are explicitly defined.
Canonical state ownership is established.
Input and output semantics are established.
Validation rules are established.
Atomicity requirements are established.
RED
tests/test_resource_move.py exists.
Tests fail for the expected missing implementation reasons.
Tests are not weakened to fit an implementation.
Implementation
Move is exposed through the existing application boundary.
Canonical Resource identity is preserved.
Canonical ownership is preserved.
No competing Resource model exists.
Mutation is deterministic.
Invalid operations are atomic.
No unrelated subsystems are modified.
GREEN
Focused ENG-053 tests pass.
Regression
Full Atlas test suite passes.
No existing behavior regresses.
No unrelated test failures are introduced.
Checkpoint
ENG-053 documentation is marked complete.
Implementation, tests, and specification agree.
Repository is clean and checkpointed.
26. Current Specification State

At the time this document is created:

ENG-053 capability assignment
    ✅ Established
        Phase 11 → Move


Architectural boundaries
    ✅ Established


Application boundary
    ✅ Established


Canonical Resource identity
    ✅ Established


Canonical Resource Registry
    ✅ Established


Resource spatial/Move state
    ⚠ Not yet established


Move input semantics
    ⚠ Not yet established


Move mutation semantics
    ⚠ Not yet established


RED contract
    ⏳ Blocked until Move semantics are frozen


Implementation
    ⏳ Not started

Therefore:

ENG-053 is Proposed, not yet RED.

No production code or focused tests should be written until the unresolved Move semantics are explicitly established.

27. Architectural Principle

ENG-053 must not answer:

"How can we make a Resource move?"

by adding whatever state is convenient.

It must answer:

"What does movement mean in the canonical Atlas engineering model, who owns that meaning, and how does the existing application boundary express it?"

Once that answer is explicit, the implementation should be straightforward.

The goal is not merely to make Resources movable.

The goal is to make Resource mutation a first-class, canonical, deterministic Atlas capability that future editing, validation, constraints, agents, UI, and AI can build upon without replacing the foundation.
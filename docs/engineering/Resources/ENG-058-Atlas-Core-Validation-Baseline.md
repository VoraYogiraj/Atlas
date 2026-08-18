# ENG-058 — Atlas Core Validation Baseline

**Document ID:** ENG-058  
**Title:** Atlas Core Validation Baseline  
**Version:** 0.1.0  
**Status:** Proposed  
**Phase:** Phase 12 — Validation  
**Previous:** ENG-057 — Resource Duplicate  
**Depends On:** ENG-001 through ENG-057  
**Scope:** Validation of the implemented Atlas v0.1 architecture and its established contracts

---

## 1. Purpose

ENG-058 begins Phase 12 — Validation.

Phase 12 exists to verify the Atlas architecture after completion of the Phase 11 Resource Editing capability set.

The Phase 12 objective is:

> Verify Atlas architecture.

The validation program includes:

- Unit tests
- Integration tests
- UI tests
- Manual testing

The Phase 12 deliverable is:

> Stable MVP.

ENG-058 establishes the first validation baseline for the implemented Atlas core and the Resource Editing contracts completed through ENG-057.

ENG-058 does not introduce a new engineering capability.

It verifies that the capabilities already established by previous engineering milestones remain internally consistent, deterministic, isolated, and compatible.

---

## 2. Architectural Position

The validation target is the existing Atlas architecture.

```text
Canonical Engineering Model
        │
        ├── AtlasID
        ├── AtlasResource
        ├── Classification
        ├── Properties
        ├── Semantics
        ├── Lifecycle
        ├── Relationships
        ├── Resource Registry
        ├── AtlasProject
        ├── Validation / Constraints
        └── Persistence / Exchange
                │
                ▼
        AtlasApplication
                │
                ▼
        UI / Workspace / Scene
                │
                ▼
        Agents / AI / External Interfaces

ENG-058 validates the boundaries between these layers.
The canonical engineering model remains authoritative.
Validation must not create a second model, registry, graph, spatial state system, or application command system.
3. Phase 11 Completion Baseline
ENG-058 begins from the completed Phase 11 Resource Editing sequence:
ENG-052 — Resource Create
        ↓
ENG-053 — Resource Move
        ↓
ENG-054 — Resource Rotate
        ↓
ENG-055 — Resource Scale
        ↓
ENG-056 — Resource Delete
        ↓
ENG-057 — Resource Duplicate
The established executable baseline at the beginning of ENG-058 is:
Full regression:
1925 passed
0 failed
This baseline must remain reproducible.
ENG-058 must not weaken, remove, or reinterpret existing passing contracts merely to make new validation tests pass.
4. Scope
ENG-058 validates the existing architecture in the following areas.
4.1 Canonical Resource Identity
Verify:
Every Resource has a stable AtlasID.
AtlasID remains the canonical engineering identity.
Resource identity is not replaced by viewport node_id.
Duplicate Resources receive distinct identities.
Invalid identity inputs are rejected.
Identity is preserved across supported operations.
4.2 Resource Registry Integrity
Verify:
The canonical Resource Registry remains authoritative.
Resources are registered exactly once.
Resource lookup is deterministic.
Unknown Resources are rejected where required.
Create, duplicate, and delete operations preserve registry integrity.
UI or Scene structures do not create competing Resource registries.
4.3 Project Ownership
Verify:
AtlasProject remains the owner of canonical Resource state.
Resource operations do not create an alternative ownership model.
Application-layer operations delegate to canonical project/domain state.
UI components do not become owners of engineering Resources.
4.4 Relationship Integrity
Verify:
Relationships remain owned by the canonical relationship graph.
Resource editing does not silently create relationships.
Resource deletion removes relationships according to the established delete contract.
Resource duplication does not clone relationships.
Existing relationship identity is preserved when unrelated operations occur.
Relationship counts remain correct.
4.5 Spatial State Integrity
Verify the existing project-scoped spatial state:
AtlasID
   ├── Position
   ├── Rotation
   └── Scale
Verify:
Spatial state is keyed by AtlasID.
Resource creation initializes deterministic spatial defaults.
Move changes Position only.
Rotate changes Rotation only.
Scale changes Scale only.
Delete removes all spatial state belonging to the Resource.
Duplicate copies spatial state to the new AtlasID.
Spatial state remains independent between Resources.
Spatial state does not become geometry stored directly on AtlasResource.
4.6 Resource State Isolation
Verify:
Resource mutations affect only their intended Resource.
Duplicate mutable state is independent.
Metadata is independently mutable.
Properties are independently mutable.
Semantic membership is independently mutable.
Lifecycle state remains Resource-local.
Unrelated Resources remain unchanged.
4.7 Lifecycle Integrity
Verify:
Resource lifecycle follows the established lifecycle model.
Creation starts in the appropriate initial state.
Duplicate creation starts as a new Resource lifecycle rather than blindly copying terminal lifecycle state.
Delete follows the established deletion contract.
Invalid lifecycle transitions remain rejected.
Resource editing does not introduce a second lifecycle system.
4.8 Validation and Atomicity
Verify the existing validation boundary:
Input
  ↓
Validate
  ↓
Mutate canonical state
For invalid operations:
Invalid Input
     ↓
Rejected
     ↓
Canonical State Unchanged
Verify:
Invalid types are rejected.
Invalid identifiers are rejected.
Invalid structures are rejected.
Invalid spatial values are rejected.
Invalid lifecycle operations are rejected.
Invalid operations do not partially mutate canonical state.
Existing validation behavior remains deterministic.
ENG-058 does not create a second validation engine.
Existing validation infrastructure remains authoritative.
4.9 Application Boundary
Verify:
User / UI / Agent / External System
              ↓
         AtlasCommand
              ↓
       AtlasApplication
              ↓
         AtlasProject
              ↓
       Canonical Atlas State
Verify:
Commands represent intent.
Commands do not contain domain rules.
AtlasApplication remains an application boundary rather than a second domain model.
Canonical Resource state remains owned by AtlasProject/domain structures.
Unsupported commands remain explicitly rejected.
Existing command contracts remain compatible.
4.10 UI and 3D Boundary
The Phase 10 UI/3D architecture established that presentation state must remain separate from canonical engineering state.
Verify:
Scene owns scene-node presentation structure.
Scene Nodes may reference Resources by AtlasID.
Scene does not become a second Resource Registry.
Selection remains separate from Resource ownership.
Gizmo state remains separate from engineering mutation.
Renderer-independent application state remains renderer-independent.
Basic editing and Resource editing do not collapse into one ownership system.
UI state does not silently become engineering truth.
4.11 Agent / AI Boundary
Verify:
Agents do not become canonical owners of engineering state.
Agent operations continue through established application/domain boundaries.
AI-generated information does not silently replace canonical Resource state.
Validation remains a deterministic Atlas responsibility.
No ENG-058 behavior depends on an LLM, external AI service, or model output.
5. Core Invariants
ENG-058 establishes the following validation invariants.
Invariant 1 — Single Canonical Resource Model
There is one canonical AtlasResource model.
No subsystem may introduce a competing engineering Resource representation.
Invariant 2 — Single Canonical Registry
The canonical Resource Registry remains authoritative.
Invariant 3 — AtlasID Is Engineering Identity
AtlasID remains the identity of an engineering Resource.
node_id remains a viewport/SceneNode identity.
Invariant 4 — Project Owns Canonical Resource State
AtlasProject remains the domain owner of Resources and their canonical relationships and spatial state.
Invariant 5 — Relationships Are Explicit
Resource operations do not implicitly invent relationships.
Invariant 6 — Spatial State Is Separate
Position, Rotation, and Scale remain project-scoped spatial state keyed by AtlasID.
Invariant 7 — Validation Precedes Mutation
Invalid input cannot partially mutate canonical state.
Invariant 8 — Resource Isolation
A Resource operation must not mutate unrelated Resources.
Invariant 9 — UI Isolation
Presentation state must not become a competing engineering model.
Invariant 10 — Determinism
Equivalent initial state plus equivalent operation sequence produces equivalent observable canonical state.
Invariant 11 — Additive Architecture
Validation adds verification coverage without requiring replacement of the established Atlas foundation.
6. Validation Matrix
ENG-058 must validate the following operation families:
Capability	Primary validation
Resource Create	identity, registration, defaults, ownership
Resource Move	position isolation, validation, determinism
Resource Rotate	rotation isolation, validation, determinism
Resource Scale	scale isolation, validation, determinism
Resource Delete	registry cleanup, relationship cleanup, spatial cleanup
Resource Duplicate	identity, state isolation, spatial copy, relationship exclusion
Relationships	graph integrity and identity preservation
Semantics	classification/tag/category preservation and isolation
Lifecycle	valid state transitions and invalid transition rejection
Application	command boundary and domain ownership
Scene/UI	engineering/presentation separation
Agents	boundary and canonical-state ownership
Validation	rejection and atomicity
Full system	regression compatibility


7. Testing Strategy
ENG-058 follows the established Atlas testing discipline.
7.1 Unit Validation
Validate individual domain contracts independently.
Examples:
Resource
Registry
Classification
Properties
Semantics
Lifecycle
Relationships
Spatial State
Validation
Constraints
7.2 Integration Validation
Validate interactions between:
AtlasApplication
        ↓
AtlasProject
        ↓
Resource Registry
        ↓
Relationship Graph
        ↓
Spatial State
7.3 UI Boundary Validation
Validate that existing UI/3D components remain isolated from canonical engineering ownership.
These tests are architectural tests, not renderer visual tests.
7.4 Manual Validation
Manual validation belongs to the broader Phase 12 validation program.
ENG-058 establishes the automated baseline required before manual validation becomes meaningful.
8. Test Organization
ENG-058 must prefer extending existing focused test suites where a contract already exists.
No duplicate test framework or parallel validation framework should be introduced.
Where a dedicated architectural validation suite is necessary, it must be explicitly named and remain focused on cross-cutting invariants.
Potential validation suite:
tests/test_core_validation.py
The suite must not duplicate every existing operation test.
Its purpose is to verify cross-capability invariants that cannot be adequately expressed by one isolated ENG milestone.
9. Expected RED State
Before ENG-058 implementation, the new focused validation suite is expected to fail where the required cross-capability invariant is not yet explicitly represented or where the repository does not expose the necessary verification boundary.
The RED phase must distinguish:
Expected contract failure
        vs
Existing repository/test defect
        vs
Incorrect test assumption
A test/API mismatch must be corrected rather than forcing production code to satisfy an invented interface.
Existing passing tests must remain untouched.
10. Implementation Constraints
ENG-058 implementation must:
add only the minimum validation capability required by this specification
preserve all existing public APIs
preserve ENG-052 through ENG-057 behavior
preserve Phase 10 UI/3D boundaries
preserve existing validation infrastructure
avoid introducing a second validation engine
avoid introducing a second Resource Registry
avoid introducing a second Resource model
avoid introducing a second relationship graph
avoid moving spatial state into AtlasResource
avoid introducing renderer dependencies
avoid introducing AI dependencies
avoid changing Resource semantics
avoid changing established lifecycle semantics
avoid changing existing command contracts unless a contradiction is demonstrated
avoid unrelated refactoring
No speculative architecture is permitted.
11. Non-Goals
ENG-058 does not implement:
new Resource capabilities
new geometry
BIM functionality
rendering
Three.js integration
new UI components
new Scene behavior
new agent types
new AI models
persistence redesign
exchange redesign
collaboration
undo/redo
transaction history
provenance redesign
new semantic systems
new constraint systems
general-purpose test framework replacement
Those capabilities remain outside this milestone unless already implemented by previous ENG specifications.
12. Completion Criteria
ENG-058 is complete when:
The Phase 0–11 specification history has been reconciled with the implemented repository baseline.
The existing 1925-test baseline remains green.
ENG-052 through ENG-057 remain green.
Cross-capability Resource invariants are explicitly tested.
Canonical Resource ownership is verified.
Registry integrity is verified.
AtlasID identity integrity is verified.
Relationship integrity is verified.
Spatial state integrity is verified.
Resource isolation is verified.
Lifecycle integrity is verified.
Validation atomicity is verified.
Application/domain boundaries are verified.
UI/engineering boundaries are verified.
Agent/AI boundaries are verified.
Determinism is verified.
No duplicate canonical architecture is introduced.
Focused ENG-058 tests pass.
Phase 11 regression passes.
Full regression passes.
Documentation reflects the verified state.
ENG-058 is checkpointed.
13. Expected Validation Flow
Phase 0–11 specification history
             ↓
Phase 0–11 implementation
             ↓
Existing test baseline
             ↓
ENG-058 cross-capability contracts
             ↓
             RED
             ↓
Minimum validation implementation
             ↓
            GREEN
             ↓
Phase 11 regression
             ↓
Full regression
             ↓
Manual validation
             ↓
ENG-058 checkpoint
14. Architectural Success Condition
The purpose of ENG-058 is not simply to increase the number of passing tests.
The success condition is:
The Atlas foundation implemented through Phase 11 can be validated as one coherent architecture without requiring competing models, duplicated ownership, hidden state, or special-case exceptions between milestones.

The existing architecture must remain understandable as:
Resource
   ↓
Registry
   ↓
Relationships
   ↓
Semantics
   ↓
Validation / Constraints
   ↓
Agents
   ↓
Application / UI / AI
with canonical engineering state remaining authoritative beneath the presentation and execution layers.        
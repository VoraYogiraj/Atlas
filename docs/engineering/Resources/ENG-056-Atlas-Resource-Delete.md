ENG-056 — Atlas Resource Delete
Status: Proposed
Phase: Phase 11 — Resource Editing
Depends On: ENG-055 — Atlas Resource Scale
Previous: ENG-055 — Atlas Resource Scale
Next: ENG-057 — TBD
1. Purpose
ENG-056 introduces the canonical Resource Delete operation to Atlas.
The operation removes an identified AtlasResource from the canonical AtlasProject while preserving project integrity and removing all canonical state owned by that Resource.
Delete is a project-level canonical operation.
It is not a Scene operation, UI operation, renderer operation, or presentation-layer operation.
2. Architectural Position
ENG-056 extends the existing canonical Resource lifecycle:
Resource Create
      ↓
Resource Move
      ↓
Resource Rotate
      ↓
Resource Scale
      ↓
Resource Delete
The canonical architecture remains:
AtlasApplication
      │
      ├── Commands / Queries
      │
      │    delete_resource
      │
      ↓
AtlasProject
   ┌───────────────┬───────────────────┐
   │               │                   │
   ↓               ↓                   ↓
Resource       Relationship        Spatial State
Registry          Graph              Registry
   │               │                   │
AtlasResource   Relationships     AtlasID → State
                                      │
                              ┌───────┼────────┐
                              ↓       ↓        ↓
                           Position Rotation Scale
ENG-056 does not introduce another Resource registry, graph, identity system, or spatial-state system.
3. Core Contract
Given a canonical AtlasID:
delete_resource(ResourceID)
Atlas shall:
Resolve the Resource through the canonical Resource Registry.
Reject the operation if the Resource does not exist.
Remove all relationships involving that Resource.
Remove the Resource from the canonical Resource Registry.
Remove all canonical spatial state associated with that Resource:Position
Rotation
Scale

Leave all unrelated Resources unchanged.
Leave all unrelated relationships unchanged.
Leave all unrelated spatial state unchanged.
The operation must be deterministic.
4. Canonical Identity
Resource deletion is identified exclusively by:
AtlasID
AtlasID remains the canonical engineering identity of the Resource.
No deletion operation may identify a Resource by:
node_id
Scene node
Resource name
array/list index
UI selection
renderer object
database-specific identifier
temporary viewport identifier
The canonical Resource Registry remains authoritative.
5. Application Command
The application boundary shall expose:
AtlasCommand(
    name="delete_resource",
    payload={
        "resource_id": resource.aid,
    },
)
The command represents intent only.
It must not contain business logic.
6. Delete Semantics
ENG-056 defines deletion as a canonical Resource removal operation.
Given:
Resource R
AtlasID = A
before deletion:
Resource Registry
    A → R

Relationship Graph
    relationships involving A

Spatial State Registry
    A → Position
    A → Rotation
    A → Scale
after successful deletion:
Resource Registry
    A → absent

Relationship Graph
    no relationships involving A

Spatial State Registry
    A → absent
No replacement Resource is created.
No tombstone Resource is required by ENG-056.
No historical revision system is introduced by ENG-056.
7. Relationship Integrity
A Resource may participate in zero or more relationships.
When a Resource is deleted, every relationship involving that Resource must also be removed.
For example:
Wall A ───── supports ───── Beam B
Wall A ───── adjacent ──── Wall C
Deleting Wall A must result in:
Beam B
Wall C
remaining valid Resources, while:
Wall A ───── supports ───── Beam B
Wall A ───── adjacent ──── Wall C
are removed.
Relationships between unrelated Resources must remain unchanged.
8. Spatial State Integrity
ENG-056 extends the canonical spatial-state ownership established by ENG-053, ENG-054, and ENG-055.
The spatial registry currently contains:
AtlasID
   ├── Position
   ├── Rotation
   └── Scale
When a Resource is deleted, its entire canonical spatial state must be removed.
Therefore:
delete(Resource A)
must remove:
Position(A)
Rotation(A)
Scale(A)
while preserving:
Position(B)
Rotation(B)
Scale(B)
for every unrelated Resource B.
9. Resource Model Boundary
AtlasResource remains unchanged.
ENG-056 must not add:
deleted
is_deleted
position
rotation
scale
geometry
to AtlasResource.
Deletion state is represented by the Resource's presence or absence from the canonical Resource Registry.
The canonical Resource model remains intentionally independent from spatial and presentation state.
10. Validation
The application boundary must validate the command before mutation.
Resource ID
resource_id must be an AtlasID.
Invalid identifiers must fail without mutation.
Resource existence
The target Resource must exist in the canonical Resource Registry.
An unknown Resource must produce a failure.
The operation must not create spatial state for an unknown Resource.
11. Atomicity
Invalid deletion requests must not partially mutate the Project.
For an invalid request:
Resource Registry       unchanged
Relationship Graph      unchanged
Spatial State Registry  unchanged
For a valid request, deletion must leave the Project in a consistent post-delete state.
The implementation must not expose an intermediate state in which:
Resource exists
but spatial state does not
or:
Resource is gone
but relationships still reference it
or:
Resource is gone
but canonical spatial state remains
12. Idempotency
ENG-056 defines deletion as a single canonical state transition.
A successful deletion removes the Resource.
A subsequent deletion request for the same AtlasID must fail because the Resource no longer exists.
ENG-056 does not define repeated deletion as a successful no-op.
13. Determinism
Given the same initial Project state and the same valid deletion command, Atlas must produce the same resulting canonical state.
Deletion must not depend on:
randomness
timing
renderer state
Scene state
camera state
selection state
AI output
Agent state
external services
14. Resource Isolation
Deleting one Resource must not alter unrelated Resources.
Given:
Resource A
Resource B
Resource C
after:
delete_resource(A)
the following must remain unchanged:
Resource B
Resource C
including their:
Resource properties
classifications
relationships not involving A
Position
Rotation
Scale
15. Relationship Isolation
Only relationships involving the deleted Resource are removed.
For:
A ── R1 ── B
B ── R2 ── C
deleting A produces:
B ── R2 ── C
R2 must remain intact.
The delete operation must not clear the entire relationship graph.
16. Spatial Isolation
Only spatial state belonging to the deleted Resource is removed.
For:
A → PositionA, RotationA, ScaleA
B → PositionB, RotationB, ScaleB
deleting A results in:
A → absent
B → PositionB, RotationB, ScaleB
17. Scene Independence
ENG-056 must operate without:
AtlasScene
AtlasSceneNode
AtlasCamera
AtlasNavigation
AtlasSelection
AtlasGizmo
AtlasRenderer
Three.js
WebGL
The canonical delete operation belongs to:
AtlasApplication
        ↓
AtlasProject
        ↓
Resource Registry
Relationship Graph
Spatial State Registry
Scene state is outside the ENG-056 contract.
18. Gizmo Independence
ENG-056 must not modify:
AtlasGizmo
The Gizmo remains an interaction-state mechanism.
Deletion is a canonical Resource operation and must not be implemented as a Gizmo action.
19. Agent / AI Independence
ENG-056 must not require:
an Agent
an LLM
AI inference
semantic interpretation
external tools
Agents may eventually request Resource deletion through the application command boundary, but they do not define deletion semantics.
The canonical Project model remains authoritative.
20. History / Undo Boundary
ENG-056 does not introduce:
undo
redo
event sourcing
revision history
snapshots
audit history
soft-delete history
recovery mechanisms
Those are separate future capabilities.
ENG-056 only defines the current canonical Project state after deletion.
21. Project Ownership
The canonical ownership remains:
AtlasProject
│
├── AtlasResourceRegistry
│      └── AtlasResource
│
├── AtlasResourceGraph
│      └── AtlasRelationship
│
└── AtlasSpatialStateRegistry
       └── AtlasID
            ├── Position
            ├── Rotation
            └── Scale
AtlasProject remains responsible for maintaining integrity between these structures.
22. Spatial Registry Cleanup
The existing:
AtlasSpatialStateRegistry.remove(...)
must be used or extended as the canonical cleanup boundary for the deleted Resource's spatial state.
ENG-056 must not directly manipulate private spatial registry dictionaries from the application layer.
The application layer expresses intent.
Project/spatial infrastructure owns state mutation.
23. Public Query Behavior
ENG-056 does not require a new deletion-status query.
Existing queries should naturally behave according to Resource absence.
For example:
AtlasQuery(
    name="get_resource_position",
    parameters={
        "resource_id": resource.aid,
    },
)
after deletion must fail because the Resource no longer exists.
The same applies to:
get_resource_rotation
get_resource_scale
No new is_resource_deleted query is introduced.
24. Error Boundary
An invalid delete request must fail through the established Atlas application/project validation conventions.
The exact exception type should follow the existing application conventions established by ENG-052 through ENG-055.
ENG-056 must not introduce an unrelated error hierarchy merely for deletion.
25. Required Tests
ENG-056 implementation must be test-driven.
Create:
tests/test_resource_delete.py
The RED test suite must cover at minimum:
Command
delete_resource command can be constructed.
Command name is exactly delete_resource.
Resource ID is carried correctly.
Successful deletion
Existing Resource can be deleted.
Resource disappears from canonical Resource Registry.
Project Resource count decreases appropriately.
Relationship cleanup
Relationships involving deleted Resource are removed.
Relationships between unrelated Resources remain.
Graph remains internally consistent.
Spatial cleanup
Position is removed.
Rotation is removed.
Scale is removed.
Spatial state count is updated correctly.
Resource isolation
Deleting Resource A does not affect Resource B.
Resource B's properties remain unchanged.
Resource B's spatial state remains unchanged.
Unknown Resource
Deleting an unknown AtlasID fails.
No Resource is created.
No spatial state is created.
Existing Resources remain unchanged.
Existing relationships remain unchanged.
Invalid identity
Non-AtlasID resource identifiers are rejected.
No partial mutation occurs.
Repeated deletion
First valid deletion succeeds.
Second deletion of the same Resource fails.
Scene independence
Tests operate through AtlasProject / AtlasApplication.
No Scene or renderer dependency exists.
26. Compatibility Requirements
ENG-056 must preserve all existing behavior.
At minimum, after implementation:
ENG-052 Create       must remain GREEN
ENG-053 Move         must remain GREEN
ENG-054 Rotate       must remain GREEN
ENG-055 Scale        must remain GREEN
The complete Atlas regression suite must remain GREEN.
No existing public API may be removed or silently changed.
27. Non-Goals
ENG-056 does not implement:
Soft delete
Trash/recycle bin
Undo/redo
Restore
Revision history
Audit logging
Event sourcing
Scene deletion
Renderer deletion
GPU resource disposal
UI deletion controls
AI deletion
Agent deletion semantics
Geometry deletion
File deletion
Database deletion
External system deletion
Cascade deletion of unrelated Resources
These may be addressed by future milestones.
28. Architectural Invariants
ENG-056 must preserve the following Atlas invariants:
Invariant 1 — Canonical Identity
AtlasID
remains the sole canonical Resource identity.
Invariant 2 — Canonical Registry
The Resource Registry remains the authoritative source of Resource existence.
Invariant 3 — Resource Boundary
AtlasResource remains free of spatial state and presentation concerns.
Invariant 4 — Spatial Boundary
Position, Rotation, and Scale remain Project-owned canonical spatial state.
Invariant 5 — Relationship Integrity
No relationship may remain referencing a deleted Resource.
Invariant 6 — No Orphaned Spatial State
No Position, Rotation, or Scale may remain for a deleted Resource.
Invariant 7 — Isolation
Deleting one Resource cannot mutate unrelated Resource state.
Invariant 8 — Determinism
The same valid deletion operation against the same initial state produces the same resulting state.
Invariant 9 — Layer Separation
Canonical deletion remains independent of Scene, Renderer, UI, Gizmo, Agent, and AI systems.
Invariant 10 — Additive Architecture
ENG-056 extends the existing foundation without replacing or redesigning it.
29. Completion Criteria
ENG-056 is complete only when all of the following are true:

ENG-056-Atlas-Resource-Delete.md exists.

RED tests exist in tests/test_resource_delete.py.

RED tests initially demonstrate missing Delete capability.

delete_resource command is implemented.

Canonical Resource deletion is implemented.

Relationship cleanup is implemented.

Position cleanup is implemented.

Rotation cleanup is implemented.

Scale cleanup is implemented.

Unknown Resource validation is implemented.

Invalid operations are atomic.

Resource isolation is verified.

Relationship isolation is verified.

Spatial isolation is verified.

Existing Create/Move/Rotate/Scale behavior remains GREEN.

Full Atlas regression passes.

No new architectural registry/model is introduced.

AtlasResource remains unchanged.

No Scene/Renderer/UI/AI dependency is introduced.

Documentation checkpoint is closed.
30. Final Architecture After ENG-056
                    AtlasApplication
                           │
                           │
                    Atlas Commands
                           │
                           ↓
                     AtlasProject
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ↓                ↓                 ↓
   Resource Registry   Relationship Graph   Spatial State
          │                │                 Registry
          │                │                 │
          ↓                ↓                 ↓
   AtlasResource      Relationships       AtlasID
                                             │
                                  ┌──────────┼──────────┐
                                  ↓          ↓          ↓
                               Position   Rotation    Scale
Delete operates across these existing canonical structures to leave a consistent Project state:
delete_resource(A)
        │
        ├── remove A from Resource Registry
        ├── remove relationships involving A
        └── remove A spatial state
              ├── Position
              ├── Rotation
              └── Scale
No new foundation is required.
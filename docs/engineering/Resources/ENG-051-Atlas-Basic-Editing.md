ENG-051 — Atlas Basic Editing
Phase: 10 — 3D Workspace
Status: Proposed / Specification Draft
Depends On: ENG-039, ENG-040, ENG-045, ENG-046, ENG-047, ENG-048, ENG-049, ENG-050
Previous: ENG-050 — Gizmos
Next: TBD
Layer: Application / 3D Workspace interaction boundary
Specification authority: This document defines the minimum Basic Editing capability required by the existing Atlas architecture. It does not introduce requirements not established by the preceding milestones.

1. Purpose
ENG-051 introduces the first capability in Atlas that mutates 3D SceneNode transformation state.
ENG-046 established the Scene and SceneNode representation.
ENG-049 established selection.
ENG-050 established renderer-independent manipulation intent through the Gizmo.
ENG-051 establishes the boundary where that manipulation intent can become an actual transformation of an existing AtlasSceneNode.
The architectural progression is:
Scene
  ↓
Camera
  ↓
Navigation
  ↓
Selection
  ↓
Gizmo
  ↓
Basic Editing
  ↓
SceneNode transformation
ENG-051 therefore represents the transition from 3D interaction state to 3D editing state.
2. Architectural Principle
Atlas must retain a single authoritative representation of SceneNode transformation state.
ENG-051 MUST NOT create a competing transformation model.
The existing SceneNode remains the owner of:
position
rotation
scale
Therefore:
ENG-051
   ↓
AtlasSceneNode
   ├── position
   ├── rotation
   └── scale
and not:
ENG-051
   ↓
AtlasEditingNode
   ↓
AtlasSceneNode
This follows the established Atlas principle that presentation/application layers do not create competing canonical engineering models.
3. Architectural Position
The complete Phase 10 chain is:
Atlas Core
    ↓
Atlas Application
    ↓
Atlas Workspace
    ↓
Atlas Scene
    ↓
SceneNode
    ↑
Basic Editing
    ↑
Gizmo
    ↑
Selection
The Workspace already hosts an AtlasScene, stores selection through canonical AtlasID, and dispatches commands through AtlasApplication.  
The Application boundary remains deliberately thin and does not replace AtlasProject with another engineering model. 
4. Scope
ENG-051 MUST establish the minimum deterministic capability for transforming an existing SceneNode.
The initial transformation categories are:
Translation
position
 ├── X
 ├── Y
 └── Z
Rotation
rotation
 ├── X
 ├── Y
 └── Z
Scale
scale
 ├── X
 ├── Y
 └── Z
The implementation MUST preserve the existing SceneNode representation established by ENG-046.
5. Gizmo Relationship
ENG-050 represents manipulation intent.
It does not perform transformation.
The established relationship is:
AtlasSelection
      ↓
selected node identity
      ↓
AtlasGizmo
      ├── mode
      ├── axis
      └── active state
      ↓
ENG-051 Basic Editing
      ↓
AtlasSceneNode
The Gizmo's modes correspond conceptually to:
translate → position
rotate    → rotation
scale     → scale
Its axes correspond to:
x → X
y → Y
z → Z
ENG-051 MUST NOT absorb Gizmo responsibilities such as rendering, picking, raycasting, handle state, or manipulation visualization.
6. Selection Relationship
Selection identifies the target.
ENG-051 performs the transformation.
Therefore:
Selection = "Which node?"
Editing   = "What transformation?"
Gizmo     = "How is manipulation expressed?"
Scene     = "Where is the resulting state stored?"
ENG-051 MUST NOT become the owner of selection state.
The Workspace already stores selection by AtlasID, rather than storing a Resource object. workspace.pyPY
7. Application / Command Boundary
AtlasCommand already represents user/system intent that may change engineering state and intentionally contains no engineering rules. commands.pyPY
Therefore ENG-051 MUST reuse the established command abstraction.
It MUST NOT introduce a parallel command system such as:
AtlasEditCommand
GizmoCommand
SceneCommand
TransformCommandSystem
unless a future specification explicitly establishes such an abstraction.
The intended architectural direction is:
User / Gizmo
      ↓
AtlasCommand
      ↓
AtlasApplication
      ↓
ENG-051 editing behavior
      ↓
AtlasSceneNode
However, the exact command names and payload schema are intentionally not frozen by this specification yet. They must be established by the RED contract after the editing API is resolved.
The existing Application boundary deliberately leaves domain-specific command handlers for later milestones. application.pyPY
8. Transformation Semantics
8.1 Translation
ENG-051 MUST support translation of a SceneNode along the established X/Y/Z axes.
The exact distinction between:
absolute position
and:
delta translation
is an open specification decision and MUST be resolved before RED tests are frozen.
It MUST NOT be silently inferred by implementation.
8.2 Rotation
ENG-051 MUST support rotation along the established X/Y/Z representation used by AtlasSceneNode.
The existing representation MUST be preserved.
ENG-051 MUST NOT introduce a second rotation representation unless the preceding Scene specification explicitly requires it.
8.3 Scale
ENG-051 MUST support scaling along the established X/Y/Z representation.
The semantics of scaling MUST be explicitly defined before RED tests are finalized.
In particular, the specification must settle whether an editing operation represents:
absolute scale
or:
multiplicative scale delta
before implementation.
9. Atomicity
Every editing operation MUST be atomic.
For an operation:
before
   ↓
validate
   ↓
apply
   ↓
after
if validation fails or the operation cannot be completed:
before == after
for the complete transformation state.
Partial transformation MUST NOT be observable.
Example:
position = (1, 2, 3)
An invalid operation MUST NOT result in:
position = (5, 2, 3)
after an X component was changed before a later validation failure.
10. Determinism
Given identical:
SceneNode state
+
editing operation
+
editing parameters
ENG-051 MUST produce the same resulting state.
No rendering state, frame timing, camera state, pointer position, or other presentation state may alter the deterministic transformation result.
11. Validation
ENG-051 MUST validate editing requests before mutation.
At minimum, the RED contract must establish behavior for:
invalid target identity
missing target
invalid operation
invalid axis
invalid transformation parameters
invalid editing state
malformed command payload, where commands are used
Invalid requests MUST fail deterministically.
Invalid requests MUST NOT partially mutate the SceneNode.
12. Isolation Requirements
ENG-051 MUST NOT directly own or redefine:
Atlas Core
Resource Registry
Resource Graph
Resource semantics
Relationships
Validation engine
Agent Runtime
Project model
UI
Workspace lifecycle
Panel registry
View registry
UI selection state
visual styling
3D interaction
Camera
Navigation
Picking
Raycasting
Gizmo rendering
Gizmo handles
Future systems
Undo/redo
Collaboration
BIM
Geometry kernel
AI editing
History/event sourcing
Those are outside the minimum ENG-051 contract.
13. SceneNode Ownership
ENG-051 MUST operate on an existing SceneNode.
It MUST NOT silently create a second SceneNode representation.
The transformation state remains associated with the existing SceneNode identity.
Conceptually:
Scene
 └── node_id
      ├── resource_id
      ├── position
      ├── rotation
      └── scale
Editing changes the transformation values associated with that node.
It does not redefine the node's identity.
14. Resource Boundary
A SceneNode transformation is 3D presentation/workspace state.
ENG-051 MUST NOT assume that changing:
position
rotation
scale
automatically means changing:
AtlasResource properties
AtlasResource semantics
Relationships
No automatic Resource mutation is part of ENG-051 unless an existing Atlas contract explicitly establishes such synchronization.
This distinction is essential:
Atlas Resource
      │
      ↓
SceneNode representation
      │
      ↓
3D editing
must not silently become:
3D editing
      ↓
arbitrary Resource mutation
15. Multi-Object Editing
Out of scope for the initial ENG-051 contract.
ENG-049 provides selection capability, but the existence of selection does not by itself establish multi-selection editing requirements.
Therefore the first ENG-051 implementation should establish deterministic editing of a single target unless the repository's existing contracts demonstrate otherwise.
16. Snapping
Out of scope.
No grid snapping, angular snapping, vertex snapping, surface snapping, or engineering constraint snapping is introduced by ENG-051.
17. Constraints
Out of scope unless explicitly required by an existing Atlas constraint contract.
ENG-051 should not invent a new geometric constraint system.
18. Undo / Redo
Out of scope for the initial ENG-051 implementation.
ENG-051 should not introduce a history stack simply because editing exists.
Future history functionality can consume properly defined editing operations later.
19. Persistence
ENG-051 MUST NOT introduce a new persistence mechanism.
If the existing Scene representation is already covered by Atlas persistence, editing changes must remain compatible with that existing boundary.
No second serialization format is permitted.
20. Agent Integration
AI/Agent-driven editing is not an ENG-051 implementation requirement.
The future architecture may allow:
Agent
   ↓
AtlasCommand
   ↓
ENG-051
but ENG-051 itself MUST remain deterministic and independent of an Agent Runtime.
This preserves the established Atlas principle that agents can request operations without becoming the authority over canonical state.
21. Proposed Public Capability
The eventual public API MUST remain minimal.
Conceptually it needs to express:
target
operation
axis
value / transformation parameters
The exact class/function names are intentionally not frozen yet.
Possible conceptual operations:
translate(...)
rotate(...)
scale(...)
But these names MUST NOT be treated as approved API until the RED contract is finalized.
This prevents implementation details from prematurely becoming architectural requirements.
22. Error and State Guarantees
ENG-051 MUST provide:
Valid operation
    → transformation applied
    → deterministic result
and:
Invalid operation
    → deterministic failure
    → original transformation preserved
The editing system MUST NOT leave partially mutated state after a failed operation.
23. Testing Strategy
ENG-051 follows Atlas's established workflow:
Specification
     ↓
RED Tests
     ↓
Implementation
     ↓
GREEN
     ↓
Full Regression
     ↓
Checkpoint
This preserves the existing Atlas engineering discipline and avoids allowing implementation details to silently define the contract.
23.1 Baseline tests
Tests MUST establish:
deterministic construction
valid initial state
no mutation on initialization
23.2 Translation tests
Tests MUST cover:
X translation
Y translation
Z translation
preservation of unaffected axes
deterministic results
invalid translation
atomic failure
23.3 Rotation tests
Tests MUST cover:
X rotation
Y rotation
Z rotation
preservation of unaffected axes
deterministic results
invalid rotation
atomic failure
23.4 Scale tests
Tests MUST cover:
X scale
Y scale
Z scale
preservation of unaffected axes
deterministic results
invalid scale
atomic failure
23.5 Integration tests
Where the final API establishes these relationships, tests MUST verify:
Selection → target identity → Editing → SceneNode
and:
Gizmo mode/axis → appropriate editing operation
without requiring the editing layer to own Gizmo or Selection state.
23.6 Isolation tests
Tests MUST verify that ENG-051 does not introduce:
Resource mutation
Registry ownership
Graph ownership
Relationship mutation
Agent ownership
Renderer dependency
Camera dependency
Navigation dependency
Gizmo ownership
duplicate transformation models
24. Acceptance Criteria
ENG-051 is complete only when all of the following are satisfied.
Core
Basic Editing capability exists.
It operates on existing SceneNode state.
Translation is supported.
Rotation is supported.
Scale is supported.
X/Y/Z behavior is deterministic.
Invalid operations fail deterministically.
Failed operations are atomic.
Architecture
No competing SceneNode transformation model exists.
Gizmo remains an interaction mechanism rather than an editing engine.
Selection remains responsible for target identification.
Workspace remains a presentation/application container.
Application remains the established boundary.
AtlasCommand remains the established command abstraction.
Atlas Core remains authoritative for engineering state.
No renderer/framework dependency is introduced.
Testing
Focused ENG-051 RED tests are created before implementation.
Focused tests become GREEN.
Full Atlas regression passes.
No previously passing Atlas milestone regresses.
Public exports are verified.
A formal checkpoint is recorded.
25. Explicit Non-Goals
The following are not ENG-051 requirements:
Undo / Redo
History
Multi-selection editing
Snapping
Constraints
BIM semantics
Geometry kernel
Mesh editing
Topology editing
Collision handling
Physics
Rendering
Raycasting
Picking
Camera control
Navigation
AI editing
Agent implementation
Collaboration
Network synchronization
Revision system
These may become future milestones.
26. Open Decisions Before RED
These MUST be resolved before freezing the RED suite:
Decision 1 — Translation semantics
absolute
vs
delta
Decision 2 — Rotation semantics
Exact operation representation and whether values represent absolute orientation or rotational delta.
Decision 3 — Scale semantics
absolute
vs
multiplicative delta
Decision 4 — Valid scale range
Whether:
0
negative values
are legal.
Decision 5 — Command integration
Whether the first ENG-051 implementation exposes editing through:
AtlasCommand → AtlasApplication
directly, or establishes the smallest intermediate application capability necessary while still preserving the existing boundary.
Decision 6 — Target contract
Whether ENG-051 receives:
node_id
directly, a SceneNode reference, or another already-established identity mechanism.
The architecture strongly favors stable identity rather than duplicating objects, but the exact API must be derived from the actual Scene contract rather than invented here.
27. Completion Flow
The intended final flow is:
User
  ↓
Selection
  ↓
AtlasID / node identity
  ↓
Gizmo
  ↓
mode + axis + manipulation intent
  ↓
AtlasCommand / application operation
  ↓
ENG-051 Basic Editing
  ↓
AtlasSceneNode
  ├── position
  ├── rotation
  └── scale
  ↓
3D presentation
The critical invariant is:
Gizmo ≠ Editor
Editor ≠ Scene
Scene ≠ Resource
UI ≠ Engineering Model
Each layer has one responsibility.
28. Milestone Gate
ENG-051 MUST NOT proceed to implementation until the six open decisions above are explicitly resolved and the RED contract is frozen.
Once frozen:
ENG-051 Specification
        ↓
       RED
        ↓
   Implementation
        ↓
      GREEN
        ↓
 Full Regression
        ↓
   Checkpoint
This is consistent with the spec-first discipline we're already using: requirements, constraints, and acceptance criteria are established before implementation so the implementation remains traceable to the intended contract.
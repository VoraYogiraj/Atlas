# ENG-050 — Atlas Gizmo

**Status:** Complete  
**Phase:** Phase 10 — 3D Workspace  
**Depends On:** ENG-039, ENG-040, ENG-045, ENG-046, ENG-047, ENG-048, ENG-049  
**Previous:** ENG-049 — Atlas Selection  
**Next:** ENG-051 — Atlas Basic Editing

---

## 1. Purpose

ENG-050 introduces the Atlas Gizmo layer for the 3D workspace.

The Gizmo is a renderer-independent controller representing the state and intent of viewport manipulation for a selected scene node.

It defines:

- manipulation mode,
- constrained axis,
- target scene-node identity,
- manipulation lifecycle.

The Gizmo does **not** perform actual scene-node transformation.

Actual mutation of scene-node position, rotation, or scale belongs to ENG-051 — Atlas Basic Editing.

The Gizmo therefore represents **manipulation intent and interaction state**, not engineering mutation.

---

# 2. Architectural Position

The Phase 10 interaction chain is:

```text
ENG-046 Scene
      ↓
ENG-047 Camera
      ↓
ENG-048 Navigation
      ↓
ENG-049 Selection
      ↓
ENG-050 Gizmo
      ↓
ENG-051 Basic Editing
The intended responsibility boundaries are:
Scene
  owns scene-node structure

Camera
  owns viewpoint state

Navigation
  manipulates camera viewpoint

Selection
  owns current selection state

Gizmo
  owns manipulation configuration/state

Basic Editing
  performs scene-node transformation
The Gizmo must not collapse these responsibilities into a single controller.
3. Core Design Principle
The Gizmo is an interaction-state abstraction, not a renderer abstraction.
It must remain independent from:
Three.js,
WebGL,
any renderer,
viewport implementation,
mouse events,
keyboard events,
touch events,
raycasting,
picking,
highlighting.
A future renderer/input layer may adapt user input into Gizmo operations.
4. Proposed Module
Implementation location:
src/atlas/application/gizmo.py
Public class:
class AtlasGizmo:
    ...
Public package export:
from atlas.application import AtlasGizmo
The class must also be directly importable:
from atlas.application.gizmo import AtlasGizmo
5. Gizmo Modes
The Gizmo supports three manipulation modes:
translate
rotate
scale
These represent the intended category of manipulation.
They do not themselves modify any scene-node property.
Invalid modes must raise:
ValueError
The accepted values are exact lowercase strings.
6. Gizmo Axes
ENG-050 initially supports single-axis constraints:
x
y
z
An unset axis is represented by:
None
Therefore valid axis values are:
None
x
y
z
Invalid axis values must raise:
ValueError
Plane constraints such as:
xy
xz
yz
and unrestricted:
xyz
are intentionally deferred.
They may be introduced by a future Gizmo extension without changing the core selection or scene model.
7. Identity Model
The Gizmo references a SceneNode by its viewport identity:
node_id: str | None
It must not own the AtlasSceneNode object.
It must not copy SceneNode transformation state.
It must not replace:
AtlasID
as the canonical engineering identity.
The distinction remains:
AtlasID
    engineering/resource identity

node_id
    viewport/scene-node identity
A node may reference an engineering resource, but the Gizmo operates on the node identity.
8. Proposed State
The Gizmo should expose:
@property
def mode(self) -> str:
    ...
@property
def active_axis(self) -> str | None:
    ...
@property
def node_id(self) -> str | None:
    ...
@property
def is_active(self) -> bool:
    ...
Initial state:
mode = "translate"
active_axis = None
node_id = None
is_active = False
The default mode is therefore:
translate
The Gizmo initially has no target and is inactive.
9. Public Operations
9.1 Set Mode
def set_mode(*, mode: str) -> None
Valid values:
translate
rotate
scale
Invalid values raise:
ValueError
Mode changes must not:
attach a node,
activate the Gizmo,
mutate a SceneNode,
mutate a Resource.
9.2 Set Axis
def set_axis(*, axis: str | None) -> None
Valid values:
None
x
y
z
Invalid values raise:
ValueError
Axis changes must not:
attach a node,
activate the Gizmo,
mutate Scene state.
9.3 Attach
def attach(*, node_id: str) -> None
Attaches the Gizmo to a SceneNode identity.
Validation:
node_id must be a string.
node_id must not be empty.
node_id must not contain only whitespace.
Invalid node IDs must raise:
TypeError
for invalid types and:
ValueError
for empty/whitespace identifiers.
The Gizmo stores only the identifier.
It does not:
resolve the SceneNode,
require an AtlasScene,
inspect the Scene,
copy the SceneNode,
validate the node against a Scene.
Calling attach() while the Gizmo is active is invalid and must raise:
RuntimeError
9.4 Detach
def detach() -> None
Detaching removes the current target:
node_id = None
The Gizmo becomes inactive:
is_active = False
Detaching must not modify any SceneNode.
Detaching an already detached Gizmo is valid and idempotent.
Detaching while active should be rejected with:
RuntimeError
The active manipulation must first be ended or cancelled.
9.5 Begin
def begin() -> None
Begins a manipulation session.
Requirements:
Gizmo must have an attached node.
Gizmo must not already be active.
Otherwise:
RuntimeError
When successful:
is_active = True
No SceneNode mutation occurs.
No Resource mutation occurs.
9.6 End
def end() -> None
Ends an active manipulation session.
Requirements:
is_active == True
Otherwise:
RuntimeError
After successful completion:
is_active = False
No SceneNode transformation is performed.
Actual mutation belongs to ENG-051.
9.7 Cancel
def cancel() -> None
Cancels an active manipulation session.
Requirements:
is_active == True
Otherwise:
RuntimeError
After cancellation:
is_active = False
Because ENG-050 does not mutate SceneNode transformation state, cancellation does not need to restore position/rotation/scale.
Transformation rollback belongs to the future editing transaction model.
10. Lifecycle
The Gizmo lifecycle is:
detached
    │
    │ attach()
    ▼
attached
    │
    │ begin()
    ▼
active
    │
    ├── end() ──────► attached
    │
    └── cancel() ───► attached
    │
    │ detach()
    ▼
detached
Initial state:
detached
Valid transitions:
detached  → attached
attached  → active
active    → attached
attached  → detached
Invalid transitions must raise RuntimeError.
The Gizmo must never have an implicit lifecycle transition caused by changing mode or axis.
11. State Invariants
At all times:
node_id is None
    ⇒ is_active == False
An active Gizmo must always have a target:
is_active == True
    ⇒ node_id is not None
Only one node may be attached at a time.
There is no multi-node Gizmo state in ENG-050.
12. Atomicity
Validation must occur before mutation.
For example:
gizmo.attach(node_id="wall")
followed by:
gizmo.set_mode(mode="invalid")
must leave:
node_id = "wall"
mode = previous valid mode
is_active = previous state
Similarly, invalid axis/node operations must not partially mutate the Gizmo.
All state-changing operations should follow:
validate
    ↓
construct intended state
    ↓
commit
rather than partially mutating state before validation completes.
13. Determinism
Given the same initial state and the same sequence of operations, the Gizmo must produce the same resulting state.
No randomness, timing dependency, renderer state, or external state may influence the Gizmo.
Example:
Gizmo A:
attach("wall")
set_mode("rotate")
set_axis("z")
begin()
end()

Gizmo B:
attach("wall")
set_mode("rotate")
set_axis("z")
begin()
end()
Both must produce equivalent observable state.
14. Scene Independence
The Gizmo must be independently constructible:
gizmo = AtlasGizmo()
No Scene is required.
It must not:
gizmo.scene
or otherwise own an AtlasScene.
The Gizmo must not:
add/remove SceneNodes,
inspect Scene hierarchy,
change parent relationships,
change visibility,
change node ordering,
resolve node existence.
The node_id is an identity reference only.
15. Selection Independence
ENG-049 owns selection state.
ENG-050 may consume a node identity supplied by an external controller, but it must not redefine selection.
The Gizmo must not own:
AtlasSelectionState
and must not perform:
selection,
deselection,
multi-selection,
picking,
hit testing,
highlighting.
Expected future flow:
Pointer/Input
    ↓
Picking
    ↓
AtlasSelectionState
    ↓
selected node_id
    ↓
AtlasGizmo.attach()
16. Renderer Independence
ENG-050 must not import or depend on:
three
three.js
WebGL
WebGPU
OpenGL
renderer-specific APIs
No renderer object may be stored by the Gizmo.
No raycaster may be stored by the Gizmo.
No visual mesh or handle object may be stored by the Gizmo.
The renderer will later interpret Gizmo state and render the appropriate visual representation.
17. Engineering Isolation
The Gizmo must not own or mutate:
AtlasResource
AtlasRelationship
AtlasResourceGraph
AtlasProject
AtlasID
The Gizmo stores only viewport node identity:
node_id: str
No engineering properties are changed by ENG-050.
18. Transformation Boundary
ENG-050 explicitly does not implement:
position changes
rotation changes
scale changes
translation deltas
rotation deltas
scale deltas
The Gizmo only describes:
what manipulation mode is active
which axis constrains it
which node is targeted
whether manipulation is active
Actual transformations belong to:
ENG-051 — Atlas Basic Editing
Future flow:
Gizmo
  mode = translate
  axis = x
  node_id = wall-01
        ↓
Basic Editing
        ↓
SceneNode.position mutation
19. Input Boundary
ENG-050 does not process raw input.
No APIs for:
mouse down
mouse move
mouse up
keyboard
touch
gamepad
pointer events
are introduced.
Input adaptation belongs to a future UI/input integration layer.
20. Persistence Boundary
ENG-050 does not implement:
serialization,
persistence,
project save/load,
import/export.
Gizmo state is transient UI/application state.
21. Agent / AI Boundary
ENG-050 does not invoke:
agents,
AI,
LLMs,
orchestration,
engineering validation.
The Gizmo is deterministic application-layer interaction state.
22. Testing Strategy
Create:
tests/test_gizmo.py
Focused test command:
pytest tests/test_gizmo.py -q
23. Focused Test Categories
Construction
Verify:
default construction succeeds,
default mode is translate,
axis is None,
node identity is None,
Gizmo is inactive.
Modes
Verify:
translate,
rotate,
scale,
invalid mode rejection,
mode changes do not activate the Gizmo.
Axes
Verify:
no axis,
x,
y,
z,
invalid axis rejection.
Attachment
Verify:
valid node attachment,
node identity preservation,
invalid node type rejection,
empty node rejection,
whitespace node rejection,
attachment does not require Scene,
attachment does not own SceneNode.
Lifecycle
Verify:
attach,
begin,
end,
cancel,
detach,
invalid lifecycle transitions,
detached Gizmo cannot become active,
active Gizmo cannot be attached to another node,
detach is idempotent when inactive.
Atomicity
Verify:
invalid mode preserves state,
invalid axis preserves state,
invalid node ID preserves state,
invalid operations do not partially mutate lifecycle state.
Single Target
Verify:
only one node is attached,
no multi-selection behavior,
replacing an attached node follows the lifecycle rules.
Scene Independence
Verify:
no Scene constructor dependency,
no Scene ownership,
no Scene mutation.
Selection Independence
Verify:
no AtlasSelectionState ownership,
Gizmo does not select/deselect nodes.
Renderer Independence
Verify:
no renderer,
no Three.js,
no raycaster,
no visual object ownership.
Engineering Isolation
Verify:
no Resource ownership,
no Relationship ownership,
no Graph ownership,
no Project ownership,
no engineering mutation.
Determinism
Verify that identical operation sequences produce identical observable state.
Public API
Verify:
from atlas.application.gizmo import AtlasGizmo
and:
from atlas.application import AtlasGizmo
both work.
24. Expected RED State
Before implementation, the focused test suite should fail because:
AtlasGizmo
does not yet exist.
Expected missing implementation/export failures are acceptable during the RED phase.
Existing ENG-039 through ENG-049 tests must remain untouched.
25. Implementation Constraints
Implementation must:
introduce only the Gizmo responsibility,
preserve all previous public APIs,
avoid changing Scene behavior,
avoid changing Camera behavior,
avoid changing Navigation behavior,
avoid changing Selection behavior,
avoid introducing renderer dependencies,
avoid implementing Basic Editing,
maintain deterministic behavior,
maintain atomic validation.
No unrelated refactoring is permitted.
26. Completion Criteria
ENG-050 is complete when:

AtlasGizmo exists.

Default state is deterministic.

Translate/rotate/scale modes work.

X/Y/Z axis constraints work.

Node attachment works.

Lifecycle is deterministic.

Invalid lifecycle transitions are rejected.

Invalid values are rejected.

Atomicity invariants pass.

Gizmo does not own Scene.

Gizmo does not own SceneNode objects.

Gizmo does not own Selection.

Gizmo has no renderer dependency.

Gizmo has no Three.js dependency.

Gizmo has no raycasting dependency.

Gizmo does not mutate engineering resources.

Gizmo does not perform SceneNode transformations.

Focused tests pass.

Full regression passes.

AtlasGizmo is publicly exported.

ENG-050 is checkpointed.
27. Explicit Non-Goals
The following are explicitly outside ENG-050:
Scene mutation
Camera manipulation
Navigation
Selection
Picking
Raycasting
Highlighting
Rendering
Three.js integration
Input events
Translation
Rotation
Scaling
Undo/redo
Editing transactions
Persistence
Serialization
Import/export
Agents
AI
Engineering validation
These responsibilities must remain in their appropriate layers.
28. Final Architecture
After ENG-050:
Atlas Application
│
├── Scene
│   └── SceneNode hierarchy
│
├── Camera
│   └── Viewpoint
│
├── Navigation
│   └── Camera manipulation
│
├── Selection
│   └── Current node/resource selection
│
├── Gizmo
│   └── Manipulation state
│
└── Basic Editing
    └── SceneNode transformation
The resulting interaction model is:
Selection
    ↓
selected node_id
    ↓
Gizmo
    ├── mode
    ├── axis
    └── active state
    ↓
Basic Editing
    ↓
SceneNode transformation
ENG-050 therefore establishes the manipulation layer without allowing viewport interaction concerns to leak into the canonical engineering model.
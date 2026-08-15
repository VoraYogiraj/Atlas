ENG-049 — Atlas Selection

Document Type: Engineering Resource Specification
Status: Proposed
Phase: Phase 10 — 3D Workspace
Depends On: ENG-039, ENG-040, ENG-045, ENG-046, ENG-047, ENG-048
Primary Capability: Selection
Implementation Target: packages/atlas/src/atlas/application/selection.py
Test Target: packages/atlas/tests/test_selection.py

1. Purpose

ENG-049 defines the renderer-independent Atlas Selection capability for the Atlas 3D Workspace.

Selection establishes the application-level state describing what is currently selected without coupling selection to:

rendering,
mouse or pointer input,
raycasting,
visual highlighting,
gizmos,
editing,
engineering-resource mutation.

Selection is state.

Input systems determine how something becomes selected.

Renderers determine how the selected state is visually represented.

Engineering systems determine what the selected resource means.

The separation is:

Input / Picking
      │
      ▼
Atlas Selection
      │
      ├── Atlas Resource identity
      │
      └── Scene representation identity
      │
      ▼
Presentation / Renderer
2. Architectural Intent

Atlas must distinguish between an engineering resource and its viewport representation.

An AtlasID identifies an engineering resource.

An AtlasSceneNode.node_id identifies a scene representation.

These are intentionally different identities.

For example:

Engineering Resource
┌─────────────────────┐
│ WALL-001            │
│ AtlasID: abc123     │
└──────────┬──────────┘
           │
           ├───────────────┐
           ▼               ▼
      SceneNode A      SceneNode B
      node-001         node-002

Both scene nodes may represent the same engineering resource.

Therefore ENG-049 must not collapse:

resource identity

and:

scene-node identity

into a single identifier.

3. Existing Selection Architecture

The Atlas application already contains:

AtlasResourceSelection

from ENG-039.

ENG-049 must extend and formalize the existing selection capability rather than introduce a competing resource-selection system.

There must remain one canonical application-level selection concept.

The existing abstraction should therefore remain the foundation for resource selection.

ENG-049 may add scene-representation semantics around that foundation only where necessary.

No second competing:

AtlasSelection

resource model should be created merely to duplicate AtlasResourceSelection.

4. Scope
4.1 In Scope

ENG-049 owns:

Single-selection state.
Selected Atlas resource identity.
Optional selected scene-node identity.
Selection and deselection.
Selection state validation.
Deterministic state transitions.
Selection clearing.
Renderer-independent selection semantics.
Separation between resource identity and scene representation identity.
Atomicity of invalid selection operations.
4.2 Out of Scope

ENG-049 does not own:

mouse input,
keyboard input,
touch input,
pointer events,
raycasting,
hit testing,
Three.js Raycaster,
WebGL,
WebGPU,
visual highlighting,
outline rendering,
selection overlays,
gizmos,
transform controls,
multi-selection,
engineering editing,
resource mutation,
relationship mutation,
scene hierarchy mutation,
persistence,
serialization,
import/export,
AI,
agents.
5. Selection Model

ENG-049 defines single selection.

At any given time there is either:

nothing selected

or:

one active selection

The selection state consists conceptually of:

resource_id
node_id

where:

resource_id
    = engineering identity


node_id
    = viewport representation identity
6. Empty Selection

The initial state is:

resource_id = None
node_id     = None
is_selected = False

An empty selection is a valid state.

Selection does not require a selected object to exist.

7. Resource Selection

Selecting an engineering resource identifies it through its canonical AtlasID.

Conceptually:

select_resource(
    resource_id=AtlasID(...)
)

The resulting state is:

resource_id = AtlasID(...)
node_id     = None
is_selected = True

Resource selection does not require a scene node.

This is important because Atlas resources may exist without currently being represented in a 3D scene.

8. Scene-Node Selection

A scene representation may be selected using its node_id.

Conceptually:

select_node(
    node_id="wall-node-01",
    resource_id=AtlasID(...),
)

The resulting state is:

resource_id = AtlasID(...)
node_id     = "wall-node-01"
is_selected = True

The resource_id association is optional at the Selection state level.

A scene node may therefore be selected as a viewport representation without Selection becoming responsible for proving that the node exists.

Scene existence and hierarchy remain the responsibility of AtlasScene.

9. Public API

The ENG-049 selection abstraction exposes the following semantic operations.

9.1 Resource Selection
def select_resource(
    self,
    *,
    resource_id: AtlasID,
) -> None

Selects an engineering resource.

Requirements:

resource_id must be an AtlasID.
Invalid values raise TypeError.
Existing selection is replaced.
node_id becomes None.
is_selected becomes True.
9.2 Scene Node Selection
def select_node(
    self,
    *,
    node_id: str,
    resource_id: AtlasID | None = None,
) -> None

Selects a viewport scene representation.

Requirements:

node_id must be a non-empty string.
Whitespace-only IDs are invalid.
resource_id, when provided, must be an AtlasID.
Invalid arguments must not modify the current selection.
Existing selection is replaced.
9.3 Clear
def clear(self) -> None

Clears the current selection.

Result:

resource_id = None
node_id     = None
is_selected = False

Calling clear() repeatedly is valid and deterministic.

10. Public State

Selection exposes:

@property
def resource_id(self) -> AtlasID | None

and:

@property
def node_id(self) -> str | None

and:

@property
def is_selected(self) -> bool

These properties represent selection state only.

They do not perform lookup or validation against a Scene or Registry.

11. Resource Identity Boundary

resource_id represents the canonical engineering identity.

It must use:

AtlasID

and must not be replaced by:

resource names,
scene-node IDs,
arbitrary strings,
object references,
renderer IDs.

Selection does not own the actual AtlasResource.

Therefore:

AtlasResourceSelection
        │
        └── AtlasID

not:

Selection
   └── AtlasResource object

This prevents Selection from becoming another owner of engineering entities.

12. Scene Node Identity Boundary

node_id identifies a viewport representation.

It must be a string.

It is not an AtlasID.

This distinction is intentional.

AtlasID
    → engineering identity


node_id
    → scene representation identity

A single resource may have multiple scene representations.

13. Scene Boundary

Selection does not own an AtlasScene.

It must not:

create scenes,
delete scenes,
create nodes,
delete nodes,
modify node hierarchy,
modify node transforms,
modify visibility,
resolve scene hierarchy,
mutate scene state.

The application layer may coordinate:

AtlasScene
+
AtlasSelection

but neither component owns the other.

14. Scene Existence Validation

ENG-049 does not require AtlasSelection to validate that a selected node_id exists inside an AtlasScene.

This is deliberate.

Selection stores identity/state.

Scene owns existence and hierarchy.

Future application coordination may enforce:

selected node exists

where required.

That validation must not turn Selection into a second Scene registry.

15. Single-Selection Invariant

Only one selection is active.

For example:

select_resource(resource_a)
select_resource(resource_b)

must result in:

resource_id = resource_b

not:

resource_id = [resource_a, resource_b]

Likewise:

select_node("node-a")
select_node("node-b")

results in:

node_id = "node-b"

Multi-selection is explicitly outside ENG-049.

16. Selection Replacement

Every successful selection operation replaces the previous selection.

Example:

Initial:
resource=A
node=None


select_node(node=B, resource=C)


Result:
resource=C
node=B

The previous selection is discarded atomically.

17. Resource Selection and Node Selection Relationship

Resource and node selection can coexist when the node is associated with a resource.

Example:

resource_id = WALL-001
node_id     = wall-node-01

This means:

Scene representation wall-node-01 is selected and is associated with engineering resource WALL-001.

Selection does not infer this association automatically.

The caller supplies the relationship.

18. Validation
18.1 AtlasID

resource_id must be:

AtlasID

Otherwise:

TypeError

is raised.

18.2 node_id

node_id must be a string.

Non-string:

TypeError

Empty string:

ValueError

Whitespace-only string:

ValueError
18.3 Optional Resource ID

When resource_id is provided to select_node(), it must be an AtlasID.

Invalid values raise:

TypeError
19. Atomicity

Selection operations must be atomic.

The required sequence is:

Validate input
      ↓
Construct new state
      ↓
Commit state

Never:

Modify current state
      ↓
Validate
      ↓
Fail

For example, if the current selection is:

resource=A
node=node-a

and:

select_node(
    node_id="",
    resource_id=resource_b,
)

fails, the state must remain:

resource=A
node=node-a

unchanged.

20. Determinism

Selection must be deterministic.

Given the same initial state and the same sequence of operations, the resulting state must be identical.

Example:

clear
select_resource(A)
select_node(B, C)
clear

must always result in:

resource_id = None
node_id = None
is_selected = False

Selection must not depend on:

time,
renderer state,
frame rate,
random values,
browser state,
global mutable state.
21. Renderer Boundary

ENG-049 contains no rendering implementation.

It must not import:

Three.js
WebGL
WebGPU
Canvas
DOM

Selection state is renderer-neutral.

A future renderer may map:

AtlasSelection.node_id
        ↓
Three.js Object3D
        ↓
Visual highlight

but the renderer must not become the canonical selection state.

22. Input Boundary

ENG-049 does not process input events.

There is no:

mouse click
pointer event
keyboard event
touch event
raycast
hit test

inside Selection.

Future TypeScript code may perform:

Pointer Event
      ↓
Three.js Raycaster
      ↓
node_id
      ↓
Atlas Selection

but the input adaptation is outside ENG-049.

23. Picking Boundary

Picking is explicitly separate from Selection.

Picking
    = determine what the user pointed at


Selection
    = store what is currently selected

Therefore ENG-049 must not implement:

raycasting,
collision tests,
geometry intersection,
screen-coordinate conversion,
depth testing,
viewport hit testing.

These belong to the future presentation/input layer.

24. Highlighting Boundary

Selection does not visually modify selected objects.

There is no:

selected = true

property on AtlasSceneNode.

There is no material mutation.

There is no outline state.

There is no renderer-specific highlight state.

A future presentation layer can observe Selection and render the appropriate visual state.

25. Gizmo Boundary

Gizmos belong to ENG-050.

Selection does not:

create gizmos,
position gizmos,
manipulate transforms,
rotate objects,
translate objects,
scale objects.

The relationship is:

Selection
    ↓
identifies selected object


Gizmos
    ↓
manipulate selected object
26. Editing Boundary

Basic editing belongs to ENG-051.

Selection must not modify:

resource properties,
resource geometry,
relationships,
classifications,
semantics,
validation constraints,
project state.

Selecting something does not change what that engineering entity means.

27. Relationship Boundary

Selection must not traverse or modify the Atlas relationship graph.

It does not:

create relationships,
delete relationships,
inspect graph topology,
alter relationship semantics.

Selection is identity/state, not graph logic.

28. Registry Boundary

Selection must not become a Registry lookup service.

The selection system stores identifiers.

It does not own:

AtlasResourceRegistry
AtlasProjectRegistry
AtlasResourceGraph

A higher-level application service may resolve the selected resource when needed.

29. Persistence Boundary

ENG-049 does not define persistence.

Selection state may eventually be included in workspace/session state, but this milestone does not implement:

JSON serialization,
project persistence,
save/load,
import/export,
database storage.
30. Agent and AI Boundary

Selection is deterministic application state.

It does not invoke:

agents,
LLMs,
AI,
semantic reasoning,
engineering validation.

Future agents may request selection through an application command interface, but that integration is outside ENG-049.

31. TypeScript / Three.js Future Integration

ENG-049 is designed to integrate cleanly with the future TypeScript + Three.js workspace.

The intended flow is:

                 Browser
                    │
              Pointer Event
                    │
                    ▼
          TypeScript Input Layer
                    │
                    ▼
            Three.js Raycaster
                    │
                    ▼
               node_id
                    │
                    ▼
            Atlas Selection
                    │
             ┌──────┴──────┐
             ▼             ▼
        resource_id      node_id
             │             │
             └──────┬──────┘
                    ▼
             UI / Inspector

This allows the Three.js layer to determine what was clicked while Atlas Selection determines what is selected.

The renderer therefore remains an adapter, not the source of truth.

32. Inspector Integration

Selection is expected to become an important input to the existing Inspector architecture.

The future flow may be:

AtlasSelection
      │
      ▼
selected AtlasID
      │
      ▼
AtlasInspector
      │
      ▼
AtlasResourcePresentation

However, ENG-049 does not modify Inspector behavior unless explicitly required by a later integration milestone.

33. Dashboard / Explorer Boundary

Selection may eventually be shared with:

Explorer,
Dashboard,
Inspector,
Scene,
3D Workspace.

However, ENG-049 must not create duplicate selection states for each UI component.

The goal is one application-level selection state that multiple views can consume.

34. Public API Surface

The final public API must remain intentionally small.

The existing application-level selection API must remain canonical.

Where ENG-049 extends it, the supported semantics are:

select_resource(...)
select_node(...)
clear()


resource_id
node_id
is_selected

No renderer-specific or input-specific methods should be added.

35. Test Requirements

ENG-049 tests must cover the following categories.

35.1 Construction
default state is empty,
deterministic initial state,
no external dependency required.
35.2 Resource Selection
valid AtlasID,
selected resource is exposed,
node selection is cleared when resource-only selection occurs,
is_selected becomes True.
35.3 Scene Node Selection
valid node ID,
optional resource ID,
node ID exposed,
associated resource ID exposed,
selection becomes active.
35.4 Clearing
clear active resource selection,
clear active node selection,
clear combined selection,
repeated clear is safe.
35.5 Replacement
resource → resource,
resource → node,
node → resource,
node → node.
35.6 Validation
invalid resource IDs,
invalid node IDs,
empty node IDs,
whitespace node IDs,
invalid optional resource IDs.
35.7 Atomicity

Invalid operations must preserve the previous selection exactly.

35.8 Single Selection

Tests must establish that only one active selection exists.

35.9 Identity Separation

Tests must establish that:

AtlasID != node_id

conceptually and structurally.

35.10 Scene Independence

Selection must work without constructing an AtlasScene.

35.11 Renderer Independence

Tests must require no renderer or browser dependency.

35.12 Engineering Isolation

Selection must not mutate:

resources,
relationships,
registries,
graph state.
35.13 Public API

The expected package-level selection API must remain importable from:

from atlas.application import AtlasResourceSelection

and any ENG-049 additions must be explicitly exported without breaking existing application exports.

36. Architectural Invariants

ENG-049 must preserve these invariants.

Invariant 1 — One canonical selection model

Atlas must not create competing resource-selection systems.

Invariant 2 — Resource identity remains AtlasID

Selection must not replace engineering identity with scene-node identity.

Invariant 3 — Scene identity remains node_id

Scene representation identity must remain separate from engineering identity.

Invariant 4 — Single selection

Only one active selection exists.

Invariant 5 — Selection does not own Scene

AtlasScene remains the owner of scene state.

Invariant 6 — Selection does not own Resources

AtlasResource remains the canonical engineering entity.

Invariant 7 — Selection does not perform picking

Picking belongs to input/presentation infrastructure.

Invariant 8 — Selection does not perform highlighting

Visual representation belongs to the renderer/UI.

Invariant 9 — Selection does not edit

Editing belongs to ENG-051.

Invariant 10 — Selection is deterministic

Identical operations produce identical state.

Invariant 11 — Invalid operations are atomic

Failed validation cannot corrupt or partially modify selection state.

Invariant 12 — Renderer independence

Selection remains usable without Three.js.

37. Completion Criteria

ENG-049 is complete when:

 Existing AtlasResourceSelection architecture has been preserved.
 ENG-049 selection semantics are documented.
 Single-selection behavior is defined.
 Resource identity uses AtlasID.
 Scene-node identity remains separate.
 Resource selection is supported.
 Scene-node selection is supported where appropriate.
 Selection clearing is supported.
 Invalid input is rejected deterministically.
 Failed operations are atomic.
 Selection does not own Scene.
 Selection does not own Resources.
 Selection does not mutate Relationships.
 Selection does not implement picking.
 Selection does not implement highlighting.
 Selection does not implement gizmos.
 Selection does not implement editing.
 Selection has no renderer dependency.
 Selection has no browser/input dependency.
 Focused ENG-049 tests pass.
 Full Atlas regression passes.
 Application exports remain intact.
 ENG-049 documentation matches implementation.
38. Phase 10 Position
Phase 10 — 3D Workspace


ENG-046  Atlas Scene          ✅
ENG-047  Atlas Camera         ✅
ENG-048  Atlas Navigation     ✅
ENG-049  Atlas Selection      ← CURRENT
ENG-050  Atlas Gizmos
ENG-051  Atlas Basic Editing

ENG-049 establishes the selection state foundation required before Gizmos and Basic Editing.
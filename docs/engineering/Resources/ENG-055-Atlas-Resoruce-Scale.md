ENG-055 — Atlas Resource Scale

Status: Proposed
Phase: Phase 11 — Resource Editing
Depends On: ENG-054 — Atlas Resource Rotate
Previous: ENG-054 — Atlas Resource Rotate
Next: ENG-056 — Atlas Resource Delete

1. Purpose

ENG-055 introduces the Scale capability within Phase 11 — Resource Editing.

Phase 11 establishes canonical Resource editing capabilities in the following sequence:

ENG-052  Create
    ↓
ENG-053  Move
    ↓
ENG-054  Rotate
    ↓
ENG-055  Scale
    ↓
ENG-056  Delete
    ↓
ENG-057  Duplicate

The purpose of ENG-055 is to establish a deterministic, canonical, application-level operation for changing the spatial scale associated with an Atlas Resource.

Scale must extend the existing Move and Rotate architecture without modifying the canonical AtlasResource structure, without transferring ownership to AtlasSceneNode, and without introducing a competing transformation model.

The existing Phase 11 architecture already establishes that Resource editing must enter through the Atlas application boundary and preserve AtlasID, AtlasProject, and the canonical Resource Registry.

2. Architectural Position

The canonical Atlas interaction path remains:

User / UI / Agent / External System
                ↓
          AtlasCommand
                ↓
       AtlasApplication
                ↓
          AtlasProject
                ↓
 Canonical Atlas engineering state

For ENG-055:

AtlasCommand
    │
    │ scale_resource
    ▼
AtlasApplication.execute()
    │
    ▼
AtlasProject
    │
    ▼
AtlasSpatialStateRegistry
    │
    └── AtlasID → Scale(x, y, z)

Reads follow:

AtlasQuery
    │
    │ get_resource_scale
    ▼
AtlasApplication.query()
    │
    ▼
AtlasProject.spatial_states
    │
    ▼
Scale(x, y, z)

The application boundary remains a thin interaction layer and does not become a second engineering model. This follows the existing Atlas architecture in which commands represent intent and canonical state remains outside the command itself.

3. Relationship to ENG-052

ENG-052 established the Resource creation flow:

AtlasCommand
      ↓
AtlasApplication
      ↓
AtlasResource
      ↓
AtlasProject.resources
      ↓
AtlasResourceRegistry

ENG-055 must not modify that creation contract.

When a Resource is created, its spatial state must contain the Scale default:

Scale = (1.0, 1.0, 1.0)

The value 1.0 represents the neutral scale factor.

Therefore:

Create Resource
      ↓
Position = (0, 0, 0)
Rotation = (0, 0, 0)
Scale    = (1, 1, 1)

The creation contract remains unchanged; Scale is only an additional spatial state initialized alongside the already-established Move and Rotate state.

4. Relationship to ENG-053 and ENG-054

ENG-053 established:

AtlasID
   ↓
SpatialStateRegistry
   ↓
Position

ENG-054 extends it with:

AtlasID
   ↓
SpatialStateRegistry
   ├── Position
   └── Rotation

ENG-055 extends the same state boundary:

AtlasID
   ↓
SpatialStateRegistry
   ├── Position
   ├── Rotation
   └── Scale

This is one canonical Resource-associated spatial state boundary.

ENG-055 must not create:

ScaleRegistry
ResourceScaleRegistry
SceneScaleRegistry
TransformRegistry

or any equivalent competing subsystem.

5. Canonical Resource Model

The canonical AtlasResource remains:

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

ENG-055 must not add:

scale
transform
position
rotation
spatial_transform

to AtlasResource.

The established Phase 11 architectural decision deliberately keeps spatial editing state separate from AtlasResource. The original Move specification explicitly required that spatial fields not simply be added to the Resource model.

Therefore:

AtlasResource
      │
      │ AtlasID
      ▼
AtlasSpatialStateRegistry
      │
      ├── Position
      ├── Rotation
      └── Scale
6. What “Scale” Means

ENG-055 defines:

Scale(Resource, Scale) means: set the canonical spatial scale associated with the identified Resource to the supplied absolute 3D scale factors.

The operation is therefore an absolute assignment, not a scale delta.

Example:

Current Scale:
(2.0, 2.0, 2.0)


Scale Resource to:
(0.5, 1.0, 3.0)


Result:
(0.5, 1.0, 3.0)

The previous scale is replaced.

The operation does not mean:

current × requested

and does not mean:

current + requested
7. Scale Representation

Scale is represented by three scalar factors:

Scale
├── x
├── y
└── z

Example:

{
    "x": 1.0,
    "y": 1.0,
    "z": 1.0,
}

A dedicated domain value object is therefore proposed:

@dataclass(frozen=True, slots=True)
class AtlasSpatialScale:
    x: float
    y: float
    z: float

This follows the existing position and rotation representation pattern.

8. Scale Is Dimensionless

Scale factors are dimensionless multipliers.

For example:

1.0 = original scale
2.0 = twice the scale
0.5 = half the scale

Scale therefore does not carry:

mm
cm
m
inch
ft

or any other physical unit.

This distinction is important.

ENG-055 does not define physical dimension editing.

For example:

Wall width = 3000 mm

is a property/geometry/dimension concept.

Whereas:

Scale X = 2.0

is a spatial transform factor.

ENG-055 must not silently convert one into the other.

9. Absolute Scale Semantics

The operation is absolute.

Example:

AtlasCommand(
    name="scale_resource",
    payload={
        "resource_id": resource.aid,
        "scale": {
            "x": 2.0,
            "y": 3.0,
            "z": 4.0,
        },
    },
)

After execution:

Scale =
    x = 2.0
    y = 3.0
    z = 4.0

A second request:

{
    "x": 5.0,
    "y": 6.0,
    "z": 7.0,
}

produces:

Scale =
    x = 5.0
    y = 6.0
    z = 7.0

It must not produce:

(10, 18, 28)
10. Non-Uniform Scale

ENG-055 supports independent X/Y/Z factors.

Therefore:

Scale:
x = 2
y = 1
z = 0.5

is valid.

This establishes the smallest useful 3D Scale capability without prematurely introducing:

uniform_scale
lock_aspect_ratio
axis_constraints
plane_constraints
proportional_scaling

Those may be introduced by later specifications.

11. Scale Validation

Every scale component must satisfy:

numeric
+
finite
+
strictly greater than zero

Therefore:

1.0       ✅
2.5       ✅
0.25      ✅
100.0     ✅


0.0       ❌
-1.0      ❌
NaN       ❌
+∞        ❌
-∞        ❌
True      ❌
False     ❌
"2.0"     ❌
None      ❌
Why zero is invalid

A scale factor of zero collapses the corresponding spatial dimension.

That creates degenerate spatial state and is not a valid engineering transform for the initial Resource Scale capability.

Therefore:

x > 0
y > 0
z > 0

is mandatory.

Why negative values are invalid

A negative scale factor introduces reflection/mirroring semantics rather than ordinary scaling.

Reflection is a separate transformation concern and is not part of ENG-055.

Therefore:

Scale(-1, 1, 1)

must be rejected.

12. Floating-Point Policy

ENG-055 does not impose rounding.

The supplied finite numeric value is preserved as a floating-point value.

For example:

1.25
0.333333
2.75

remain valid without normalization.

No arbitrary precision policy, rounding policy, or unit conversion should be introduced.

13. Resource Identity

The target Resource is identified exclusively through:

AtlasID

Example:

resource_id = resource.aid

The command must not target:

resource name
SceneNode ID
array index
registry position
classification
UI selection object

The existing distinction between canonical engineering identity and viewport identity remains unchanged. ENG-050 explicitly establishes AtlasID as engineering identity and node_id as viewport identity.

14. Canonical Ownership

Scale belongs to the Project-scoped canonical spatial state:

AtlasProject
│
├── AtlasResourceRegistry
│
├── AtlasResourceGraph
│
├── ClassificationRegistry
│
└── AtlasSpatialStateRegistry
      │
      └── AtlasID → AtlasSpatialScale

The Project remains the ownership boundary.

The Resource Registry remains authoritative for Resource existence.

The spatial registry does not become a Resource Registry.

15. Application Command

The public command identity is:

scale_resource

Conceptual request:

AtlasCommand(
    name="scale_resource",
    payload={
        "resource_id": resource.aid,
        "scale": {
            "x": 2.0,
            "y": 1.5,
            "z": 0.5,
        },
    },
)

The command contains intent only.

It must not contain:

validation rules
Resource mutation logic
Registry logic
Scene logic
geometry logic
renderer logic
AI logic

This follows the established command contract.

16. Application Query

The public query identity is:

get_resource_scale

Conceptual request:

AtlasQuery(
    name="get_resource_scale",
    parameters={
        "resource_id": resource.aid,
    },
)

The query returns:

{
    "x": 2.0,
    "y": 1.5,
    "z": 0.5,
}

The query does not return:

AtlasResource
AtlasSceneNode
renderer object
Gizmo

It returns only the canonical Scale representation.

17. Default Scale

Every Resource participating in the established spatial-state model must have:

Scale = (1.0, 1.0, 1.0)

This means no scale transformation is applied.

This ensures that:

Create → Query Scale

is deterministic.

Expected result:

{
    "x": 1.0,
    "y": 1.0,
    "z": 1.0,
}
18. Relationship to Position

Scale must not mutate Position.

Example:

Position:
(10, 20, 30)


Scale:
(2, 2, 2)

After scaling:

Position:
(10, 20, 30)


Scale:
(2, 2, 2)

Position remains unchanged.

19. Relationship to Rotation

Scale must not mutate Rotation.

Example:

Rotation:
(10, 20, 30)


Scale:
(2, 3, 4)

After scaling:

Rotation:
(10, 20, 30)


Scale:
(2, 3, 4)

Rotation remains unchanged.

20. Relationship to Move

The three transformations are independent canonical components:

Position
Rotation
Scale

Therefore:

Move
  → Position only


Rotate
  → Rotation only


Scale
  → Scale only

No operation may silently modify another component.

The established Phase 11 implementation principle requires future editing capabilities to extend cleanly from Move → Rotate → Scale without introducing a second Resource model.

21. Atomicity

All validation must occur before spatial state mutation.

Required sequence:

Receive command
      ↓
Validate command object
      ↓
Validate AtlasID
      ↓
Resolve Resource
      ↓
Validate scale container
      ↓
Validate x
      ↓
Validate y
      ↓
Validate z
      ↓
Construct AtlasSpatialScale
      ↓
Commit Scale

An invalid request must never partially mutate the existing Scale.

Example:

Existing:
(1, 2, 3)


Request:
(4, 0, 6)

Because y = 0 is invalid, the entire request fails.

Result remains:

(1, 2, 3)

Not:

(4, 2, 3)

and not:

(4, 0, 6)
22. Unknown Resource

If the supplied AtlasID does not identify a Resource in the Project:

scale_resource
      ↓
Resource resolution
      ↓
failure

No spatial state may be created for the unknown Resource.

Existing Resources must remain unchanged.

23. Idempotency

Scale is idempotent.

Given:

Scale = (2, 3, 4)

and the same request:

Scale = (2, 3, 4)

executed repeatedly:

Result remains:
(2, 3, 4)

There must be no cumulative behavior.

Therefore:

Scale(S, X)
Scale(S, X)
Scale(S, X)

always produces:

X
24. Determinism

Given:

same initial Resource state
+
same Scale command

the resulting state must always be identical.

No:

randomness
timing
renderer state
Scene state
selection state
AI
Agent
external state

may influence the result.

25. Scene Independence

ENG-055 must not require an AtlasScene.

This must be valid conceptually:

project = AtlasProject("Test")
application = AtlasApplication(project)

Scale must operate through:

AtlasProject
AtlasResourceRegistry
AtlasSpatialStateRegistry

without:

AtlasScene
AtlasSceneNode
Three.js
WebGL
renderer
camera

The Phase 10 architecture explicitly keeps Scene/Gizmo presentation concerns separate from canonical engineering mutation.

26. Gizmo Independence

AtlasGizmo already has a scale manipulation mode.

ENG-055 must not modify Gizmo behavior.

The existing flow remains:

Selection
    ↓
Gizmo
    ├── mode = scale
    ├── axis = x/y/z
    └── target node_id
    ↓
future controller/application logic
    ↓
scale_resource

The Gizmo does not itself perform Resource Scale mutation.

The existing ENG-050 specification explicitly excludes actual translation, rotation, and scaling from the Gizmo responsibility.

27. SceneNode Independence

ENG-055 must not mutate:

AtlasSceneNode.scale

directly.

AtlasSceneNode remains a presentation/workspace representation.

ENG-055 establishes canonical Resource-associated scale independently.

A later synchronization or rendering specification may map canonical engineering state into presentation state, but that is outside ENG-055.

28. Selection Independence

ENG-055 must not:

select Resource
deselect Resource
change SelectionState
create SelectionState
depend on selected Resource

The target is supplied explicitly through AtlasID.

This maintains the existing identity-based interaction model.

29. Renderer Independence

ENG-055 must not import or depend on:

three
three.js
WebGL
WebGPU
OpenGL
D5
Lumion
any renderer

No visual representation is established here.

30. Resource State Preservation

A successful Scale operation must preserve:

AtlasID
Classification
Name
Properties
Relationships
Metadata
Semantic Tags
Categories
Lifecycle

Only:

Spatial Scale

may change.

31. Relationship Preservation

Scale must not modify:

AtlasRelationship
AtlasResourceGraph
relationship type
source
target
relationship metadata

Scaling a Resource must not alter its engineering relationships.

32. Registry Preservation

Scale must not:

register Resource
unregister Resource
create alternate Resource registry
change Resource Registry ordering
duplicate Resource

The canonical Resource Registry remains authoritative.

33. No Geometry Semantics

ENG-055 does not establish:

mesh scaling
vertex transformation
bounding-box mutation
physical dimension recalculation
area recalculation
volume recalculation
mass recalculation
quantity recalculation
material quantity recalculation
structural recalculation

Those belong to future Geometry, Engineering Semantics, Validation, Constraint, or domain-specific capabilities.

This distinction is critical for keeping Scale from silently becoming a geometry-engineering system.

34. No Physical Dimension Mutation

This operation:

Scale X = 2

does not automatically mean:

Width × 2

inside:

Resource.Properties

and does not automatically update:

length
width
height
area
volume
quantity
cost

Those relationships require explicit future semantics.

ENG-055 only establishes the canonical spatial Scale factor.

35. Proposed Domain Type

The spatial module should expose:

@dataclass(frozen=True, slots=True)
class AtlasSpatialScale:
    x: float
    y: float
    z: float

Validation:

x > 0
y > 0
z > 0

with every value finite and numeric.

It should expose:

as_mapping()

returning:

{
    "x": float,
    "y": float,
    "z": float,
}
36. Spatial Registry API

ENG-055 adds:

set_scale(
    resource_id: AtlasID,
    scale: AtlasSpatialScale,
) -> None
get_scale(
    resource_id: AtlasID,
) -> AtlasSpatialScale | None
require_scale(
    resource_id: AtlasID,
) -> AtlasSpatialScale

The existing registry remains the owner of spatial state.

No new Scale-specific registry is introduced.

37. Resource Lifecycle

When a Resource is created:

Position = (0, 0, 0)
Rotation = (0, 0, 0)
Scale    = (1, 1, 1)

When a Resource is removed:

Position → removed
Rotation → removed
Scale    → removed

No orphan spatial state may remain.

38. Command Validation Matrix
Input	Requirement	Result
resource_id	AtlasID	Required
scale	mapping/dict	Required
scale.x	finite numeric > 0	Required
scale.y	finite numeric > 0	Required
scale.z	finite numeric > 0	Required
missing x	invalid	Reject
missing y	invalid	Reject
missing z	invalid	Reject
extra component	invalid	Reject
zero	invalid	Reject
negative	invalid	Reject
NaN	invalid	Reject
±∞	invalid	Reject
bool	invalid	Reject
string numeric	invalid	Reject
unknown Resource	invalid	Reject
39. Query Contract

The query:

AtlasQuery(
    name="get_resource_scale",
    parameters={
        "resource_id": resource_id,
    },
)

must:

validate resource_id as AtlasID;
require the Resource to exist;
resolve canonical Scale state;
return the Scale mapping.

Expected:

{
    "x": 1.0,
    "y": 1.0,
    "z": 1.0,
}

for a newly created Resource.

40. Testing Strategy

Create:

tests/test_resource_scale.py

Focused command:

pytest tests/test_resource_scale.py -q

The test suite must establish the contract before ENG-055 is considered complete.

41. Required RED Test Categories
Command surface

Verify:

scale_resource
AtlasCommand
resource_id
scale
Application boundary

Verify:

AtlasApplication.execute()

is the mutation entry point.

Query boundary

Verify:

get_resource_scale
AtlasApplication.query()
Identity

Verify:

AtlasID

is authoritative.

Absolute semantics

Verify:

scale = (2, 3, 4)
scale = (5, 6, 7)

produces:

(5, 6, 7)

rather than cumulative scaling.

Non-uniform scale

Verify:

(2, 3, 0.5)

is valid.

Default state

Verify:

(1, 1, 1)

after Resource creation.

Validation

Verify rejection of:

0
negative
NaN
∞
bool
strings
None
missing components
extra components
Atomicity

Verify invalid Scale does not modify the previous Scale.

Idempotency

Verify identical Scale requests produce identical state.

Resource preservation

Verify Resource metadata/state remains unchanged.

Move isolation

Verify Scale does not modify Position.

Rotate isolation

Verify Scale does not modify Rotation.

Scene independence

Verify Scale requires no Scene.

Renderer independence

Verify no renderer dependency.

Resource-model isolation

Verify:

not hasattr(resource, "scale")

and:

not hasattr(resource, "transform")
Resource isolation

Scaling Resource A must not change Resource B.

Determinism

Identical initial state + identical request must yield identical output.

42. Full Regression Requirement

ENG-055 is not complete merely because:

tests/test_resource_scale.py

passes.

The full suite must remain green:

pytest -q

The existing baseline entering ENG-055 is:

1741 passed

Therefore, assuming the new Scale suite contributes N tests, expected full regression is:

1741 + N passed
0 failed
0 errors

No existing tests may be weakened or removed to accommodate Scale.

43. Explicit Non-Goals

ENG-055 does not include:

Resource Create
Resource Move
Resource Rotate
Resource Delete
Resource Duplicate


SceneNode scaling
Gizmo implementation
Gizmo mutation
Selection
Picking
Raycasting
Rendering
Three.js
Camera
Navigation


Geometry transformation
Mesh transformation
Physical dimension editing
Property recalculation
Quantity recalculation
Cost recalculation
Structural recalculation


Undo / Redo
History
Transactions
Persistence
Serialization
Import / Export


Constraint engine
Constraint solving
Validation-runtime expansion


Agents
AI
LLM
Orchestration


Multi-select scaling
Uniform-scale lock
Axis snapping
Grid snapping
Constraint-based scaling

These remain outside ENG-055.

44. Future Compatibility

ENG-055 must leave clean boundaries for:

ENG-056 Delete
      ↓
ENG-057 Duplicate

and future systems:

Validation
Constraints
Geometry
Physical dimensions
History
Persistence
Agents
AI
UI
Renderer
BIM
Interoperability
Provenance

None of these should require replacing:

AtlasResource
AtlasProject
AtlasResourceRegistry
AtlasApplication
AtlasID
AtlasSpatialStateRegistry
45. Architecture Invariants

ENG-055 must preserve:

AtlasID
    = canonical engineering identity


AtlasProject
    = Project ownership boundary


AtlasResourceRegistry
    = canonical Resource registry


AtlasApplication
    = application interaction boundary


AtlasCommand
    = intent


AtlasQuery
    = read request


AtlasResource
    = canonical Resource model


AtlasScene
    = presentation/workspace state


AtlasSceneNode
    = viewport identity + presentation transform


AtlasGizmo
    = manipulation intent/state

No subsystem introduced by ENG-055 may violate these boundaries.

46. Final ENG-055 Architecture
                    ATLAS
                      │
               Canonical Core
                      │
              AtlasApplication
                      │
          ┌───────────┴───────────┐
          │                       │
      Commands                 Queries
          │                       │
          ▼                       ▼
    scale_resource       get_resource_scale
          │                       │
          └───────────┬───────────┘
                      ▼
                 AtlasProject
                      │
       ┌──────────────┴──────────────┐
       │                             │
Resource Registry           Spatial State Registry
       │                             │
 AtlasResource                 AtlasID → Spatial State
                                     │
                          ┌──────────┼──────────┐
                          │          │          │
                       Position   Rotation    Scale

The critical invariant is that Scale is one additional component of the already-established project-scoped spatial state, not a new Resource model.

47. Completion Criteria

ENG-055 is complete only when all of the following are true.

Specification
Scale semantics explicitly defined        ✅
Absolute semantics defined                 ✅
Scale representation defined               ✅
Validation defined                         ✅
Atomicity defined                          ✅
Canonical ownership defined                ✅
RED
tests/test_resource_scale.py exists        ⏳
Focused tests fail for expected reasons    ⏳
Implementation
scale_resource command                     ⏳
get_resource_scale query                   ⏳
AtlasSpatialScale                          ⏳
SpatialStateRegistry integration           ⏳
Default scale = (1,1,1)                    ⏳
Resource isolation                         ⏳
Move/Rotate compatibility                  ⏳
GREEN
Focused Scale tests pass                   ⏳
Regression
Full Atlas suite passes                    ⏳
No ENG-052 regression                      ⏳
No ENG-053 regression                      ⏳
No ENG-054 regression                      ⏳
No Agent regression                        ⏳
Checkpoint
ENG-055 = COMPLETE
48. Decision Freeze

The following decisions are now the proposed non-negotiable ENG-055 contract:

1. Scale is canonical Resource-associated spatial state.


2. Scale is keyed by AtlasID.


3. Scale is owned by the Project-scoped spatial-state boundary.


4. Scale is NOT stored on AtlasResource.


5. Scale is NOT owned by AtlasSceneNode.


6. Scale is NOT implemented by AtlasGizmo.


7. Scale is an absolute operation.


8. Scale supports independent X/Y/Z factors.


9. Scale factors are dimensionless.


10. Each scale factor must be finite and strictly > 0.


11. Zero scale is invalid.


12. Negative scale is invalid.


13. Scale defaults to (1,1,1).


14. Scale does not mutate Position.


15. Scale does not mutate Rotation.


16. Scale does not mutate Resource properties.


17. Scale does not mutate Relationships.


18. Scale is deterministic.


19. Scale is idempotent.


20. Invalid Scale requests are atomic.


21. Resource lookup remains canonical through AtlasProject/Registry.


22. Mutation enters through AtlasApplication.execute().


23. Reading enters through AtlasApplication.query().


24. No Scene is required.


25. No renderer is required.


26. No Agent/AI is required.


27. Physical dimensions are NOT modified by Scale.


28. Geometry recalculation is NOT part of ENG-055.


29. No second Resource or spatial registry is introduced.

The source archive supports the Phase 11 sequence Create → Move → Rotate → Scale → Delete → Duplicate and the core rule that these capabilities extend the application boundary while preserving the canonical Resource architecture.
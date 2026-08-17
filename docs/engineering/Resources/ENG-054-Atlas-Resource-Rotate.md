ENG-054 — Atlas Resource Rotate
Status: Complete
Phase: Phase 11 — Resource Editing
Depends On: ENG-053 — Atlas Resource Move
Previous: ENG-053 — Atlas Resource Move
Next: ENG-055 — Atlas Resource Scale
1. Purpose
ENG-054 introduces the Rotate capability within Phase 11 — Resource Editing.
Phase 11 establishes canonical Resource editing capabilities:
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
The purpose of ENG-054 is to establish a deterministic, canonical operation for setting the spatial rotation associated with an Atlas Resource.
ENG-054 extends the spatial state architecture established by ENG-053 without changing the canonical AtlasResource model, without transferring ownership to the 3D Scene, and without introducing a second Resource or transformation model.
2. Architectural Position
Atlas engineering mutation follows the existing application boundary:
User / UI / Agent / External Interface
                    ↓
              AtlasCommand
                    ↓
           AtlasApplication
                    ↓
              AtlasProject
                    ↓
        Canonical Atlas State
For ENG-054:
AtlasCommand
     │
     │ rotate_resource
     ▼
AtlasApplication.execute()
     │
     ▼
AtlasProject
     │
     ▼
Canonical Spatial State
     │
     └── AtlasID → Rotation
Reads follow:
AtlasQuery
     │
     │ get_resource_rotation
     ▼
AtlasApplication.query()
     │
     ▼
AtlasProject
     │
     ▼
Canonical Spatial State
The application boundary remains a thin interaction boundary and does not become a second engineering model. This is consistent with the established Atlas command architecture, where commands represent intent rather than containing domain rules. commands.pyPY
3. Relationship to ENG-053
ENG-053 established Resource-associated canonical spatial state.
Its frozen ownership model is:
AtlasProject
├── AtlasResourceRegistry
└── Canonical Spatial State
       └── AtlasID → Position
ENG-054 extends this to:
AtlasProject
├── AtlasResourceRegistry
└── Canonical Spatial State
       ├── AtlasID → Position
       └── AtlasID → Rotation
The same Project-scoped spatial boundary is used.
ENG-054 must not introduce:
RotationRegistry
ResourceRotationRegistry
TransformRegistry
SceneRotationRegistry
or any competing spatial ownership mechanism.
4. Canonical Resource Model
The canonical AtlasResource model remains unchanged:
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
ENG-054 must not add:
rotation
transform
position
scale
to AtlasResource.
The architectural foundation established by ENG-053 explicitly separates Resource state from spatial transformation state and prevents convenient but unauthorized additions to AtlasResource. 
5. Canonical Meaning of Rotate
ENG-054 defines:
Rotate(Resource, Rotation) means: set the canonical spatial rotation associated with the identified Resource to the supplied absolute 3D rotation.

Rotation is therefore an absolute operation.
Given:
Current Rotation = (10°, 20°, 30°)
and:
Rotate = (40°, 50°, 60°)
the result is:
Rotation = (40°, 50°, 60°)
It is not:
(50°, 70°, 90°)
and it is not interpreted as a rotation delta.
6. Rotation Representation
Rotation consists of three Euler components:
Rotation
├── x
├── y
└── z
The canonical representation is:
AtlasSpatialRotation(
    x=...,
    y=...,
    z=...,
)
The object is immutable.
The canonical state exposes the components as a mapping:
{
    "x": 10.0,
    "y": 20.0,
    "z": 30.0,
}
7. Angular Unit
ENG-054 establishes:
Rotation values are expressed in degrees.

Example:
x = 90.0
y = 0.0
z = 45.0
means:
90° around X
0° around Y
45° around Z
Atlas does not silently convert the canonical values to radians.
Renderer-specific conversion, if required later, belongs outside ENG-054.
8. Euler Representation
ENG-054 uses three scalar Euler components.
It does not introduce:
Quaternion
RotationMatrix
TransformationMatrix
as canonical Resource state.
No renderer-specific representation is allowed to become the Atlas canonical model.
Future specifications may introduce alternate representations or conversion mechanisms without replacing the ENG-054 canonical meaning.
9. Rotation Range
ENG-054 does not impose a [0°, 360°) range.
The following are valid finite values:
0°
90°
180°
270°
360°
450°
-90°
-180°
Rotation normalization is not part of ENG-054.
For example:
450°
is not silently rewritten to:
90°
by the canonical spatial state.
10. Numeric Validation
Each rotation component must be:
numeric
finite
Valid:
0
45
-90
360
450.5
Invalid:
NaN
+∞
-∞
None
"90"
True
False
Boolean values are explicitly invalid even though Python treats bool as a subclass of int.
11. Rotation Payload
The command payload must contain exactly:
resource_id
rotation
with:
rotation.x
rotation.y
rotation.z
Example:
AtlasCommand(
    name="rotate_resource",
    payload={
        "resource_id": resource.aid,
        "rotation": {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        },
    },
)
Missing axes are invalid.
Unexpected axes are invalid.
12. Resource Identity
Rotation targets a Resource exclusively through AtlasID.
Valid:
resource.aid
Invalid target forms include:
Resource name
Scene node ID
selection object
registry index
array index
Resource object as identifier
The engineering identity remains AtlasID.
The viewport identity node_id remains separate. ENG-050 explicitly preserves this distinction. 
13. Default Rotation
Every newly created Resource receives:
Rotation = (0.0, 0.0, 0.0)
This is the neutral spatial rotation.
Therefore:
Create Resource
      ↓
Position = (0, 0, 0)
Rotation = (0, 0, 0)
ENG-054 must not alter the existing ENG-052 Resource creation semantics.
14. Application Command
The canonical command is:
rotate_resource
Example:
AtlasCommand(
    name="rotate_resource",
    payload={
        "resource_id": resource.aid,
        "rotation": {
            "x": 90.0,
            "y": 20.0,
            "z": 45.0,
        },
    },
)
Commands express intent only.
The command must not implement:
validation rules
Resource lookup
spatial mutation
Scene mutation
renderer operations
AI behavior
15. Application Query
The canonical query is:
get_resource_rotation
Example:
AtlasQuery(
    name="get_resource_rotation",
    parameters={
        "resource_id": resource.aid,
    },
)
Expected output:
{
    "x": 90.0,
    "y": 20.0,
    "z": 45.0,
}
16. Canonical Ownership
Rotation belongs to the Project-owned canonical spatial state.
Conceptually:
AtlasProject
│
├── AtlasResourceRegistry
│      └── AtlasResource
│
└── Canonical Spatial State
       └── AtlasID
             ├── Position
             └── Rotation
The spatial registry does not own Resources.
The Resource Registry remains authoritative for Resource existence.
17. Position Independence
Rotate must change only Rotation.
Example:
Before:
Position = (100, 200, 300)
Rotation = (0, 0, 0)

Rotate:
(45, 10, 90)
After:
Position = (100, 200, 300)
Rotation = (45, 10, 90)
Position must remain unchanged.
18. Resource-State Preservation
Successful rotation must preserve:
AtlasID
Classification
Name
Properties
Relationships
Metadata
Semantic Tags
Categories
Lifecycle
Only Rotation may change.
19. Relationship Preservation
Rotate must not alter:
AtlasRelationship
AtlasResourceGraph
relationship source
relationship target
relationship type
relationship metadata
Resource relationships remain exactly as before the operation.
20. Move Independence
Move and Rotate are independent spatial capabilities:
Move
  → Position

Rotate
  → Rotation
Executing Rotate must not modify Position.
Executing Move must not modify Rotation.
Example:
Move:
Position = (10, 20, 30)

Rotate:
Rotation = (10, 45, 90)
Final state:
Position = (10, 20, 30)
Rotation = (10, 45, 90)
21. Atomicity
Validation must be completed before mutation.
Required sequence:
Receive command
      ↓
Validate resource_id
      ↓
Resolve Resource
      ↓
Validate rotation container
      ↓
Validate x
      ↓
Validate y
      ↓
Validate z
      ↓
Construct AtlasSpatialRotation
      ↓
Commit rotation
Example:
Existing:
(10, 20, 30)

Request:
(40, NaN, 60)
must fail and leave:
(10, 20, 30)
unchanged.
No partial mutation is permitted.
22. Unknown Resource
If resource_id does not resolve to a Resource in the Project:
rotate_resource
      ↓
Resource resolution
      ↓
failure
The operation must not create spatial state for the unknown Resource.
Other Resources must remain unchanged.
23. Idempotency
Rotation is idempotent.
Given:
Rotation = (10, 20, 30)
executing the same absolute operation repeatedly must always result in:
Rotation = (10, 20, 30)
There is no cumulative behavior.
24. Determinism
Identical initial state plus identical Rotate command produces identical resulting state.
No:
randomness
timing
renderer state
Scene state
selection state
AI
Agent
external environment
may influence the result.
25. Scene Independence
ENG-054 must not require AtlasScene.
Rotation must be executable using only:
AtlasProject
AtlasResourceRegistry
Canonical Spatial State
AtlasApplication
It must not directly depend on:
AtlasScene
AtlasSceneNode
Camera
Navigation
Renderer
Three.js
WebGL
The existing Atlas architecture intentionally separates presentation/workspace state from canonical engineering state. 
26. Gizmo Independence
AtlasGizmo already provides:
mode = rotate
but it does not become the owner of Resource rotation.
The intended future interaction is:
Selection
    ↓
Gizmo
    ├── mode = rotate
    ├── axis
    └── node_id
    ↓
Application interaction
    ↓
rotate_resource
    ↓
Canonical spatial Rotation
The Gizmo itself performs no Resource mutation.
ENG-050 explicitly excludes actual rotation transformation from the Gizmo responsibility. ENG-050-Atlas-Gizmo.mdMD
27. SceneNode Independence
ENG-054 must not directly modify:
AtlasSceneNode.rotation
The SceneNode remains presentation/workspace state.
Future synchronization between canonical Resource state and presentation state belongs to a later specification.
28. Selection Independence
ENG-054 must not:
select
deselect
change selection
inspect selection
depend on current selection
The Resource is explicitly identified through AtlasID.
29. Renderer Independence
ENG-054 must not introduce renderer dependencies:
three
three.js
WebGL
WebGPU
OpenGL
No visual representation is defined by this specification.
30. Geometry Independence
ENG-054 does not define:
mesh rotation
vertex transformation
geometry transformation
bounding-box changes
physical orientation calculations
Those are future capabilities.
31. Engineering-Semantics Independence
Rotation does not automatically update:
width
length
height
area
volume
quantity
mass
cost
structural properties
material properties
Those are semantic/domain consequences that require explicit future specifications.
32. Spatial Domain Type
The canonical spatial module shall expose:
AtlasSpatialRotation
with:
x: float
y: float
z: float
The value object shall be immutable and validate its components.
It shall provide a mapping representation:
{
    "x": float,
    "y": float,
    "z": float,
}
33. Spatial Registry API
ENG-054 introduces the following spatial-state operations:
set_rotation(
    resource_id: AtlasID,
    rotation: AtlasSpatialRotation,
) -> None
get_rotation(
    resource_id: AtlasID,
) -> AtlasSpatialRotation | None
require_rotation(
    resource_id: AtlasID,
) -> AtlasSpatialRotation
No standalone rotation registry is permitted.
34. Resource Lifecycle
Creation:
Position = (0, 0, 0)
Rotation = (0, 0, 0)
Removal:
Position → removed
Rotation → removed
No orphaned spatial state may remain after Resource removal.
35. RED Phase
The RED phase shall create:
tests/test_resource_rotate.py
The focused suite shall verify the specification before implementation is accepted.
Command:
pytest tests/test_resource_rotate.py -q
The tests must initially fail because the rotate_resource capability has not yet been implemented according to the frozen contract.
Tests must not be weakened to accommodate an implementation.
The direction remains:
Specification
      ↓
RED contract
      ↓
Implementation
      ↓
GREEN
      ↓
Regression
not:
Implementation
      ↓
Modify specification until tests pass
This follows the same RED-phase principle established in the ENG-053 specification. Pasted markdown(5).mdMD
36. RED Test Categories
tests/test_resource_rotate.py must cover at minimum:
Command construction
Application command boundary
Query boundary
AtlasID targeting
Default rotation
Absolute semantics
Degree semantics
Negative rotations
Angles > 360°
Finite numeric validation
Boolean rejection
Missing x/y/z
Extra keys
Invalid rotation container
Unknown Resource
Atomicity
Idempotency
Resource identity preservation
Resource state preservation
Relationship preservation
Move/Rotate isolation
Scene independence
Gizmo independence
Renderer independence
AtlasResource isolation
Resource-to-Resource isolation
Determinism
37. Public Contract
The frozen command surface is:
AtlasCommand(
    name="rotate_resource",
    payload={
        "resource_id": resource.aid,
        "rotation": {
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
        },
    },
)
The frozen query surface is:
AtlasQuery(
    name="get_resource_rotation",
    parameters={
        "resource_id": resource.aid,
    },
)
38. Explicit Non-Goals
ENG-054 does not include:
Resource Scale
Resource Delete
Resource Duplicate

SceneNode rotation
Gizmo mutation
Selection
Picking
Raycasting
Rendering
Three.js
Camera
Navigation

Quaternions as canonical state
Rotation matrices as canonical state
Automatic angle normalization

Geometry transformation
Physical dimension transformation
Engineering property recalculation
Structural validation

Undo / Redo
History
Transactions
Persistence
Serialization
Import / Export

Constraint engine
Constraint solving

Agents
AI
LLM
Orchestration
39. Architecture Invariants
ENG-054 shall preserve:
AtlasID
    = canonical engineering identity

AtlasProject
    = Resource ownership boundary

AtlasResourceRegistry
    = canonical Resource registry

AtlasApplication
    = application interaction boundary

AtlasCommand
    = mutation intent

AtlasQuery
    = read request

AtlasResource
    = canonical Resource model

AtlasScene
    = presentation/workspace state

AtlasSceneNode
    = viewport/presentation identity

AtlasGizmo
    = manipulation intent/state
No ENG-054 implementation may violate these boundaries.
40. Final Architecture
                         ATLAS
                           │
                    Canonical Core
                           │
                   AtlasApplication
                           │
              ┌────────────┴────────────┐
              │                         │
          Commands                    Queries
              │                         │
              ▼                         ▼
     rotate_resource          get_resource_rotation
              │                         │
              └────────────┬────────────┘
                           ▼
                      AtlasProject
                           │
                  Spatial State Registry
                           │
                     ┌─────┴─────┐
                     │           │
                  Position    Rotation
The important invariant is:
ENG-054 adds Rotation to the existing canonical spatial-state boundary. It does not create another Resource model, another Registry, or another transformation owner.

41. Completion Criteria
ENG-054 is complete only when:
Specification
Rotation semantics frozen              ✅
Absolute semantics frozen              ✅
Degrees convention frozen              ✅
Canonical ownership frozen             ✅
Validation frozen                      ✅
Atomicity frozen                       ✅
RED
tests/test_resource_rotate.py exists   ☐
Focused suite fails as expected        ☐
Implementation
AtlasSpatialRotation                   ☐
set_rotation                           ☐
get_rotation                           ☐
require_rotation                       ☐
rotate_resource                        ☐
get_resource_rotation                  ☐
Default rotation                       ☐
GREEN
Focused ENG-054 tests pass             ☐
Regression
ENG-052 compatibility                  ☐
ENG-053 compatibility                  ☐
Agent compatibility                    ☐
Full Atlas suite                       ☐
Checkpoint
ENG-054 = COMPLETE
42. Decision Freeze
The following decisions constitute the ENG-054 contract:
1. Rotate is canonical Resource-associated spatial state.

2. Rotation is keyed by AtlasID.

3. Rotation is owned by Project-scoped spatial state.

4. AtlasResource remains unchanged.

5. AtlasSceneNode remains unchanged.

6. AtlasGizmo remains unchanged.

7. Rotation is an absolute operation.

8. Rotation uses Euler X/Y/Z components.

9. Rotation values are expressed in degrees.

10. Rotation accepts values outside 0–360°.

11. Rotation is not automatically normalized.

12. Every component must be numeric and finite.

13. Boolean values are invalid.

14. Newly created Resources start at (0,0,0).

15. Rotate does not modify Position.

16. Rotate does not modify Resource properties.

17. Rotate does not modify Relationships.

18. Rotate is deterministic.

19. Rotate is idempotent.

20. Invalid rotation requests are atomic.

21. Unknown Resources cannot receive spatial state.

22. Mutation enters through AtlasApplication.execute().

23. Reads enter through AtlasApplication.query().

24. No Scene is required.

25. No Renderer is required.

26. No Agent or AI is required.

27. No geometry semantics are defined.

28. No physical dimension semantics are defined.

29. No second spatial or Resource registry is introduced.
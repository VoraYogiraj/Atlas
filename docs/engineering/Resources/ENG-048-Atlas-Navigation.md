ENG-048 — Atlas Navigation

Document Type: Engineering Resource Specification
Status: Proposed / Implementation Complete
Phase: Phase 10 — 3D Workspace
Depends On: ENG-039, ENG-040, ENG-045, ENG-046, ENG-047
Primary Component: AtlasNavigation
Implementation: packages/atlas/src/atlas/application/navigation.py
Tests: packages/atlas/tests/test_navigation.py

1. Purpose

ENG-048 defines Atlas Navigation, the renderer-independent controller responsible for applying deterministic viewport-navigation operations to an existing AtlasCamera.

Atlas Navigation provides the application-level semantics for:

orbiting around a camera target,
panning the camera and target,
zooming according to camera projection,
restoring the camera to its initial navigation state.

The capability exists to establish a stable application contract between the Atlas workspace model and future rendering/input implementations.

The central architectural principle is:

AtlasNavigation
       │
       ▼
AtlasCamera

AtlasNavigation controls camera movement behavior.

AtlasCamera owns camera viewpoint state.

Neither component owns a renderer, browser input system, scene, engineering model, or selection system.

2. Architectural Intent

Atlas Navigation is intentionally renderer-independent.

The Python application layer defines what navigation means, while a future TypeScript/Three.js workspace can determine how user input is converted into navigation commands and how the resulting state is rendered.

The intended future relationship is:

User Input
    │
    ▼
TypeScript Input Adapter
    │
    ▼
Atlas Navigation Contract
    │
    ▼
AtlasCamera State
    │
    ▼
Three.js Camera Adapter
    │
    ▼
Renderer

The renderer must not become the source of navigation semantics.

3. Scope
3.1 In Scope

ENG-048 owns:

Binding to an existing AtlasCamera.
Orbiting around the camera target.
Panning camera and target together.
Perspective zoom.
Orthographic zoom.
Capturing the initial camera viewpoint.
Resetting the camera to the captured viewpoint.
Deterministic numeric validation.
Atomic failure behavior.
Renderer-independent navigation mathematics.
3.2 Out of Scope

ENG-048 does not own:

mouse input,
keyboard input,
touch input,
gamepad input,
browser events,
viewport events,
Three.js,
WebGL,
WebGPU,
raycasting,
picking,
highlighting,
selection,
multi-selection,
gizmos,
transform manipulation,
engineering-resource editing,
relationship editing,
scene ownership,
resource ownership,
persistence,
serialization,
import/export,
agents,
AI,
navigation sensitivity configuration,
damping,
inertia,
key bindings,
mouse mappings.

These capabilities belong to other application or presentation layers.

4. Component Definition
class AtlasNavigation:
    def __init__(
        self,
        *,
        camera: AtlasCamera,
    ) -> None

AtlasNavigation is a controller over an existing AtlasCamera.

It does not create or replace the camera.

5. Public API
5.1 Constructor
AtlasNavigation(
    *,
    camera: AtlasCamera,
)
Requirements

camera must be an instance of AtlasCamera.

Invalid values raise:

TypeError

The supplied camera becomes the camera controlled by the Navigation instance.

5.2 Camera Property
@property
def camera(self) -> AtlasCamera

Returns the camera controlled by the navigation instance.

The returned object is the existing AtlasCamera, not a copy.

Example:

camera = AtlasCamera(
    camera_id="main",
    name="Main Camera",
)


navigation = AtlasNavigation(camera=camera)


assert navigation.camera is camera
6. Orbit
def orbit(
    *,
    delta_yaw_degrees: float,
    delta_pitch_degrees: float,
) -> None

Orbit rotates the camera around its target.

The camera target remains unchanged.

The camera-to-target distance remains unchanged.

Example

Initial state:

Camera: (0, 0, 10)
Target: (0, 0, 0)

Positive 90° yaw:

Camera: (10, 0, 0)
Target: (0, 0, 0)

Negative 90° yaw:

Camera: (-10, 0, 0)
Target: (0, 0, 0)

Positive 90° pitch from:

(0, 0, 10)

produces:

(0, 10, 0)

The target remains:

(0, 0, 0)
7. Orbit Mathematics

Let:

C = camera position
T = camera target
O = C - T

where O is the camera offset from the target.

Navigation operates on O, then reconstructs the camera position.

7.1 Yaw

For yaw angle θ:

x' = cos(θ)x + sin(θ)z
y' = y
z' = -sin(θ)x + cos(θ)z

The resulting vector is then used as the new camera-target offset.

7.2 Pitch

For pitch angle φ:

x' = x
y' = cos(φ)y + sin(φ)z
z' = -sin(φ)y + cos(φ)z

The pitch convention is defined so that positive pitch moves the camera upward according to the ENG-048 coordinate convention.

7.3 Position Reconstruction

After rotation:

C' = T + O'

The target itself is not modified.

7.4 Distance Invariant

Orbit must preserve camera-target distance.

Before:

D = |C - T|

After:

D' = |C' - T|

The operation must preserve:

D' ≈ D

within normal floating-point precision.

8. Pan
def pan(
    *,
    delta_x: float,
    delta_y: float,
) -> None

Pan translates the camera and target by the same world-space displacement.

The displacement is:

D = (delta_x, delta_y, 0)

The new state is:

C' = C + D
T' = T + D

Therefore:

C' - T' = C - T

The camera-target relationship remains unchanged.

ENG-048 defines pan using world-space displacement.

Viewport-relative or screen-space pan behavior is outside this contract.

9. Zoom
def zoom(
    *,
    delta: float,
) -> None

Zoom behavior depends on camera projection.

9.1 Perspective Projection

For perspective cameras:

positive delta → move toward target
negative delta → move away from target

Let:

O = C - T
D = |O|

The new distance is:

D' = D - delta

The direction remains unchanged:

N = O / D

The new camera position is:

C' = T + N × D'

The target remains unchanged.

9.2 Perspective Zoom Validation

The resulting camera-target distance must remain positive.

If:

D' <= 0

the operation is invalid and must raise:

ValueError

The camera must remain unchanged after the failure.

9.3 Orthographic Projection

For orthographic cameras, zoom does not modify camera position.

Instead:

new_scale = current_scale - delta

Therefore:

positive delta → zoom in
negative delta → zoom out

The resulting scale must remain positive.

If:

new_scale <= 0

the operation raises:

ValueError

and leaves the camera unchanged.

9.4 Zero Zoom

A zero zoom:

navigation.zoom(delta=0)

is valid and performs no state change.

10. Reset
def reset() -> None

When an AtlasNavigation instance is constructed, it captures the initial navigation viewpoint.

The captured state includes:

position
target
up
projection
field_of_view_degrees
orthographic_scale
near_clip
far_clip

reset() restores that complete camera state.

Reset does not create a new camera.

It restores the existing bound camera.

11. Initial Viewpoint Semantics

The initial viewpoint is captured when AtlasNavigation is constructed.

Example:

camera = AtlasCamera(
    camera_id="main",
    name="Main",
)


navigation = AtlasNavigation(camera=camera)

The state of camera at this moment becomes the reset state.

Subsequent camera modifications do not automatically change the reset state.

Therefore:

Construction
     │
     ▼
Capture initial viewpoint
     │
     ▼
Navigation operations
     │
     ▼
Modified camera
     │
     ▼
reset()
     │
     ▼
Original captured viewpoint
12. Numeric Validation

Navigation accepts numeric int and float values.

Boolean values are explicitly rejected even though Python considers bool a subclass of int.

For example:

delta=1

is valid.

delta=1.5

is valid.

delta=True

is invalid.

Invalid numeric arguments raise:

TypeError
12.1 Validated Parameters

The following parameters require numeric validation:

delta_yaw_degrees
delta_pitch_degrees
delta_x
delta_y
delta

Validation occurs before camera mutation.

13. Atomicity

Navigation operations must be atomic with respect to validation failures.

The rule is:

Validate
   ↓
Calculate
   ↓
Validate resulting state
   ↓
Mutate Camera

not:

Mutate Camera
   ↓
Discover invalid state

For example, invalid perspective zoom:

navigation.zoom(delta=1000)

must not partially move the camera before raising ValueError.

Likewise, invalid orthographic zoom must not modify the scale before raising.

Invalid numeric input must leave all camera state unchanged.

14. Camera Boundary

AtlasNavigation may read and modify the supplied AtlasCamera through its public API.

It must not duplicate camera ownership.

The following state belongs to AtlasCamera:

camera_id
name
position
target
up
projection
field_of_view_degrees
orthographic_scale
near_clip
far_clip

Navigation may retain the initial viewpoint snapshot required by reset(), but this does not constitute a second camera model.

Navigation must not create:

AtlasCamera

internally.

15. Scene Boundary

AtlasNavigation does not own or manipulate AtlasScene.

It must not:

create scenes,
delete scenes,
add scene nodes,
remove scene nodes,
change node hierarchy,
change visibility,
modify node resources,
modify node transforms.

The relationship is:

AtlasScene       AtlasCamera
     │                │
     │                │
     └──── Application ┘
             │
        AtlasNavigation

Navigation operates exclusively on camera state.

16. Resource and Relationship Boundary

ENG-048 must not directly or indirectly become an engineering-model editing mechanism.

Navigation must not modify:

AtlasResource
AtlasRelationship
AtlasResourceGraph
AtlasProject
AtlasResourceRegistry

Camera movement has no semantic effect on engineering resources.

17. Selection Boundary

Selection belongs to ENG-049.

ENG-048 must not implement:

selection,
picking,
hit testing,
raycasting,
highlighting,
multi-selection,
selection synchronization.

Navigation therefore does not inspect or modify:

AtlasResourceSelection

or future selection state.

18. Gizmo Boundary

Gizmos belong to ENG-050.

Navigation must not provide:

translation gizmos,
rotation gizmos,
scale gizmos,
transform handles,
object manipulation controls.

Camera movement and object manipulation are separate capabilities.

19. Basic Editing Boundary

Basic engineering/object editing belongs to ENG-051.

Navigation must not modify:

resource properties
resource geometry
resource relationships
scene-node engineering meaning

Navigation changes only viewpoint state.

20. Renderer Boundary

ENG-048 has no renderer dependency.

The implementation must not import or depend upon:

Three.js
WebGL
WebGPU
Browser DOM APIs
Canvas APIs

The Python implementation must remain usable without a rendering backend.

Future rendering adapters may translate:

AtlasCamera
    ↓
Three.js Camera

but the renderer does not become the canonical camera state.

21. Input Boundary

ENG-048 does not process physical input.

There is no support in this milestone for:

mouse
keyboard
touch
gamepad
pointer events
wheel events
browser events

Input adapters belong outside the navigation model.

Future input mapping may translate:

mouse drag
    ↓
delta yaw/pitch
    ↓
AtlasNavigation.orbit(...)

or:

mouse wheel
    ↓
zoom delta
    ↓
AtlasNavigation.zoom(...)

but that mapping is not part of ENG-048.

22. Configuration Boundary

ENG-048 deliberately does not introduce configurable interaction behavior.

The following are outside scope:

sensitivity
damping
inertia
acceleration
friction
mouse-button mappings
keyboard mappings
touch gestures

The initial contract uses explicit deterministic numerical operations.

Future UX configuration must not change the core navigation semantics.

23. Determinism

Given the same:

initial AtlasCamera state
+
same navigation operation sequence
+
same numerical inputs

the resulting camera state must be deterministic within expected floating-point precision.

Example:

camera_a = AtlasCamera(...)
camera_b = AtlasCamera(...)


navigation_a = AtlasNavigation(camera=camera_a)
navigation_b = AtlasNavigation(camera=camera_b)


navigation_a.orbit(
    delta_yaw_degrees=45,
    delta_pitch_degrees=15,
)


navigation_b.orbit(
    delta_yaw_degrees=45,
    delta_pitch_degrees=15,
)

must produce equivalent camera states.

Navigation must not depend on:

wall-clock time,
frame rate,
renderer state,
random numbers,
external input state,
global mutable state.
24. Independence

AtlasNavigation must be independently constructible.

It requires only:

AtlasCamera

It does not require:

AtlasWorkspace
AtlasPanel
AtlasView
AtlasScene
AtlasProject
Renderer
Browser

Example:

camera = AtlasCamera(
    camera_id="test-camera",
    name="Test Camera",
)


navigation = AtlasNavigation(camera=camera)

This must be valid without constructing the rest of the UI system.

25. Public API Surface

The intended public API is deliberately limited to:

class AtlasNavigation:
    def __init__(
        self,
        *,
        camera: AtlasCamera,
    ) -> None


    @property
    def camera(self) -> AtlasCamera


    def orbit(
        self,
        *,
        delta_yaw_degrees: float,
        delta_pitch_degrees: float,
    ) -> None


    def pan(
        self,
        *,
        delta_x: float,
        delta_y: float,
    ) -> None


    def zoom(
        self,
        *,
        delta: float,
    ) -> None


    def reset(self) -> None

No additional public navigation API is required for ENG-048.

26. Test Requirements

The ENG-048 test suite must cover the following categories.

26.1 Construction
valid camera accepted,
invalid camera rejected,
camera identity preserved.
26.2 Camera Binding
.camera returns the original camera,
no camera replacement occurs.
26.3 Orbit
positive yaw,
negative yaw,
positive pitch,
combined yaw and pitch,
target preservation,
distance preservation,
deterministic results.
26.4 Pan
X movement,
Y movement,
simultaneous movement,
camera movement,
target movement,
relative-vector preservation.
26.5 Perspective Zoom
positive zoom,
negative zoom,
zero zoom,
target preservation,
direction preservation,
distance change,
invalid resulting distance.
26.6 Orthographic Zoom
positive zoom,
negative zoom,
zero zoom,
position preservation,
target preservation,
invalid resulting scale.
26.7 Reset
initial viewpoint capture,
restoration after orbit,
restoration after pan,
restoration after zoom,
restoration of projection,
restoration of clipping,
repeated reset determinism.
26.8 Validation
invalid numeric values,
boolean rejection,
invalid camera construction,
invalid zoom result.
26.9 Atomicity

Every invalid operation must preserve the camera state exactly.

26.10 Architectural Isolation

Tests must establish that Navigation does not:

own a Scene,
mutate SceneNodes,
access engineering resources,
manipulate relationships,
implement selection,
require a renderer,
require input events.
26.11 Public API

Tests must verify:

from atlas.application import AtlasNavigation

works.

27. Implementation Contract

The canonical implementation is:

packages/atlas/src/atlas/application/navigation.py

The package-level public export is:

from atlas.application import AtlasNavigation

The implementation must remain consistent with the existing AtlasCamera contract established by ENG-047.

28. Future TypeScript / Three.js Integration

ENG-048 is explicitly designed to support a future TypeScript + Three.js workspace.

The intended architecture is:

                    ATLAS APPLICATION
                           │
                 AtlasNavigation
                           │
                      AtlasCamera
                           │
                  API / State Contract
                           │
                           ▼
                    TYPESCRIPT UI
                           │
                 Camera Adapter Layer
                           │
                           ▼
                    THREE.JS RUNTIME
                           │
              THREE.Camera / Renderer

The TypeScript layer may implement:

pointer handling,
mouse controls,
keyboard controls,
touch controls,
viewport integration,
Three.js camera synchronization.

Those capabilities must consume the Atlas contract rather than redefine the engineering/application model.

29. Serialization and Persistence Boundary

ENG-048 does not introduce its own persistence mechanism.

Navigation state is not a separate project/domain persistence model.

If camera state is eventually persisted as part of workspace state, that mechanism must be defined by the appropriate application/project persistence contract.

ENG-048 itself does not implement:

JSON serialization
project save/load
import/export
database persistence
30. Agent and AI Boundary

Navigation is deterministic application behavior.

It does not:

invoke agents,
invoke LLMs,
interpret natural language,
generate engineering decisions,
modify engineering knowledge.

Future agents may request navigation through an appropriate application command layer, but that integration is outside ENG-048.

31. Architectural Invariants

ENG-048 must preserve the following invariants:

Invariant 1 — Camera ownership

AtlasCamera remains the canonical camera state.

Invariant 2 — Navigation ownership

AtlasNavigation owns navigation behavior, not camera identity.

Invariant 3 — Scene isolation

Navigation does not own or mutate AtlasScene.

Invariant 4 — Engineering isolation

Navigation does not mutate resources or relationships.

Invariant 5 — Renderer independence

Navigation works without Three.js or any renderer.

Invariant 6 — Input independence

Navigation does not depend on physical input events.

Invariant 7 — Selection isolation

Selection remains an independent capability owned by ENG-049.

Invariant 8 — Determinism

The same operations produce the same resulting camera state.

Invariant 9 — Atomicity

Invalid operations do not partially mutate the camera.

Invariant 10 — Extension over rewrite

Future TypeScript/Three.js integration must adapt to this contract rather than require replacement of the underlying Atlas camera/navigation model.

32. Completion Criteria

ENG-048 is considered complete when all of the following are true:

 AtlasNavigation exists.
 Navigation binds to an existing AtlasCamera.
 Orbit is implemented.
 Pan is implemented.
 Perspective zoom is implemented.
 Orthographic zoom is implemented.
 Reset is implemented.
 Numeric validation is implemented.
 Boolean numeric values are rejected.
 Invalid zoom operations are atomic.
 Orbit preserves the target.
 Orbit preserves camera-target distance.
 Pan preserves camera-target relationship.
 Zoom follows projection-specific semantics.
 Navigation is renderer-independent.
 Navigation has no Scene ownership.
 Navigation has no engineering-resource ownership.
 Navigation has no selection responsibility.
 Navigation has no input/event responsibility.
 AtlasNavigation is exported from atlas.application.
 Focused ENG-048 tests pass.
 Full Atlas regression passes.
 ENG-048 documentation matches the implemented contract.
Validation result
ENG-048 focused tests
47 passed
898 warnings
0 failures


Full Atlas regression
1455 passed
66062 warnings
0 failures
8.16s

ENG-048 — Atlas Navigation: GREEN / COMPLETE.

33. Phase 10 Position
Phase 10 — 3D Workspace


ENG-046  Atlas Scene          ✅
ENG-047  Atlas Camera         ✅
ENG-048  Atlas Navigation     ✅
ENG-049  Atlas Selection      → Next
ENG-050  Atlas Gizmos
ENG-051  Atlas Basic Editing

ENG-048 therefore establishes the viewpoint/navigation foundation required before selection, manipulation, and editing are introduced.

The specification intentionally keeps the Python Atlas application layer renderer-neutral so that the eventual TypeScript + Three.js workspace can act as a presentation/input layer rather than becoming a competing source of truth.
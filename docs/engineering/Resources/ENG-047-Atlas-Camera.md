ENG-047 — Atlas Camera

**Document ID:** ENG-047  
**Title:** Atlas Camera  
**Version:** 0.1.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-046 — Atlas Scene  
**Phase:** Phase 10 — 3D Workspace  
**Implementation:** Atlas Application / 3D Workspace layer

---

# 1. Purpose

ENG-047 defines the renderer-independent Camera state for the Atlas 3D
Workspace.

The Camera describes a viewpoint over a Scene. It stores presentation state
only; it is not an Atlas Resource, does not own a Scene, and does not alter
canonical engineering information.

```text
AtlasProject / AtlasResource
        ↓
AtlasApplication
        ↓
AtlasWorkspace / AtlasScene
        ↓
AtlasCamera
```

# 2. Scope

ENG-047 defines:

- Camera identity and name
- Position, target, and up-vector
- Perspective and orthographic projection state
- Field of view
- Orthographic scale
- Near and far clipping planes
- State validation
- Direct, deterministic presentation-state mutation
- Renderer independence
- Engineering-state isolation
- Public exports

# 3. Non-Goals

ENG-047 does not implement:

- Orbit, pan, zoom, fly controls, or input handling
- Mouse, touch, keyboard, or gesture processing
- Camera animation, transitions, or bookmarks
- Rendering, matrices, WebGL, WebGPU, Three.js, or Babylon.js
- Ray casting, picking, selection, gizmos, or editing
- Scene ownership, a Camera Registry, persistence, exchange, agents, or AI
- Atlas Resource creation, modification, relationships, or classifications

Navigation behavior belongs exclusively to ENG-048.

# 4. Architectural Principle

The Camera is spatial presentation state.

```text
Engineering truth
    AtlasProject / AtlasResource / AtlasRelationship

Application behavior
    AtlasApplication

3D presentation state
    AtlasScene / AtlasCamera
```

The Camera may be consumed by a renderer, but it must not depend on one.

# 5. Camera Identity

Every Camera has:

```text
camera_id: str
name: str
```

Both values must be strings that are neither empty nor whitespace-only.
`camera_id` is immutable, unique within a future owning UI context, and is
not an `AtlasID` or engineering identity.

# 6. Exact State Contract

`AtlasCamera` exposes:

```text
camera_id: str
name: str
position: tuple[float, float, float]
target: tuple[float, float, float]
up: tuple[float, float, float]
projection: str
field_of_view_degrees: float
orthographic_scale: float
near_clip: float
far_clip: float
```

Defaults are:

```text
position              = (0.0, 0.0, 10.0)
target                = (0.0, 0.0, 0.0)
up                    = (0.0, 1.0, 0.0)
projection            = "perspective"
field_of_view_degrees = 60.0
orthographic_scale    = 10.0
near_clip             = 0.1
far_clip              = 10000.0
```

# 7. Validation

Position, target, and up must each contain exactly three numeric values.
Booleans are not numeric values for this contract.

The projection must be exactly one of:

```text
"perspective"
"orthographic"
```

`field_of_view_degrees` must be numeric and strictly greater than `0.0` and
strictly less than `180.0`.

`orthographic_scale`, `near_clip`, and `far_clip` must be numeric and
strictly greater than `0.0`. `far_clip` must be greater than `near_clip`.

Invalid types raise `TypeError`; invalid values raise `ValueError`.

# 8. Exact Public API

```text
AtlasCamera(
    *,
    camera_id: str,
    name: str,
    position: tuple[float, float, float] = (0.0, 0.0, 10.0),
    target: tuple[float, float, float] = (0.0, 0.0, 0.0),
    up: tuple[float, float, float] = (0.0, 1.0, 0.0),
    projection: str = "perspective",
    field_of_view_degrees: float = 60.0,
    orthographic_scale: float = 10.0,
    near_clip: float = 0.1,
    far_clip: float = 10000.0,
)

set_position(position)
set_target(target)
set_up(up)
set_projection(projection)
set_field_of_view_degrees(value)
set_orthographic_scale(value)
set_clipping_planes(near_clip, far_clip)
```

Direct setters change only Camera presentation state. They do not define
navigation interaction or user-input semantics.

# 9. Scene, Workspace, and Panel Boundary

An `AtlasCamera` can be constructed without an `AtlasScene`, `AtlasWorkspace`,
Panel, renderer, or navigation component. ENG-047 does not make the Scene a
Camera owner and does not introduce an `AtlasCameraRegistry`.

Future hosting and active-camera orchestration may be added when a concrete UI
need exists, without changing the canonical engineering model.

# 10. Engineering-State Isolation

Camera operations must not create, delete, or mutate:

```text
AtlasProject
AtlasResource
AtlasRelationship
AtlasResourceRegistry
Atlas Classification hierarchy
```

`AtlasCamera` must not inherit from `AtlasResource` and must not store copied
Resources, engineering relationships, classifications, or project state.

# 11. Renderer Independence

The Camera must not own renderer, engine, mesh, matrix, GPU, or framework
objects. Coordinate-system details and projection-matrix production belong to
the rendering/frontend boundary.

# 12. Acceptance Criteria

ENG-047 is complete when:

- `AtlasCamera` exists and is publicly exported.
- Its state and defaults match this contract.
- All validation and clipping-plane rules are enforced.
- Perspective and orthographic projection are supported as state.
- Camera state is independent of Scene, Workspace, Panel, renderer, and
  navigation.
- Camera operations preserve Atlas engineering state.
- Focused Camera tests and the full Atlas regression suite pass.

# 13. Phase 10 Relationship

```text
ENG-046 Scene
    ↓
ENG-047 Camera
    ↓
ENG-048 Navigation
    ↓
ENG-049 Selection
    ↓
ENG-050 Gizmos
    ↓
ENG-051 Basic Editing
```

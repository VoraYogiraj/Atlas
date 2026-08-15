# ENG-046 — Atlas Scene

**Document ID:** ENG-046  
**Title:** Atlas Scene  
**Version:** 0.2.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-045 — Atlas Panels  
**Phase:** Phase 10 — 3D Workspace  
**Implementation:** Atlas Application / 3D Workspace layer

---

# 1. Purpose

ENG-046 defines the first 3D Workspace foundation for Atlas: the Scene.

The Scene is the spatial presentation structure through which Atlas engineering
Resources may eventually be visualized in three dimensions.

The Scene is a visualization/application construct.

It is not a replacement for the canonical Atlas engineering model.

The Scene provides:

```text
Scene Identity
    ↓
Scene Nodes
    ↓
Spatial Hierarchy
    ↓
Transforms
    ↓
Visibility
    ↓
Selection Readiness

while preserving the canonical engineering model:
AtlasProject
    ↓
Resources
    ↓
Relationships
    ↓
Classifications
2. Architectural Principle
The fundamental separation is:
Atlas Engineering Truth
        ↓
AtlasProject / AtlasResource / AtlasRelationship

Application Behavior
        ↓
AtlasApplication

UI Workspace State
        ↓
AtlasWorkspace

3D Presentation State
        ↓
AtlasScene / AtlasSceneNode
The Scene visualizes Atlas engineering information.
It does not redefine engineering information.
3. Scope
ENG-046 defines:
Scene identity
Scene lifecycle
Scene name
Scene nodes
Node identity
Resource-to-node identity mapping
Node hierarchy
Root nodes
Parent validation
Cycle prevention
Node lookup
Deterministic node ordering
Spatial transforms
Visibility
Scene selection state
Loading state
Error state
Empty Scene state
Workspace relationship
Panel hosting compatibility
Application boundary
Engineering-state isolation
3D boundary
4. Non-Goals
ENG-046 does not implement:
Camera
Camera controls
Orbit
Pan
Zoom
Fly navigation
Mouse picking
Ray casting
Hit testing
Selection highlighting
Multi-selection behavior
Gizmos
Translation editing
Rotation editing
Scale editing
Geometry generation
Mesh generation
Rendering engine
WebGL
WebGPU
Three.js
Babylon.js
GPU management
Physics
Collision detection
Animation
Persistence
Scene serialization
Import
Export
Agent execution
AI-generated geometry
Scene-specific engineering validation
A second Atlas Resource Registry
A second Atlas Resource Graph
A second Atlas Classification hierarchy
These are either later Phase 10 capabilities or separate architectural
boundaries.
5. Scene Identity
Every Scene has a stable application-level identity.
The exact contract is:
scene_id: str
Rules:
scene_id must be a string.
scene_id must not be empty.
scene_id must not consist only of whitespace.
scene_id is immutable after construction.
scene_id is not an AtlasID.
scene_id is not a Resource identity.
scene_id uniquely identifies the Scene within its owning application
context.
Example:
main
or:
building-view
Scene IDs are presentation/application identities.
6. Scene Name
Every Scene has a presentation name:
name: str
Rules:
Must be a string.
Must not be empty.
Must not consist only of whitespace.
The name is presentation metadata.
7. Exact Scene Lifecycle
Scene lifecycle is separate from Atlas Resource lifecycle.
ENG-046 defines the following exact states:
created
initialized
active
inactive
disposed
Valid transitions:
created
   ↓
initialized
   ↓
active
   ↓
inactive
   ↓
active
Disposal transitions:
created       → disposed
initialized   → disposed
inactive      → disposed
disposed is terminal.
Invalid lifecycle transitions raise RuntimeError.
The Scene lifecycle must not use AtlasLifecycle.
8. Scene Construction
A Scene may be constructed independently of:
AtlasPanel
Renderer
Camera
Navigation system
Gizmo system
Selection interaction system
A Scene does not require a rendering framework.
The Scene is therefore independently testable.
9. Exact Scene State Contract
The Scene must expose the following state:
scene_id: str
name: str
lifecycle: str
is_loading: bool
error: str | None
selected_node_id: str | None
Defaults:
lifecycle       = "created"
is_loading      = False
error           = None
selected_node_id = None
10. Scene Nodes
A Scene contains zero or more AtlasSceneNode objects.
A Scene Node is a spatial presentation object.
It is not an AtlasResource.
The minimum required node contract is:
node_id: str
resource_id: AtlasID | None
parent_node_id: str | None
name: str
position: tuple[float, float, float]
rotation: tuple[float, float, float]
scale: tuple[float, float, float]
visible: bool
order: int
11. Node Identity
node_id is the identity of a Scene Node.
Rules:
node_id must be a string.
node_id must not be empty.
node_id must not consist only of whitespace.
node_id is unique within a Scene.
node_id is distinct from AtlasID.
node_id identifies the Scene presentation object, not the engineering
Resource.
Example:
node-001
12. Resource-to-Node Identity Mapping
A Scene Node may reference an Atlas Resource through:
resource_id: AtlasID | None
This is an identity reference only.
A Scene Node must not contain a copied AtlasResource.
The canonical relationship is:
SceneNode
    ↓
AtlasID
    ↓
AtlasProject
    ↓
AtlasResource
ENG-046 does not require the referenced Resource to currently exist when the
Scene Node is created.
Resource resolution remains an Application-boundary responsibility.
13. Multiple Scene Nodes per Resource
There is no uniqueness constraint on resource_id.
Therefore this is valid:
Scene Node A
    ↓
Resource X

Scene Node B
    ↓
Resource X
The uniqueness constraint applies only to:
node_id
This allows future spatial presentation patterns where a Resource may appear
in multiple scene locations.
14. Node Name
Every Scene Node has:
name: str
Rules:
Must be a string.
Must not be empty.
Must not consist only of whitespace.
The name is presentation metadata.
15. Node Parent
Every Scene Node has:
parent_node_id: str | None
Rules:
None
    ↓
Root Node
or:
"parent-node-id"
    ↓
Child Node
The parent must belong to the same Scene.
16. Root Nodes
A node is a root node when:
parent_node_id is None
The Scene exposes:
scene.root_nodes
as:
tuple[AtlasSceneNode, ...]
Root Nodes are deterministically ordered by:
(order, node_id)
17. Scene Node Collections
The Scene exposes:
scene.nodes
as:
tuple[AtlasSceneNode, ...]
All Scene Node collections are deterministically ordered by:
(order, node_id)
This applies to:
scene.nodes
scene.root_nodes
and any equivalent child-node presentation collection introduced later.
18. Node Lookup
The Scene provides:
scene.get_node(node_id)
Behavior:
Existing ID
    ↓
AtlasSceneNode

Unknown ID
    ↓
KeyError
The lookup method must reject non-string IDs with:
TypeError
19. Node Registration
The Scene provides:
scene.add_node(node)
Rules:
node must be an AtlasSceneNode.
Duplicate node_id raises ValueError.
If parent_node_id is not None, the parent must already exist in the
Scene.
Invalid parent references raise ValueError.
Adding a node must not mutate the Atlas Project.
Adding a node must not create an AtlasRelationship.
20. Node Removal
The Scene provides:
scene.remove_node(node_id)
Rules:
Unknown node IDs raise KeyError.
Removing a node removes the Scene presentation object.
Removing a node must not remove or modify an Atlas Resource.
Removing a node must not remove or modify an Atlas Relationship.
If the node has children, ENG-046 does not permit silent orphaning.
The implementation must either:
reject removal while children exist with ValueError, or
explicitly remove/reparent children through a defined contract.
For ENG-046, the required behavior is:
node with children
    ↓
ValueError
This keeps hierarchy mutations deterministic and conservative.
21. Parent Mutation
The Scene provides:
scene.set_parent(
    node_id,
    parent_node_id,
)
Rules:
Clearing Parent
parent_node_id = None
makes the node a root node.
Existing Parent
The parent must exist in the Scene.
Unknown Node
Unknown node_id raises:
KeyError
Unknown Parent
Unknown parent_node_id raises:
KeyError
Self-Parenting
A node cannot be its own parent.
This raises:
ValueError
Cycles
Any operation that creates a cycle raises:
ValueError
22. Scene Hierarchy
Scene hierarchy is presentation structure.
Example:
Scene
└── Building
    ├── Floor 1
    │   ├── Wall
    │   └── Door
    └── Floor 2
Hierarchy does not automatically imply engineering relationships.
23. Engineering Relationships vs Scene Hierarchy
This distinction is mandatory.
Atlas Relationship:
AtlasResource
    ↓
AtlasRelationship
    ↓
AtlasResource
Scene hierarchy:
AtlasSceneNode
    ↓
parent_node_id
    ↓
AtlasSceneNode
The following operations must never automatically create or destroy
AtlasRelationship objects:
add_node
remove_node
set_parent
Scene hierarchy is not the canonical engineering graph.
24. Cycle Prevention
The Scene hierarchy must remain acyclic.
Invalid:
A → B
B → C
C → A
The Scene must reject operations producing such a state.
Cycle validation occurs before committing the parent mutation.
25. Transform Representation
Each Scene Node stores:
position: tuple[float, float, float]
rotation: tuple[float, float, float]
scale: tuple[float, float, float]
Defaults:
position = (0.0, 0.0, 0.0)
rotation = (0.0, 0.0, 0.0)
scale = (1.0, 1.0, 1.0)
Each tuple must contain exactly three numeric values.
ENG-046 does not specify:
degrees vs radians
Euler vs quaternion
renderer coordinate systems
world vs local matrices
Those concerns remain outside this milestone.
26. Transform Ownership
Transform values belong to Scene presentation state.
They are not automatically authoritative engineering dimensions.
Therefore:
SceneNode.position
SceneNode.rotation
SceneNode.scale
must not automatically mutate:
AtlasResource
AtlasProject
AtlasRelationship
27. Transform Editing Boundary
ENG-046 stores transform state.
ENG-046 does not define interactive transform mutation operations such as:
translate_node()
rotate_node()
scale_node()
Interactive editing belongs to ENG-051 — Basic Editing.
Construction-time transform values are permitted.
28. Visibility
Every Scene Node has:
visible: bool
Default:
True
Visibility is presentation state.
Visibility changes must not mutate:
Resource existence
Resource properties
Resource lifecycle
Relationships
Classifications
Project state
29. Node Order
Every Scene Node has:
order: int
Default:
0
Ordering is presentation state.
Node collections are sorted deterministically by:
(order, node_id)
30. Scene Selection State
ENG-046 provides selection state storage for future ENG-049.
The Scene exposes:
selected_node_id: str | None
Default:
None
The Scene provides:
scene.set_selected_node(node_id)
where:
node_id
    = existing Scene Node ID

None
    = clear selection
Unknown node IDs raise:
KeyError
ENG-046 does not implement:
mouse picking
ray casting
hit testing
selection highlighting
multi-selection
selection interaction
Those belong to ENG-049.
31. Selection Identity
Scene selection is based on:
Scene Node ID
The Scene must not store an entire AtlasResource as selection state.
An application may resolve the node's resource_id through the canonical
Application boundary.
32. Loading State
The Scene exposes:
is_loading: bool
Default:
False
The Scene provides:
scene.set_loading(bool)
Loading state is transient presentation/application state.
It must not be stored in Atlas engineering state.
33. Error State
The Scene exposes:
error: str | None
Default:
None
The Scene provides:
scene.set_error(message | None)
Rules:
None clears the error.
Non-empty strings represent an application/presentation error.
Empty or whitespace-only error messages are invalid.
Error state is not engineering state.
34. Empty Scene
An empty Scene is valid.
Therefore:
scene.nodes == ()
is a valid state.
An empty Scene is not automatically an error.
35. Scene and AtlasWorkspace
ENG-046 does not make AtlasWorkspace a 3D engine.
A Scene may exist independently.
The generic Workspace continues to own:
application boundary
panel registry
view registry
UI lifecycle
selection context
ENG-046 does not require a second Workspace.
Future 3D Workspace orchestration may be introduced without changing the
canonical Atlas engineering model.
36. Scene and Panels
A Scene may be hosted by an Atlas Panel.
Conceptually:
AtlasWorkspace
    ↓
AtlasPanel
    ↓
AtlasScene
However:
AtlasScene
must not require:
AtlasPanel
in its constructor.
The Scene remains independently reusable and testable.
37. Scene and Explorer
Explorer may identify Resources represented in a Scene.
The relationship is identity-based:
Explorer
    ↓
AtlasID
    ↓
AtlasSceneNode
The Scene must not duplicate Explorer's project navigation model.
38. Scene and Inspector
Inspector may resolve canonical Resource information from a Scene Node:
SceneNode
    ↓
AtlasID
    ↓
AtlasApplication
    ↓
AtlasResource
    ↓
Inspector
The Scene does not duplicate Inspector presentation state.
39. Scene and Application Boundary
The Scene does not bypass the AtlasApplication boundary when obtaining or
mutating engineering information.
The Scene may contain:
AtlasID
references.
Resolution of engineering entities remains an application concern.
40. Engineering-State Isolation
Scene operations must not directly mutate:
AtlasProject
AtlasResourceRegistry
AtlasResourceGraph
AtlasRelationship
AtlasClassification
except through explicit future Application-level behavior.
The following Scene operations are strictly presentation operations:
add_node
remove_node
set_parent
set_selected_node
set_loading
set_error
visibility changes
41. No Second Resource Registry
The following architecture is prohibited:
AtlasProject
    ↓
Resource Registry

AtlasScene
    ↓
Scene Resource Registry
Scene Nodes contain identity references only.
42. No Second Engineering Graph
The Scene hierarchy is not a second Atlas Relationship Graph.
The following is prohibited:
AtlasProject Graph
        +
Scene Graph pretending to be engineering truth
A Scene hierarchy exists only for spatial presentation.
43. No Second Classification Hierarchy
Scene organization must not create a competing engineering classification
system.
Visual grouping may exist later as a presentation feature, but it must not
become canonical classification.
44. Rendering Framework Independence
ENG-046 does not select a rendering framework.
A Scene must be constructible without requiring:
Three.js
Babylon.js
WebGL
WebGPU
OpenGL
DirectX
Metal
Vulkan
Renderer integration belongs to the application/frontend implementation
boundary.
45. Camera Boundary
Camera functionality belongs exclusively to ENG-047.
ENG-046 does not define or own:
camera position
camera orientation
projection
field of view
camera controls
The Scene must not require a Camera to exist.
46. Navigation Boundary
Navigation belongs exclusively to ENG-048.
ENG-046 does not implement:
orbit
pan
zoom
fly
walk
navigation state
47. Selection Interaction Boundary
Selection interaction belongs exclusively to ENG-049.
ENG-046 provides only selection state storage.
48. Gizmo Boundary
Gizmos belong exclusively to ENG-050.
ENG-046 does not implement:
move gizmo
rotate gizmo
scale gizmo
interactive handles
49. Editing Boundary
Basic engineering editing belongs exclusively to ENG-051.
Scene presentation state must not silently become engineering mutation.
50. Persistence Boundary
ENG-046 does not implement:
Scene serialization
Scene save
Scene load
Project persistence
UI persistence
Persistence remains governed by the existing application architecture.
51. Exchange Boundary
ENG-046 does not implement:
IFC
CAD
Revit
OBJ
FBX
glTF
Other external exchange formats
52. Agent Boundary
ENG-046 does not execute Agents.
Future Agent-driven Scene commands must cross the existing application/agent
boundaries.
53. AI Boundary
AI may eventually request presentation changes such as:
Show structural elements.
Focus on Floor 3.
Hide finishes.
Such behavior must resolve through application-level commands.
AI does not become the source of engineering truth.
54. Scene Registry Decision
ENG-046 does not introduce an AtlasSceneRegistry.
The milestone focuses on proving the Scene model first.
Multi-Scene registration and active Scene orchestration may be introduced by a
future 3D Workspace milestone when required.
This avoids expanding the generic UI Workspace with premature 3D-specific
registry infrastructure.
55. Exact Public API Contract
AtlasScene
Required state:
scene_id: str
name: str
lifecycle: str
is_loading: bool
error: str | None
selected_node_id: str | None
Required operations:
add_node(node)
remove_node(node_id)
get_node(node_id)
set_parent(node_id, parent_node_id)
set_selected_node(node_id | None)
set_loading(bool)
set_error(str | None)
Required views:
nodes -> tuple[AtlasSceneNode, ...]
root_nodes -> tuple[AtlasSceneNode, ...]
56. Exact AtlasSceneNode Contract
Required state:
node_id: str
resource_id: AtlasID | None
parent_node_id: str | None
name: str
position: tuple[float, float, float]
rotation: tuple[float, float, float]
scale: tuple[float, float, float]
visible: bool
order: int
Defaults:
position = (0.0, 0.0, 0.0)
rotation = (0.0, 0.0, 0.0)
scale = (1.0, 1.0, 1.0)
visible = True
order = 0
Validation:
node_id
    non-empty string

resource_id
    AtlasID or None

parent_node_id
    string or None

name
    non-empty string

position
    exactly 3 numeric values

rotation
    exactly 3 numeric values

scale
    exactly 3 numeric values

visible
    boolean

order
    integer
57. Exact Collection Contract
scene.nodes
    ↓
tuple[AtlasSceneNode, ...]

scene.root_nodes
    ↓
tuple[AtlasSceneNode, ...]
Both collections use:
(order, node_id)
as their deterministic ordering key.
58. Exact Error Contract
Invalid type
    ↓
TypeError

Invalid construction/state value
    ↓
ValueError

Unknown Scene Node ID
    ↓
KeyError

Invalid lifecycle transition
    ↓
RuntimeError
59. Testing Strategy
ENG-046 tests must verify:
Scene type
Scene identity
Scene name
Scene lifecycle
Lifecycle transitions
Scene node type
Node identity
Resource identity mapping
Multiple nodes for one Resource
Hierarchy
Root nodes
Parent validation
Self-parent rejection
Cycle rejection
Node lookup
Duplicate node rejection
Node removal
Child-removal rejection
Node ordering
Transforms
Transform defaults
Visibility
Selection state
Loading state
Error state
Empty Scene
Panel compatibility
Explorer identity boundary
Inspector identity boundary
Engineering-state isolation
No second Resource Registry
No second Graph
No second Classification hierarchy
No renderer dependency
No Camera dependency
No Navigation implementation
No Selection interaction implementation
No Gizmo implementation
No Editing implementation
Persistence isolation
Exchange isolation
Agent isolation
AI boundary
Public exports
Deterministic behavior
Visual rendering tests belong to future rendering/frontend implementation.
60. Acceptance Criteria
ENG-046 is complete when:
AtlasScene exists.
AtlasSceneNode exists.
Scene identity is stable and validated.
Scene name is validated.
Scene lifecycle follows the exact ENG-046 state machine.
Scene lifecycle remains separate from Atlas Resource lifecycle.
Scene Nodes have unique IDs within a Scene.
Scene Nodes may reference canonical Resources by AtlasID.
Scene Nodes do not copy AtlasResource objects.
Multiple Scene Nodes may reference the same AtlasID.
Scene hierarchy is supported.
Parent references are validated.
Self-parenting is rejected.
Cyclic hierarchy is rejected.
Root nodes are supported.
Node lookup is deterministic.
Duplicate node IDs are rejected.
Node removal is validated.
Nodes with children cannot be silently orphaned.
Node ordering is deterministic.
Transform defaults are defined.
Transform state is presentation state.
Visibility is supported.
Scene selection state is supported.
Scene selection remains separate from ENG-049 interaction.
Empty Scene state is valid.
Loading state is supported.
Error state is supported.
Scene can exist without a Panel.
Scene can be hosted by a Panel.
Scene does not create a second Resource Registry.
Scene does not create a second engineering Graph.
Scene does not create a second Classification hierarchy.
Scene remains renderer-independent.
Scene does not implement Camera.
Scene does not implement Navigation.
Scene does not implement Selection interaction.
Scene does not implement Gizmos.
Scene does not implement Engineering Editing.
Scene does not implement Persistence.
Scene does not implement Exchange.
Scene does not execute Agents.
Scene does not treat AI as engineering truth.
Existing Atlas Core behavior remains unchanged.
61. Phase 10 Relationship
ENG-046 establishes:
Scene
ENG-047 establishes:
Camera
ENG-048 establishes:
Navigation
ENG-049 establishes:
Selection
ENG-050 establishes:
Gizmos
ENG-051 establishes:
Basic Editing
The progression is:
ENG-046
Scene
    ↓
ENG-047
Camera
    ↓
ENG-048
Navigation
    ↓
ENG-049
Selection
    ↓
ENG-050
Gizmos
    ↓
ENG-051
Basic Editing
Each milestone adds one capability while preserving the separation between
visualization and engineering truth.
62. Architectural Conclusion
ENG-046 establishes the Atlas Scene as the first 3D Workspace capability.
The Scene provides spatial presentation structure while preserving:
Canonical Engineering Knowledge
        ↓
AtlasProject / AtlasResource / AtlasRelationship

Application Behavior
        ↓
AtlasApplication

UI Workspace
        ↓
AtlasWorkspace

3D Presentation
        ↓
AtlasScene / AtlasSceneNode
The Scene is therefore a deterministic visualization layer over the canonical
Atlas engineering model.
It is not a competing engineering model.
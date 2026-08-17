ENG-052 — Atlas Resource Create
Status: Proposed / RED
Phase: Phase 11 — Resource Editing
Depends On: ENG-001 through existing Resource foundation, ENG-010 Registry, ENG-039 Application Boundary, ENG-040/045 Workspace/UI, Phase 10 completion
Previous: ENG-051 — Atlas Basic Editing
Next: TBD
1. Purpose
ENG-052 introduces the first canonical Resource Editing capability:
Create an Atlas Resource through the application boundary.

Unlike ENG-051, which modifies AtlasSceneNode presentation state, ENG-052 operates on the canonical engineering model.
The distinction is fundamental:
ENG-051

Gizmo
  ↓
Basic Editing
  ↓
SceneNode transformation
versus:
ENG-052

Application Command
  ↓
Canonical AtlasProject
  ↓
Resource creation
  ↓
Resource Registry
The existing architecture explicitly states that AtlasApplication is a thin boundary over the canonical AtlasProject and must not become a second engineering model. 
2. Architectural Position
Phase 11 begins the transition from presentation editing to engineering-state editing.
Atlas Core
    │
    │ canonical engineering state
    ↓
AtlasProject
    │
    ↓
AtlasApplication
    │
    ↓
AtlasCommand
    │
    ↓
ENG-052 Resource Create
    │
    ├── Resource
    └── Registry
The Workspace remains above the application boundary.
The Workspace must not become the owner of Resources or Resource registries; its existing contract explicitly restricts it to presentation/application state. 
3. Core Principle
Resource creation belongs to the canonical engineering layer, not the 3D workspace.
ENG-052 must not create a Resource merely because a SceneNode exists.
The canonical Resource is authoritative.
A future presentation layer may subsequently represent that Resource through one or more SceneNodes, but that mapping is a separate concern.
4. Proposed Capability
ENG-052 introduces the ability to request creation of a Resource with the minimum information required by the existing Resource model.
The exact Resource constructor/schema must be taken from the existing canonical Resource implementation rather than invented by ENG-052.
Therefore:
ENG-052 must adapt to the existing Resource contract. It must not redefine the Resource model.

5. Application Boundary
Resource creation must pass through the existing application boundary.
Conceptually:
UI / Agent / API / Future Input
             │
             ↓
       AtlasCommand
             │
             ↓
      AtlasApplication
             │
             ↓
        AtlasProject
             │
             ↓
       Resource Registry
The existing AtlasApplication.execute() already establishes the intended command boundary and currently rejects commands that have no implemented handler. 
ENG-052 introduces the first real domain-specific command handler.
6. Command
The command should use the existing AtlasCommand mechanism.
Candidate command name:
create_resource
Candidate conceptual payload:
{
    ...existing Resource creation fields...
}
Important: ENG-052 must not invent a parallel command object if AtlasCommand is already the canonical application command abstraction.
The existing application architecture deliberately provides a generic command boundary for later domain-specific handlers. 
7. Identity
Resource creation must preserve the existing Atlas identity model.
The new Resource receives its canonical AtlasID according to the existing Resource/identity rules.
ENG-052 must not:
use SceneNode.node_id as Resource identity
use Workspace identity as Resource identity
use an external identifier as canonical identity
create a second Resource identity system
ENG-050 already established the distinction between viewport node_id and canonical engineering AtlasID. 
That distinction must continue into Phase 11.
8. Registry
A successfully created Resource must become discoverable through the existing canonical Resource Registry.
Conceptually:
Create Resource
      ↓
Canonical Resource exists
      ↓
Registry contains Resource
      ↓
Resource can be retrieved by AtlasID
The application presentation layer already expects Resource lookup to remain owned by the canonical Resource Registry. application.pyPY
ENG-052 must not introduce:
SceneResourceRegistry
WorkspaceResourceRegistry
UIResourceRegistry
or any equivalent duplicate registry.
9. Atomicity
Creation must be atomic.
If validation fails:
BEFORE
Registry = R

CREATE INVALID RESOURCE
        ↓
        ERROR

AFTER
Registry = R
There must be no:
partially registered Resource
orphan identity
partially initialized Resource
corrupted registry state
This continues the atomic-validation principle already established in Phase 10, where validation is required before mutation. 
10. Validation
ENG-052 must use the existing canonical Resource validation rules.
It must not create a second set of Resource validation rules inside the application/UI layer.
Validation should occur before canonical mutation.
Conceptually:
Input
 ↓
Type / shape validation
 ↓
Existing Resource validation
 ↓
Registry mutation
The precise validation requirements must come from the existing Resource foundation.
11. Determinism
Given the same canonical initial state and equivalent creation command, ENG-052 must produce equivalent canonical results.
No:
renderer state
UI state
timing
random presentation state
external state
may influence the engineering result unless explicitly part of the established Resource identity mechanism.
This extends the deterministic behavior already required by Phase 10 components. ENG-050 explicitly requires identical operation sequences to produce identical observable state. 
12. Resource / Scene Separation
ENG-052 must not automatically expand into 3D editing.
This is critical.
Creating:
AtlasResource
does not automatically mean ENG-052 must implement:
AtlasSceneNode
unless the existing Atlas architecture explicitly requires that mapping.
The current architecture distinguishes canonical engineering identity (AtlasID) from viewport identity (node_id). 
Therefore, the first RED contract should test the canonical Resource creation behavior independently.
13. Selection
ENG-052 must not redefine selection.
Existing Workspace selection stores canonical AtlasID, rather than owning a Resource object. workspace.pyPY
Whether newly created Resources become selected automatically is not established by the retrieved source.
Therefore:
Do not silently add auto-selection to ENG-052.

If we later want that behavior, it should be explicitly specified as a separate application interaction contract.
14. UI Independence
ENG-052 must not require the UI to create a Resource.
The Resource creation capability should be callable without:
Workspace
Panel
View
Scene
Camera
Gizmo
renderer
This preserves the architecture where the application layer is usable independently of the presentation layer.
15. Agent / AI Independence
ENG-052 must not depend on:
Agent Runtime
Orchestrator
LLM
AI
external model
autonomous agent
An agent may eventually issue the same command, but the canonical Resource creation mechanism remains deterministic.
This preserves the existing principle that application interaction must not allow AI/viewport concerns to become the engineering model. ENG-050 explicitly isolates AI/agents from its manipulation state. ENG-050-Atlas-Gizmo.mdMD
16. Persistence
ENG-052 should not introduce a new persistence mechanism.
If the canonical project already supports persistence, the newly created Resource should naturally participate through the existing project serialization/persistence mechanisms.
But ENG-052 itself should not redesign:
serialization
save/load
import/export
schema versioning
Those are existing/future boundaries.
17. Error Semantics
For RED, we should test that invalid creation requests fail without changing canonical state.
The exact exception taxonomy should follow the existing Atlas Resource/application conventions.
We should not invent a new ResourceCreationError unless the existing architecture requires it.
18. Public API
At minimum, ENG-052 should expose its functionality through the existing application command mechanism.
We should not immediately create multiple parallel APIs such as:
application.create_resource()
project.create_resource()
workspace.create_resource()
ui.create_resource()
unless the existing canonical architecture demonstrates that such APIs are required.
The primary contract should be:
AtlasCommand
    ↓
AtlasApplication.execute()
19. RED Test Categories
The initial ENG-052 test suite should cover:
Construction / command
valid AtlasCommand
correct command name
payload handling
Successful creation
Resource is created
Resource receives canonical identity
Resource becomes available through canonical project/registry
returned result is deterministic
Required Resource fields
valid minimum Resource creation
invalid required values
invalid types
invalid combinations
Atomicity
invalid creation leaves project unchanged
registry unchanged after failure
no partially created Resource
Identity
created Resource has valid AtlasID
identity is unique according to existing identity rules
identity is not a SceneNode ID
Registry
Resource is retrievable after creation
registry contains exactly the expected Resource
no duplicate registration
Architecture
no Workspace dependency
no Scene dependency
no Camera dependency
no Gizmo dependency
no renderer dependency
no AI/Agent dependency
Determinism
equivalent initial state + equivalent command → equivalent result
Regression
all existing ENG-001 through ENG-051 tests remain untouched
full suite remains green after implementation
20. Explicit Non-Goals
ENG-052 does not implement:
Move
Rotate
Scale
Delete
Duplicate
SceneNode creation unless already required by an established canonical mapping
Gizmo interaction
Selection behavior
Picking
Rendering
Three.js
UI widgets
Undo/redo
transactions beyond the atomicity requirement
collaboration
revision history
provenance system
import/export
IFC/DWG/Revit
AI
agents
autonomous creation
constraint solving
parametric modeling
new Resource architecture
These belong to later milestones or existing/future architectural layers.
21. Implementation Constraints
Implementation must:
Preserve all existing Resource APIs.
Preserve all existing Registry behavior.
Preserve all existing Project behavior.
Preserve all existing application APIs.
Use the existing AtlasCommand.
Use the existing canonical AtlasProject.
Avoid a second engineering model.
Validate before mutation.
Maintain atomic failure.
Maintain deterministic behavior.
Introduce only Resource Create responsibility.
Avoid unrelated refactoring.
22. Expected RED State
Before implementation:
ENG-052 tests
      ↓
EXPECTED FAILURE
      ↓
create_resource handler/API does not yet exist
Existing ENG-001 through ENG-051 tests must remain untouched.
The RED phase should prove that the tests actually constrain the intended behavior rather than simply testing an already-existing implementation.
23. Completion Criteria
ENG-052 is complete when:
Resource Create contract is implemented.
Creation goes through the established application boundary.
Canonical AtlasProject remains authoritative.
Resource receives valid canonical identity.
Resource enters the existing Registry correctly.
Existing Resource validation is respected.
Invalid creation is rejected atomically.
No partial canonical state remains after failure.
Creation is deterministic.
No duplicate Resource model is introduced.
No Scene/Workspace dependency is introduced unnecessarily.
No renderer dependency exists.
No AI/Agent dependency exists.
Focused ENG-052 tests pass.
Full regression passes.
Public API is exported only where appropriate.
ENG-052 is checkpointed.
24. Architectural Result
After ENG-052:
                 Atlas Application
                       │
                       │ AtlasCommand
                       ↓
              Resource Create
                       │
                       ↓
                AtlasProject
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        AtlasResource       Resource Registry
             │
             ↓
       Canonical State
The 3D workspace remains separate:
                 3D Workspace
                      │
          Scene / Selection / Gizmo
                      │
                 SceneNode
                      │
              resource_id
                      │
                      ↓
             Canonical Resource
This is exactly the separation we want going into Phase 11: canonical engineering state becomes editable without allowing the presentation layer to become the engineering model.
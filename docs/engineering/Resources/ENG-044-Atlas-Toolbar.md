# ENG-044 — Atlas Toolbar

**Document ID:** ENG-044  
**Title:** Atlas Toolbar  
**Version:** 0.1.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-041 — Atlas Dashboard, ENG-042 — Atlas Explorer, ENG-043 — Atlas Inspector  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas Application / Presentation layer

---

# Purpose

ENG-044 defines the Atlas Toolbar as the primary command presentation surface
for the Atlas user interface.

The Toolbar presents available application commands to the user and delegates
their execution through the existing Atlas Application command boundary.

The Toolbar is not a second command engine.

It does not own engineering state.

It does not directly mutate Atlas Core.

---

# Scope

ENG-044 defines:

- Toolbar identity
- Toolbar presentation model
- Toolbar item representation
- Command identity
- Command registration
- Command grouping
- Command ordering
- Enabled / disabled state
- Command visibility
- Command execution delegation
- Selection-aware command state
- Workspace integration
- Dashboard navigation commands
- Explorer commands
- Inspector navigation
- Refresh commands
- Application boundary
- Read-only presentation behavior
- Empty command state
- Error state
- Loading state
- Deterministic command ordering
- Technology-independent behavior

---

# Non-Goals

ENG-044 does not implement:

- A second command system
- Direct Resource mutation
- Resource creation
- Resource editing
- Resource deletion
- Direct Graph mutation
- Direct Classification mutation
- Validation rule editing
- Agent execution
- Persistence
- Save
- Load
- Import
- Export
- 3D rendering
- Camera control
- Gizmos
- Geometry editing
- Collaboration
- Frontend framework selection
- Visual styling system

The Toolbar is a command presentation and delegation surface.

---

# Architectural Position

The Toolbar operates above the ENG-039 Application Boundary and inside the
ENG-040 UI Application Shell.

The architectural flow is:

```text
Atlas Core
    ↓
Atlas Application
    ↓
AtlasCommand
    ↓
Toolbar Command Presentation
    ↓
Toolbar
    ↓
User Interaction
    ↓
AtlasApplication.execute(...)
    ↓
Application Command Handling

The Toolbar does not bypass the Application Boundary.

Toolbar Principle

The Toolbar answers:

"What actions are available here?"

The Dashboard answers:

"What is the state of this project?"

The Explorer answers:

"What exists inside this project?"

The Inspector answers:

"What is this selected Resource?"

The Toolbar provides the actions that allow the user to operate these
presentation surfaces.

Toolbar Identity

The Toolbar must have a stable UI/application identity.

Recommended identity:

toolbar

This identity is not an AtlasID.

It identifies the Toolbar presentation capability.

Existing Command Boundary

ENG-039 already establishes:

AtlasCommand

as the application command representation.

ENG-044 must reuse this command abstraction.

The Toolbar must not introduce:

ToolbarCommand

as an independent engineering command system.

A Toolbar item may wrap or reference an existing AtlasCommand, but command
semantics remain owned by the Application Boundary.

Command Principle

The architectural separation is:

Toolbar
    ↓
AtlasCommand
    ↓
AtlasApplication
    ↓
Atlas Core

The prohibited architecture is:

Toolbar
    ↓
AtlasResource mutation

The Toolbar presents commands.

The Application executes commands.

Atlas Core owns engineering state.

Toolbar Presentation Model

The Toolbar should use dedicated presentation representations.

Conceptually:

AtlasCommand
    ↓
Toolbar Item
    ↓
Toolbar Presentation

The presentation model must not become an Atlas Project, Resource, Graph,
Registry, or Agent model.

Toolbar Item

A Toolbar item should represent information necessary to present and invoke a
command.

Conceptually:

AtlasToolbarItem
├── command
├── label
├── group
├── order
├── enabled
├── visible
└── tooltip

Not every implementation field must be exposed publicly if an equivalent
representation is used.

Command Identity

Every Toolbar command must preserve the identity of the underlying
AtlasCommand.

The Toolbar must not generate a second engineering identity.

Command identity must remain stable for equivalent command definitions.

Command Label

A Toolbar item may expose a presentation label.

Example:

Refresh
Search
Filter
Expand All
Collapse All
Open Explorer
Open Inspector

The label is presentation metadata.

It is not the engineering command identity.

Command Grouping

Toolbar commands may be grouped into logical presentation groups.

Possible groups include:

Navigation
View
Explorer
Inspector
Project
Selection

Grouping is presentation state.

It must not alter command semantics.

Command Ordering

Toolbar ordering must be deterministic.

Equivalent command definitions must produce equivalent ordering.

The Toolbar must not rely on:

Hash ordering
Object identity
Memory address
Unstable discovery order

unless canonical deterministic ordering is guaranteed elsewhere.

Enabled State

A Toolbar item may be enabled or disabled based on application/UI context.

Examples:

Refresh
    enabled = True


Inspect Selected Resource
    enabled = False

when no Resource is selected.

Enabled state is transient presentation state.

It is not engineering state.

Visibility

A Toolbar item may be visible or hidden based on the current UI context.

Visibility is presentation state.

A hidden command does not cease to exist as an application capability.

Selection-Aware Commands

Toolbar command availability may depend on the current Workspace selection.

For example:

No Selection
    ↓
Inspect Resource = disabled
Resource Selected
    ↓
Inspect Resource = enabled

The Toolbar must consume identity-based selection state.

Resource selection must use AtlasID.

Selection Identity

The Toolbar must not store a copied Resource as command context.

Conceptually:

Workspace Selection
    ↓
AtlasID
    ↓
Command Context

Not:

Workspace Selection
    ↓
AtlasResource Copy
    ↓
Toolbar
Dashboard Commands

The Toolbar may expose navigation commands related to the Dashboard.

Examples:

Open Dashboard
Refresh Dashboard

The Dashboard remains responsible for project-level summary presentation.

Explorer Commands

ENG-044 may expose commands anticipated by ENG-042.

Examples:

Refresh Explorer
Search
Filter
Clear Filter
Expand All
Collapse All

The Explorer specification explicitly anticipates these Toolbar operations,
while keeping command execution in the application command layer.

Inspector Commands

The Toolbar may expose Resource-level actions related to the Inspector.

Examples:

Open Inspector
Refresh Inspector

A Resource-specific Inspector command may be disabled when no Resource is
selected.

Navigation Commands

The Toolbar may allow Workspace navigation among:

Dashboard
Explorer
Inspector
Future 3D View

Navigation remains an application/workspace concern.

The Toolbar must not own individual Views or Panels.

Workspace Integration

The Toolbar is hosted by the ENG-040 Workspace.

Conceptually:

AtlasWorkspace
    ↓
Toolbar
    ↓
Toolbar Presentation

The Workspace remains responsible for:

Workspace lifecycle
Panel registration
View registration
Active View
Selection context
Command routing context

The Toolbar does not become the Workspace.

Toolbar Registration

A Toolbar may receive commands through application-level registration.

The registration model should remain deterministic.

A Toolbar may internally maintain derived presentation state such as:

Registered Items
Visible Items
Enabled Items
Active Group

but this must not become a second command registry.

No Second Command System

The Toolbar must not create an independent command execution framework.

The following architecture is prohibited:

AtlasApplication
    ↓
AtlasCommand


Toolbar
    ↓
ToolbarCommand
    ↓
ToolbarCommandEngine

Instead:

AtlasApplication
    ↓
AtlasCommand
    ↑
Toolbar

The Toolbar presents existing application commands.

Command Execution

When a user activates a Toolbar item:

User
    ↓
Toolbar
    ↓
AtlasCommand
    ↓
AtlasApplication

The Toolbar delegates execution.

It must not contain engineering mutation logic.

Command Result

The Toolbar may receive an application command result.

Presentation state may then update based on that result.

For example:

Command
    ↓
Success
    ↓
Refresh Presentation

or:

Command
    ↓
Failure
    ↓
Toolbar Error State

The Toolbar must not reinterpret command results as independent engineering
truth.

Read-Only Presentation Boundary

The Toolbar itself is a presentation surface.

Displaying a command must not mutate Atlas state.

Examples:

Building Toolbar
Building command list
Refreshing Toolbar presentation
Enabling a command
Disabling a command
Showing a tooltip

must not modify engineering Resources.

Application Boundary

Toolbar execution must remain inside the ENG-039 Application Boundary.

Conceptually:

Toolbar
    ↓
AtlasCommand
    ↓
AtlasApplication

The Toolbar must not directly call:

AtlasResource.set_property()
AtlasProject.add_resource()
AtlasProject.remove_resource()
AtlasResourceGraph.add_relationship()

for command execution.

Those are domain/application responsibilities.

Command Context

A Toolbar may construct presentation/application context needed to determine
whether a command is enabled.

Examples:

Current View
Current Selection AtlasID
Current Workspace State

Command context is not engineering truth.

Empty Toolbar

The Toolbar must support a valid empty-command state.

Example:

No Actions Available

An empty Toolbar is valid UI state.

It must not be interpreted as an application failure.

Loading State

The Toolbar may expose a transient loading state.

Example:

Loading Actions...

Loading state belongs to the UI/application layer.

It must not be written into Atlas Core.

Error State

The Toolbar must distinguish command loading/registration failure from a valid
empty Toolbar.

Potential states include:

Loading
Empty
Ready
Command Error
Execution Error

An error must not silently become an empty command list when the system knows
that registration or execution failed.

Determinism

For equivalent Workspace and Application state, the Toolbar should produce
equivalent presentation.

This applies to:

Command set
Command ordering
Groups
Visibility
Enabled state

Determinism is important for:

Testing
UI consistency
Debugging
Reproducibility
Future caching
No Engineering State Ownership

The Toolbar must not own:

AtlasProject
AtlasResource
AtlasResourceRegistry
AtlasResourceGraph
AtlasClassificationRegistry
AtlasClassificationHierarchy
Validation Engine
Agent Runtime
Persistence Store

It may receive references to application-level presentation/query state where
explicitly required by the existing UI architecture.

No Second Registry

The Toolbar must not become:

ToolbarResourceRegistry

or any other engineering registry.

Command presentation state is not a Resource Registry.

No Second Graph

The Toolbar must not represent or own a second engineering graph.

Navigation commands may reference Resource identities, but graph ownership
remains with Atlas Project.

Agent Boundary

The Toolbar does not execute Agents directly.

Future commands may invoke Agent operations through the application command
boundary.

Conceptually:

Toolbar
    ↓
AtlasCommand
    ↓
Application / Agent Runtime

Agent execution remains owned by existing Agent architecture.

AI Boundary

Future AI capabilities may generate or recommend Toolbar actions.

Examples:

"Open all external walls"
"Find unclassified resources"
"Inspect Stair 01"

AI-generated actions must resolve to existing application commands and canonical
Atlas identities.

AI must not silently create engineering truth.

Persistence Boundary

The Toolbar does not implement:

JSON serialization
Save
Load
File persistence

Persistence remains governed by ENG-036 and ENG-037.

A Toolbar may expose commands such as:

Save
Load

in a future version, but the execution responsibility remains outside the
Toolbar.

Exchange Boundary

The Toolbar does not implement:

Import
Export
IFC processing
CAD processing
Revit processing

Those remain governed by ENG-038 and future exchange capabilities.

3D Boundary

The Toolbar may expose navigation or commands related to the future 3D
Workspace.

Examples:

Open 3D View
Frame Selection
Reset Camera

However, ENG-044 does not implement:

Scene
Camera
Navigation mechanics
Selection rendering
Gizmos
Geometry
3D editing

Those belong to Phase 10.

Panel Boundary

Toolbar commands may control the visibility or activation of future Panels.

The Toolbar does not become the Panel Registry.

Panel lifecycle remains an ENG-040 Workspace concern.

Technology Independence

ENG-044 must remain independent from:

React
Vue
Angular
Svelte
Next.js
Three.js
Babylon.js
Electron
Tauri
WebGL

The specification defines application behavior and architecture, not rendering
technology.

Large Project Compatibility

The Toolbar should remain lightweight even when the Atlas Project contains a
large number of Resources.

Toolbar command state should not require copying entire Resource collections.

Resource-related command availability should consume stable identity or
application query results.

Future implementations may use:

Command State Caching
Incremental Updates
Lazy Availability Evaluation

without changing Atlas Core.

Error Isolation

A failure in one command should not necessarily make unrelated commands
unavailable.

For example:

Explorer Refresh Failure

should not inherently remove:

Open Dashboard
Open Inspector

unless the Application Boundary explicitly reports the Toolbar itself as
unavailable.

Command Lifecycle

The Toolbar may support:

Registered
Visible
Enabled
Invoked
Executing
Completed
Failed

These states are presentation/application states.

They must not be confused with Atlas Resource lifecycle.

Command Group Lifecycle

Command groups may be derived from registered commands.

The Toolbar must not require a second semantic classification hierarchy merely
to group commands.

Grouping is presentation metadata.

Testing Strategy

ENG-044 tests should verify:

Toolbar identity
Toolbar presentation model
Toolbar item model
Command identity
Command registration
Command grouping
Deterministic ordering
Enabled state
Visibility state
Selection-aware state
Command execution delegation
AtlasApplication integration
Workspace integration
Dashboard navigation
Explorer commands
Inspector commands
Empty Toolbar
Loading state
Error state
Read-only behavior
No second command system
No second Resource Registry
No second Graph
No engineering state ownership
Persistence isolation
Exchange isolation
Agent isolation
AI boundary
3D boundary
Public exports

Visual rendering tests belong to the eventual frontend implementation.

Acceptance Criteria

ENG-044 is complete when:

A Toolbar capability exists within the Atlas UI architecture.
The Toolbar is hosted by the ENG-040 Workspace.
The Toolbar exposes a stable UI/application identity.
Toolbar items represent existing application commands.
Toolbar items preserve command identity.
Command registration is deterministic.
Command ordering is deterministic.
Commands support enabled/disabled presentation state.
Commands support visibility state.
Command state may depend on current AtlasID selection.
Toolbar commands execute through AtlasApplication.
The Toolbar does not directly mutate Atlas Core.
The Toolbar does not introduce a second command system.
Dashboard navigation can be represented.
Explorer commands can be represented.
Inspector commands can be represented.
Empty Toolbar state is supported.
Loading state is distinguishable.
Error state is distinguishable.
Toolbar presentation is read-only with respect to engineering state.
The Toolbar does not own a Resource Registry.
The Toolbar does not own a Resource Graph.
The Toolbar does not own a second engineering model.
Persistence remains outside the Toolbar.
Import/export remains outside the Toolbar.
Agent execution remains outside the Toolbar.
AI-generated actions remain distinguishable from canonical engineering truth.
3D implementation remains outside ENG-044.
The Toolbar remains independent from frontend technology.
Existing Atlas Core behavior remains unchanged.
Relationship to Dashboard

The Dashboard presents project-level state.

The Toolbar provides commands for interacting with that state.

Dashboard
    ↑
Toolbar

Navigation between Dashboard and other UI surfaces should occur through the
Workspace/Application boundaries.

Relationship to Explorer

The Explorer provides project navigation.

The Toolbar provides Explorer commands such as:

Refresh
Search
Filter
Clear Filter
Expand All
Collapse All

The Explorer remains responsible for interpreting those actions in its own
presentation context.

The Toolbar only presents and delegates the command.

Relationship to Inspector

The Inspector provides Resource-level detail.

The Toolbar may expose:

Open Inspector
Refresh Inspector

Selection-aware commands use the selected AtlasID.

Relationship to Future 3D Workspace

The Toolbar may provide entry points into the future 3D Workspace.

Toolbar
    ↓
Workspace View Selection
    ↓
3D View

3D implementation itself remains outside ENG-044.

Relationship to Future Panels

The Toolbar may activate or hide future Panels through Workspace/Application
commands.

The Panel Registry remains owned by the Workspace architecture.

Relationship to Future Editing

Future Resource editing commands may eventually appear in the Toolbar.

Examples:

Create
Duplicate
Delete
Move
Rotate
Scale

ENG-044 does not implement these mutations.

Any future mutation must occur through explicit application commands and the
canonical Atlas domain model.

Architectural Conclusion

ENG-044 establishes the Toolbar as the command presentation surface of Atlas.

The architectural flow is:

                     Atlas Core
                         │
                         ▼
                Atlas Application
                         │
                         ▼
                    AtlasCommand
                         ▲
                         │
                     Toolbar
                         │
                         ▼
                       User

The Toolbar completes the first command layer around the existing navigation
surfaces:

Dashboard
    ↓
Project overview


Explorer
    ↓
Project navigation


Inspector
    ↓
Resource detail


Toolbar
    ↓
Application actions

This preserves the canonical Atlas architecture:

Resource
   ↓
Registry
   ↓
Relationships
   ↓
Semantics
   ↓
Validation
   ↓
Agents
   ↓
Application
   ↓
UI

The UI presents and delegates.

Atlas Core remains the engineering source of truth.
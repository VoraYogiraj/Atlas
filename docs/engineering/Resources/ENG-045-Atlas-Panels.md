# ENG-045 — Atlas Panels

**Document ID:** ENG-045  
**Title:** Atlas Panels  
**Version:** 0.1.0  
**Status:** Complete  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-041 — Atlas Dashboard, ENG-042 — Atlas Explorer, ENG-043 — Atlas Inspector, ENG-044 — Atlas Toolbar  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas Application / Presentation layer

---

# Purpose

ENG-045 defines the Atlas Panel system as the reusable presentation container
for major Atlas UI capabilities.

Panels provide the structural surface in which capabilities such as:

- Dashboard
- Explorer
- Inspector
- Future Validation
- Future Agents
- Future Relationships
- Future 3D controls

may be hosted inside the Atlas Workspace.

The Panel system is a UI/application concern.

It does not own Atlas engineering state.

---

# Scope

ENG-045 defines:

- Panel identity
- Panel lifecycle
- Panel presentation metadata
- Panel visibility
- Panel activation
- Panel ordering
- Panel registration
- Panel lookup
- Active Panel
- Panel state
- Workspace integration
- Panel capability association
- Panel content boundaries
- Empty Workspace state
- Loading state
- Error state
- Deterministic panel ordering
- Panel selection context
- Read-only behavior
- Application boundary
- Technology independence

---

# Non-Goals

ENG-045 does not implement:

- Resource editing
- Resource creation
- Resource deletion
- Relationship editing
- Classification editing
- Validation rule editing
- Agent execution
- Persistence
- Save
- Load
- Import
- Export
- 3D rendering
- Geometry
- Camera systems
- Gizmos
- Frontend framework selection
- Visual styling system
- Window manager implementation
- Operating-system window management
- A second Workspace
- A second Resource Registry
- A second Resource Graph
- A second command system

Panels are structural UI containers.

---

# Architectural Position

The Panel system operates inside the ENG-040 UI Application Shell.

Conceptually:

```text
Atlas Core
    ↓
Atlas Application
    ↓
Atlas Workspace
    ↓
Panel Registry
    ↓
Atlas Panel
    ↓
Capability Presentation

For example:

AtlasWorkspace
    ├── Dashboard Panel
    ├── Explorer Panel
    ├── Inspector Panel
    ├── Toolbar Panel / Surface
    └── Future Panels

The Workspace owns panel lifecycle and registration.

Individual capabilities own their own presentation behavior.

Panel Principle

A Panel answers:

"Where is this UI capability hosted?"

The Workspace answers:

"What UI is currently active?"

The capability answers:

"What does this UI capability present?"

Engineering state remains owned by Atlas Core and Project.

Panel Identity

Every Panel must have a stable UI/application identity.

Examples:

dashboard
explorer
inspector
toolbar
validation
agents
relationships

Panel identity is presentation identity.

It is not:

AtlasID
Project ID
Resource ID
Relationship ID
Panel Model

A Panel should expose dedicated presentation state.

Conceptually:

AtlasPanel
├── panel_id
├── name
├── visible
├── active
├── enabled
└── order

The exact implementation may expose equivalent information through properties
or a dedicated presentation model.

Panel Registry

Panels are registered through the existing ENG-040 Panel Registry.

The canonical relationship is:

AtlasWorkspace
    ↓
AtlasPanelRegistry
    ↓
AtlasPanel

ENG-045 must reuse the existing Panel Registry rather than creating another
registry abstraction.

No Second Panel Registry

The following architecture is prohibited:

AtlasWorkspace
    ↓
AtlasPanelRegistry


AtlasDashboard
    ↓
DashboardPanelRegistry

There must be one Workspace-level Panel Registry for UI panel registration.

Panel Registration

A Panel may be registered with the Workspace.

Registration must preserve:

Stable panel identity
Panel instance
Deterministic lookup

Duplicate panel IDs must not silently replace an unrelated registered Panel
unless the existing ENG-040 contract explicitly defines replacement behavior.

Panel Lookup

The Workspace/Panel Registry must support retrieving a Panel by stable
panel_id.

Example:

workspace.panel_registry.get("explorer")

Panel lookup is UI/application lookup.

It is not Resource Registry lookup.

Panel Ordering

Panels may have a deterministic presentation order.

Ordering may be represented by:

order

or an equivalent Workspace-level ordering mechanism.

Panel ordering must not depend on:

Hash ordering
Memory address
Random identifiers
Unstable discovery order

Equivalent Workspace state should produce equivalent panel ordering.

Panel Visibility

A Panel may be:

Visible
Hidden

Visibility is transient UI state.

Changing panel visibility must not change engineering state.

Panel Activation

A Workspace may have one active Panel context.

Conceptually:

Dashboard
Explorer
Inspector

The active Panel is UI state.

Activating a Panel must not mutate:

Resources
Relationships
Classifications
Lifecycle
Validation rules
Project identity
Active Panel Identity

The active Panel should be represented by its stable panel identity.

Example:

active_panel_id = "explorer"

The Workspace must not store an entire copied Panel as active engineering
context.

Panel Enabled State

A Panel may be enabled or disabled.

Examples:

Inspector
    enabled = False

when the application context does not allow Inspector interaction.

Enabled state is UI/application state.

Panel Content Boundary

A Panel hosts a capability.

Examples:

Dashboard Panel
    ↓
AtlasDashboard


Explorer Panel
    ↓
AtlasExplorer


Inspector Panel
    ↓
AtlasInspector

The Panel itself should not reimplement the capability.

Dashboard Panel

The Dashboard may be hosted by:

panel_id = "dashboard"

The Panel provides the hosting surface.

AtlasDashboard owns project-level presentation behavior.

The Panel must not duplicate Dashboard presentation data.

Explorer Panel

The Explorer may be hosted by:

panel_id = "explorer"

The Panel provides the hosting surface.

AtlasExplorer owns project navigation and presentation behavior.

The Panel must not become a second Explorer implementation.

Inspector Panel

The Inspector may be hosted by:

panel_id = "inspector"

The Panel provides the hosting surface.

AtlasInspector owns Resource-level presentation behavior.

The Panel must not duplicate Inspector state.

Toolbar Relationship

ENG-044 establishes the Toolbar as the application command presentation
surface.

The Panel architecture must not require the Toolbar to become a normal
content Panel unless the host Workspace explicitly chooses that representation.

The Toolbar remains a command surface.

Panels remain capability containers.

Selection Context

Panels may consume the Workspace selection context.

Resource selection must remain identity-based:

AtlasID

A Panel must not store copied AtlasResource objects as selection state.

Conceptually:

Workspace
    ↓
AtlasID Selection
    ↓
Panel
    ↓
Capability
Panel Lifecycle

Panels may follow a UI lifecycle such as:

Created
    ↓
Registered
    ↓
Visible
    ↓
Active
    ↓
Inactive
    ↓
Hidden
    ↓
Disposed

The lifecycle is UI/application state.

It must not be confused with:

AtlasLifecycle

for engineering Resources.

Workspace Lifecycle

Panel lifecycle remains subordinate to Workspace lifecycle.

Conceptually:

Workspace Created
    ↓
Panel Registration
    ↓
Workspace Initialized
    ↓
Workspace Active
    ↓
Panels Active / Inactive
    ↓
Workspace Disposed

A Panel must not independently redefine Workspace lifecycle.

Panel State

Transient Panel state may include:

Visible
Active
Enabled
Expanded
Collapsed
Loading
Error

This state is presentation/application state.

It must remain separate from Atlas engineering state.

Loading State

A Panel may be loading its presentation data.

Example:

Explorer
    Loading

Loading state must not be written into Atlas Core.

Error State

A Panel may expose presentation/application errors.

The Panel must distinguish:

Loading
Empty
Ready
Unavailable
Error

A valid empty state must not silently become an error.

Empty Panel

A Panel must support valid empty content.

Examples:

No Resource Selected
No Project Data
No Commands Available
No Validation Findings

An empty state is not automatically an engineering failure.

Panel Read-Only Boundary

The Panel system itself is read-oriented infrastructure.

Panel operations such as:

Register Panel
Activate Panel
Hide Panel
Show Panel
Refresh Presentation

must not directly mutate Atlas engineering state.

Panel Mutation Boundary

A Panel may host a capability that eventually executes application commands.

However:

Panel
    ↓
AtlasApplication

must remain the application boundary.

The Panel must not directly call arbitrary Core mutation APIs.

Application Boundary

Panels must interact with Atlas through the existing ENG-039 Application
Boundary where engineering information or commands are involved.

Conceptually:

Panel
    ↓
Capability
    ↓
AtlasApplication
    ↓
Atlas Core

The Panel does not bypass the Application layer.

No Second Application Boundary

The Panel system must not create:

PanelApplication
PanelCommandEngine
PanelQueryEngine

The existing AtlasApplication remains the application boundary.

No Engineering State Ownership

Panels must not own:

AtlasProject
AtlasResourceRegistry
AtlasResourceGraph
AtlasClassificationRegistry
AtlasClassificationHierarchy
Validation Engine
Agent Runtime
Persistence Engine

They may receive application-level references where the established ENG-040
architecture explicitly permits them.

No Second Resource Registry

The Panel system must not become:

PanelResourceRegistry

or any other independent engineering Resource collection.

No Second Graph

The Panel system must not become:

PanelGraph
ExplorerGraph
InspectorGraph
DashboardGraph

The canonical Resource Graph remains owned by Atlas Project.

No Second Classification Hierarchy

A Panel may display a tree or hierarchy.

That hierarchy remains a presentation of canonical Atlas classifications.

It must not create another classification system.

Panel Commands

Panels may receive commands through the existing application command
boundary.

Examples:

Open Dashboard
Open Explorer
Open Inspector
Refresh
Search
Filter

Command semantics remain owned by ENG-039 Application architecture and
ENG-044 Toolbar integration.

Panel and Toolbar

The Toolbar may activate or control Panels through Workspace/application
commands.

Conceptually:

Toolbar
    ↓
AtlasCommand
    ↓
AtlasApplication
    ↓
Workspace
    ↓
Panel Activation

The Toolbar must not directly manipulate arbitrary Panel internals.

Panel Navigation

Navigation between Panels should use stable Panel IDs.

Example:

"dashboard"
"explorer"
"inspector"

Panel navigation must not require knowledge of frontend components.

Panel and 3D Workspace

The future 3D Workspace may be hosted inside the Panel architecture.

Conceptually:

AtlasWorkspace
    ↓
3D Workspace Panel
    ↓
3D View

ENG-045 does not implement:

Scene
Camera
Navigation mechanics
Selection rendering
Gizmos
Geometry
3D editing

Those belong to Phase 10.

Panel and Agents

Future Agent UI may be hosted in a Panel.

For example:

Agents Panel
    ↓
Agent Activity Presentation

The Panel must not directly execute Agents.

Agent execution remains owned by the existing Agent Runtime and orchestration
architecture.

Panel and Validation

Future Validation UI may be hosted in a Panel.

For example:

Validation Panel
    ↓
Validation Presentation

Validation computation remains owned by the validation subsystem.

Panel and Relationships

Future Relationship UI may be hosted in a Panel.

The Panel must use canonical Project Graph information.

It must not create a second relationship graph.

Persistence Boundary

The Panel system does not implement:

JSON serialization
Save
Load
File persistence

Persistence remains outside the Panel architecture.

Panels may host commands that eventually invoke persistence through the
Application boundary.

Exchange Boundary

The Panel system does not implement:

IFC Import
IFC Export
CAD Import
Revit Import
External exchange processing

Exchange remains governed by ENG-038 and future exchange capabilities.

Agent Boundary

The Panel system does not execute Agents directly.

Future Agent interactions must use application-level commands or existing Agent
runtime interfaces.

AI Boundary

Future AI may determine which Panel a user should open.

Example:

"Show me the wall properties"

may resolve to:

Inspector

However, the AI result must resolve to canonical UI/application identities.

AI must not silently create engineering truth.

Determinism

Equivalent Workspace state must produce equivalent:

Panel Registry
Panel ordering
Active Panel
Visibility state
Enabled state

Determinism is required for:

Testing
UI consistency
Debugging
Reproducibility
Future persistence of UI preferences
Technology Independence

ENG-045 must remain independent from:

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

The specification defines behavior and architecture, not rendering technology.

Large Workspace Compatibility

The Panel system should remain lightweight even when the Workspace contains
many capabilities.

Panels should not materialize entire Atlas Resource collections.

Panel registration should remain small and deterministic.

Future implementations may introduce:

Lazy Panel Initialization
Panel Virtualization
Deferred Presentation Loading
Background Queries
Panel State Caching

without changing the canonical Atlas model.

Workspace Separation

The Panel system must not replace the Workspace.

The architecture remains:

AtlasWorkspace
    ↓
AtlasPanelRegistry
    ↓
AtlasPanel

The Workspace remains responsible for:

Lifecycle
Active Panel
Selection context
Panel registration
Panel visibility
Panel ordering
Panel Registry Separation

The Panel Registry stores UI Panel registrations.

It must not store:

Atlas Resources
Relationships
Classifications
Projects
Agents

Those remain owned by their respective subsystems.

Testing Strategy

ENG-045 tests should verify:

Panel identity
Panel type
Panel presentation model
Panel registration
Panel lookup
Panel ordering
Panel visibility
Panel enabled state
Panel activation
Active Panel identity
Panel lifecycle
Panel Workspace integration
Dashboard hosting
Explorer hosting
Inspector hosting
Selection context
Loading state
Error state
Empty state
Read-only behavior
Application boundary
No second Panel Registry
No second Resource Registry
No second Graph
No second Classification hierarchy
No second command system
Persistence isolation
Exchange isolation
Agent isolation
AI boundary
3D boundary
Deterministic behavior
Public exports

Visual rendering tests belong to the eventual frontend implementation.

Acceptance Criteria

ENG-045 is complete when:

A reusable Panel capability exists in the Atlas UI architecture.
Panels integrate with the ENG-040 Workspace.
Panel registration uses the existing Panel Registry.
Panels expose stable UI/application identities.
Panels support deterministic lookup.
Panels support deterministic ordering.
Panels support visibility state.
Panels support enabled state.
Panels support active/inactive state.
Workspace active Panel is identity-based.
Panel lifecycle remains separate from Atlas Resource lifecycle.
Panels can host Dashboard presentation.
Panels can host Explorer presentation.
Panels can host Inspector presentation.
Panels can consume AtlasID-based selection context.
Panels support empty state.
Panels distinguish loading and error state.
Panel presentation does not mutate engineering state.
Panels use the existing AtlasApplication boundary.
Panels do not create a second command system.
Panels do not create a second Resource Registry.
Panels do not create a second Resource Graph.
Panels do not create a second Classification hierarchy.
Persistence remains outside Panels.
Import/export remains outside Panels.
Agent execution remains outside Panels.
AI-generated navigation remains separate from engineering truth.
3D implementation remains outside ENG-045.
Panels remain independent from frontend technology.
Existing Atlas Core behavior remains unchanged.
Relationship to Existing Phase 9 Capabilities

The Phase 9 UI architecture now forms:

AtlasWorkspace
    │
    ├── Dashboard
    │      ↓
    │   Project Overview
    │
    ├── Explorer
    │      ↓
    │   Project Navigation
    │
    ├── Inspector
    │      ↓
    │   Resource Detail
    │
    ├── Toolbar
    │      ↓
    │   Application Commands
    │
    └── Panels
           ↓
       Capability Hosting

The Panel system is therefore structural infrastructure rather than another
engineering-information surface.

Relationship to Phase 10

ENG-045 provides the UI shell needed to host future Phase 10 visualization.

Phase 10 remains responsible for:

Scene
Camera
Navigation
Selection
Gizmos
Basic Editing

The architectural transition is:

Phase 9
UI Shell
    ↓
Panels
    ↓
Phase 10
3D Workspace
Architectural Conclusion

ENG-045 establishes Panels as reusable UI/application containers while
preserving the separation between:

Engineering State
    ↓
Atlas Core


Application Behavior
    ↓
AtlasApplication


Workspace State
    ↓
AtlasWorkspace


Panel Structure
    ↓
AtlasPanel


Capability Presentation
    ↓
Dashboard / Explorer / Inspector / Future Views

The Panel architecture does not redefine Atlas engineering knowledge.

It provides the structural UI layer required for Atlas to become a usable
engineering workspace.
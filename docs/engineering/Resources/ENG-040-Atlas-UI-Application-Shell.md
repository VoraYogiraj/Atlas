# ENG-040 — Atlas UI Application Shell

**Document ID:** ENG-040  
**Title:** Atlas UI Application Shell  
**Version:** 0.1.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas UI/Application layer

---

# Purpose

ENG-040 defines the application shell that hosts the Atlas user interface.

The application shell provides the structural workspace in which Atlas
presentation surfaces operate.

The shell is responsible for:

- Workspace structure
- View composition
- Panel registration
- Panel visibility
- Active view
- Workspace state
- Selection context
- Application lifecycle

The shell does not become part of the canonical Atlas engineering model.

---

# Scope

ENG-040 defines:

- Atlas Workspace
- Workspace state
- Atlas panels
- Panel registration
- Panel identity
- Panel visibility
- Active panel state
- Main view
- Application shell lifecycle
- Workspace composition
- View registration
- View identity
- UI context
- Shell/core separation

ENG-040 establishes the structural UI layer required by Phase 9.

---

# Non-Goals

ENG-040 does not define:

- Specific frontend framework
- Specific rendering engine
- Visual design system
- 3D rendering
- Geometry editing
- BIM rendering
- Full Dashboard functionality
- Full Explorer functionality
- Full Inspector functionality
- Collaboration UI
- AI Assistant UI
- Production styling
- Responsive design implementation

Those capabilities belong to future UI specifications and implementation
milestones.

---

# Architectural Position

ENG-040 sits directly above ENG-039.

```text
User
  ↓
UI Application Shell
  ↓
ENG-039 Application Boundary
  ↓
Atlas Core

The shell is therefore a presentation composition layer.

It must not bypass the ENG-039 application boundary to directly manipulate
Atlas domain objects.

Canonical Rule

The Atlas UI shell is not the Atlas engineering model.

The canonical engineering model remains:

AtlasProject
AtlasResource
AtlasID
AtlasClassification
AtlasProperty
AtlasRelationship
AtlasResourceGraph
Semantic Tags
Categories
Lifecycle
Validation
Constraints
Agents

The shell may reference application state and presentation state, but it must
not become an alternative source of engineering truth.

Workspace

The workspace is the top-level UI composition context.

Conceptually:

Atlas Workspace
┌────────────────────────────────────────┐
│ Toolbar                                │
├────────────┬───────────────────┬───────┤
│ Explorer   │ Main View         │Inspector
│            │                   │       │
│            │                   │       │
├────────────┴───────────────────┴───────┤
│ Auxiliary / Status / Future Panels     │
└────────────────────────────────────────┘

The actual visual layout is an implementation concern.

The architectural requirement is that the workspace can compose multiple
independent UI surfaces.

AtlasWorkspace

AtlasWorkspace represents the structural UI workspace.

It is responsible for:

Workspace identity
Registered panels
Registered views
Active view
Active panels
Workspace state

It must not own:

AtlasProject
AtlasResourceRegistry
AtlasResourceGraph
Validation Engine
Agent Runtime

The workspace interacts with those systems through the ENG-039 application
boundary.

Workspace Identity

Each workspace should have a stable identity within the application session.

Example conceptual representation:

Workspace
 └── id

Workspace identity is UI/application identity.

It must not be confused with:

AtlasProject ID
AtlasResource ID
AtlasRelationship ID

A future system may support multiple workspaces for the same Atlas Project.

Workspace State

Workspace state represents presentation and interaction state.

Examples:

Active View
Visible Panels
Active Panel
Selected Resource
Navigation Context
Search Context
Display Preferences

Workspace state is distinct from engineering state.

Workspace State Invariant

Workspace state must not silently become engineering state.

For example:

Active Panel
Expanded Explorer Node
Selected View
Viewport Mode

must not become Atlas domain data merely because they are stored in the
workspace.

Panels

A Panel is a modular presentation surface hosted by the workspace.

Examples:

Dashboard
Explorer
Inspector
Validation
Relationships
Agents
Tasks
History
Documents
AI Assistant

A panel should have:

Stable identity
Display name
Visibility state
Optional ordering
Presentation responsibility
AtlasPanel

AtlasPanel represents the architectural contract for a panel.

A Panel is not a domain model.

A Panel must not:

Own AtlasProject
Own Resource Registry
Own Resource Graph
Implement engineering rules
Implement validation independently
Maintain a duplicate Resource database

A Panel may consume application queries and issue application commands.

Panel Identity

Panel identity must be stable and machine-readable.

Examples:

dashboard
explorer
inspector
validation
relationships
agents
history

The identity should not depend on:

Display text
Screen position
Component memory address
Rendering technology
Panel Metadata

A panel may expose presentation metadata such as:

id
name
description
category
default visibility

Future extensions may include:

icon
keyboard shortcut
permissions
feature flags
dock position

These remain UI/application concerns.

Panel Registry

The workspace must maintain a dedicated panel registry.

Conceptually:

AtlasWorkspace
      ↓
AtlasPanelRegistry
      ↓
Registered Panels

The Panel Registry is a UI registry.

It must not replace:

AtlasResourceRegistry
AtlasProjectRegistry
Panel Registration

A panel may be registered with the workspace.

Registration must enforce unique panel identity.

Example:

register(explorer)
register(inspector)
register(dashboard)

Registering the same panel identity twice must fail explicitly.

Panel Lookup

Panels should be retrievable by stable identity.

Example:

get("explorer")
get("inspector")
get("dashboard")

Unknown panel identity should return an explicit not-found result or raise a
clear error according to the implementation contract.

Panel Visibility

The workspace may control whether a panel is visible.

Example states:

Visible
Hidden

Visibility is UI state.

Changing visibility must not modify Atlas engineering state.

Active Panel

The workspace may maintain an active panel.

The active panel must refer to a registered Panel identity.

An active panel that has not been registered must not become valid workspace
state.

Main Views

A View represents the principal presentation surface displayed in the main
workspace region.

Examples:

Project View
Resource View
3D View
Validation View
Knowledge View
Document View

ENG-040 defines only the architectural view boundary.

Actual 3D behavior is deferred to the 3D Workspace phase.

AtlasView

AtlasView represents a future-ready architectural contract for a main
workspace view.

A View should have:

Stable identity
Display name
Presentation responsibility

A View must not become a canonical engineering model.

View Registry

The workspace may maintain a dedicated View Registry.

Conceptually:

AtlasWorkspace
      ↓
AtlasViewRegistry
      ↓
Registered Views

This registry contains UI presentation views only.

It must not replace any Atlas engineering registry.

Active View

The workspace should maintain a single active main View at a time.

The active View must refer to a registered View.

Changing the active View changes presentation state only.

Selection Context

The workspace may expose the currently selected Atlas Resource through the
ENG-039 identity-based selection contract.

Conceptually:

Workspace
   ↓
Selection Context
   ↓
AtlasID
   ↓
ENG-039 Application Boundary
   ↓
AtlasResource

The workspace must not store a copied canonical Resource as the selection.

UI Context

The workspace may provide a shared UI context containing:

Current Project Context
Current Selection
Workspace State
Active View
Active Panels

This context is a presentation/application context.

It must not become a second Atlas domain context.

Project Context

The shell may operate against one Atlas Project at a time initially.

The project itself remains owned by the ENG-039 application boundary.

Conceptually:

AtlasWorkspace
      ↓
AtlasApplication
      ↓
AtlasProject

The Workspace must not create or replace the AtlasProject.

Application Lifecycle

The shell should define a basic application lifecycle:

Create
Initialize
Activate
Run
Deactivate
Dispose

The exact event loop or runtime implementation is outside the scope of
ENG-040.

The purpose of the lifecycle is to provide predictable ownership and
initialization boundaries.

Initialization

Workspace initialization should establish:

Workspace identity
Panel registry
View registry
Initial UI state
Default active View
Default panels

Initialization must not mutate Atlas engineering state simply because the UI
has started.

Activation

Activation indicates that a workspace is ready for interaction.

Activation may:

Build presentation surfaces
Load UI state
Establish selection context
Prepare registered panels

Activation must not bypass Atlas application commands or queries.

Deactivation

Deactivation should release active presentation resources without modifying
engineering state unless an explicit application command requests such a
change.

Disposal

Disposal should release UI/application-owned state.

Disposal must not delete or modify the Atlas Project merely because a UI
workspace is closed.

Project persistence remains an explicit operation.

Command Integration

Workspace actions that change engineering state must pass through ENG-039
Commands.

Example:

Toolbar
   ↓
Workspace Action
   ↓
AtlasCommand
   ↓
AtlasApplication
   ↓
Atlas Core

The Workspace must not implement domain mutation directly.

Query Integration

Workspace presentation should use ENG-039 Queries when Atlas information is
required.

Example:

Workspace
   ↓
AtlasQuery
   ↓
AtlasApplication
   ↓
Atlas Core
   ↓
Presentation Model
   ↓
UI
Panel Command Boundary

Panels follow the same application boundary.

Panel
  ↓
Command
  ↓
AtlasApplication
  ↓
Atlas Core

A Panel must not directly modify Resource internals.

Panel Query Boundary

Panels retrieve information through application queries and presentation
models.

Atlas Core
   ↓
Query
   ↓
Presentation Model
   ↓
Panel
Workspace and Agents

The Workspace may expose Agent activity through Panels.

For example:

Agent Panel
Agent Status
Agent Results
Task Progress

Agents themselves remain independent from the Workspace.

The dependency direction remains:

Workspace
   ↓
AtlasApplication
   ↓
Agent Runtime

not:

Agent Runtime
   ↓
Workspace
Workspace and Validation

Validation is a core Atlas capability.

The Workspace may display validation through a Validation Panel.

The architecture is:

Atlas Validation
      ↓
Application Query
      ↓
Presentation Model
      ↓
Validation Panel

The Panel must not reimplement Atlas validation rules.

Workspace and Persistence

The shell may expose Save and Load actions.

These actions must use the existing persistence boundary.

Workspace Action
      ↓
Application Operation
      ↓
AtlasProjectPersistence
      ↓
Atlas Project

The Workspace must not contain serialization or filesystem logic.

Workspace and Exchange

Import and Export remain governed by ENG-038.

Conceptually:

Workspace
     ↓
Application Operation
     ↓
Exchange Boundary
     ↓
External Representation

The shell must not become an importer or exporter.

Future 3D Workspace

The main View boundary allows the future 3D Workspace to become a registered
Atlas View.

Conceptually:

AtlasWorkspace
      ↓
AtlasViewRegistry
      ↓
3D View
      ↓
Renderer

The 3D renderer remains a presentation technology.

It must not become the canonical Resource or Relationship model.

Future Multiple Views

The shell should support future main views such as:

3D
2D
Document
Knowledge Graph
Validation
Schedules
Analytics
GIS
BIM

Only one active main View needs to be assumed by the initial implementation,
but the architecture should not prohibit multiple registered Views.

Future Docking and Layout

Future UI implementations may support:

Docking
Floating Panels
Tabbed Panels
Resizable Areas
Saved Layouts
Multi-window Workspaces

These are workspace concerns.

They must not alter engineering state.

Future Multi-Workspace Support

The architecture should permit future scenarios such as:

Project Workspace
Review Workspace
Construction Workspace
Validation Workspace
AI Workspace

Multiple UI Workspaces may reference the same Atlas Project through shared
application services.

Workspace Persistence

Workspace layout persistence may be introduced later.

Potential persisted UI state may include:

Panel visibility
Panel ordering
Active View
Workspace layout
Display preferences

This must remain separate from Atlas engineering persistence.

UI workspace persistence must not modify the canonical Atlas JSON model unless
an explicit future specification extends the model.

Undo / Redo Compatibility

The shell should remain compatible with future Command history.

Conceptually:

Command
  ↓
Command History
  ↓
Undo / Redo

ENG-040 does not implement undo/redo.

Future implementations must preserve Atlas engineering invariants.

Event Compatibility

The Workspace should remain compatible with future application events.

Potential events include:

ResourceCreated
ResourceUpdated
ResourceDeleted
SelectionChanged
PanelOpened
PanelClosed
ViewActivated
ProjectLoaded
ProjectSaved
ValidationCompleted
AgentCompleted

The actual event transport is outside the scope of ENG-040.

Error Handling

Workspace errors must remain distinguishable from engineering errors.

Examples:

Panel Already Registered
Panel Not Found
View Already Registered
View Not Found
Invalid Workspace State
Invalid Application Command

Engineering errors continue to originate from Atlas Core/application services.

Extensibility

The shell must support future extension without requiring a rewrite.

Potential future extension points include:

Panel Plugins
View Plugins
Toolbars
Commands
Menus
Context Menus
Keyboard Shortcuts
Themes
Layouts
Workspaces
AI Assistants

ENG-040 does not define a plugin system.

It only establishes that the architecture must not prevent future extension.

Technology Independence

ENG-040 must remain independent from:

React
Vue
Angular
Svelte
Next.js
Electron
Tauri
Three.js
Babylon.js
WebGL
Qt
Flutter

The shell defines architectural behavior, not implementation technology.

Domain Independence

The dependency direction must remain:

UI Shell
   ↓
ENG-039 Application Boundary
   ↓
Atlas Core

The following must never occur:

Atlas Core
   ↓
UI Shell

or:

AtlasResource
   ↓
UI Panel

The canonical domain must remain UI-independent.

Testing Strategy

ENG-040 tests should verify architectural and behavioral contracts.

The initial test layer should cover:

Workspace identity
Panel registration
Panel uniqueness
Panel lookup
Panel visibility
Active panel
View registration
View uniqueness
View lookup
Active view
Selection context
UI state isolation
Project ownership boundary
Command integration
Query integration
Panel/core separation
View/core separation
Lifecycle behavior
Persistence separation
Exchange separation
Agent independence
Future 3D compatibility

Visual rendering tests belong to later UI implementation milestones.

Acceptance Criteria

ENG-040 is complete when:

An Atlas Workspace can be created.
The Workspace has stable UI identity.
Panels can be registered.
Duplicate panel identities are rejected.
Panels can be retrieved by identity.
Panel visibility can be controlled.
Active panel state is identity-based.
Views can be registered.
Duplicate view identities are rejected.
Views can be retrieved by identity.
Active view state is identity-based.
Workspace state remains separate from engineering state.
Workspace selection uses AtlasID identity.
Workspace does not own a Resource Registry or Resource Graph.
Workspace actions use ENG-039 application Commands.
Workspace reads use ENG-039 application Queries.
Panels do not directly mutate Atlas domain objects.
Views do not own canonical engineering state.
Workspace lifecycle is explicit.
Workspace does not implement persistence or exchange logic.
Agents remain independent from UI components.
The architecture supports a future 3D View.
The architecture supports future additional Panels and Views.
The implementation remains frontend-technology independent.
Existing Atlas Core tests remain green.
Relationship to ENG-039

ENG-039 defines the architectural boundary between UI/application concerns
and the canonical Atlas engineering model.

ENG-040 implements the structural shell that operates inside that boundary.

ENG-039
UI/Application Architecture
        ↓
ENG-040
UI Application Shell
        ↓
Future UI Panels / Views
Relationship to Phase 9

ENG-040 provides the shell required for Phase 9 — User Interface.

Phase 9 capabilities will progressively occupy the shell:

Dashboard
Explorer
Inspector
Toolbar
Panels

ENG-040 does not fully implement these individual capabilities.

Relationship to Phase 10

The main View architecture established by ENG-040 provides the hosting boundary
for Phase 10 — 3D Workspace.

Future 3D capabilities may include:

Scene
Camera
Navigation
Selection
Gizmos
Basic Editing

The 3D implementation remains separate from the application shell.

Future Architecture

The intended application structure becomes:

                         ATLAS
                           │
                    Canonical Core
                           │
                Application Boundary
                        ENG-039
                           │
                    UI Application
                        Shell
                        ENG-040
                           │
             ┌─────────────┼─────────────┐
             │             │             │
          Panels         Views        Toolbar
             │             │             │
      Dashboard       3D View         Commands
      Explorer        2D View
      Inspector       Documents
      Validation      Knowledge
      Agents          Analytics

The shell remains a composition layer.

The canonical Atlas model remains authoritative.

Architectural Conclusion

ENG-040 establishes the Atlas UI Application Shell as the structural
presentation environment above the ENG-039 application boundary.

The essential architecture is:

User
 ↓
Atlas UI Shell
 ├── Toolbar
 ├── Panels
 ├── Views
 ├── Selection Context
 └── Workspace State
 ↓
ENG-039 Application Boundary
 ├── Commands
 ├── Queries
 └── Presentation Models
 ↓
Atlas Core
 ├── Resources
 ├── Registry
 ├── Relationships
 ├── Semantics
 ├── Validation
 └── Agents

The shell organizes the user experience.

The application boundary translates user intent.

The Atlas Core remains the source of engineering truth.

This separation allows Atlas to evolve from a basic workspace into a
3D engineering environment, AI-assisted workspace, collaborative engineering
system, and ultimately an Engineering Intelligence Platform without replacing
the canonical model.
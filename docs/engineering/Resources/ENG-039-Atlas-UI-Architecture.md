# ENG-039 — Atlas UI Architecture

**Document ID:** ENG-039  
**Title:** Atlas UI Architecture  
**Version:** 0.1.0  
**Status:** Complete  
**Depends On:** ENG-035A, ENG-036, ENG-037, ENG-038  
**Phase:** Phase 9 — User Interface  
**Implementation:** Future UI/Application layer

---

# Purpose

ENG-039 defines the architectural boundary between the canonical Atlas
engineering model and the Atlas user interface.

The purpose of this specification is to establish a future-ready UI
architecture that can support:

- Dashboard
- Explorer
- Inspector
- Toolbar
- Panels
- Future 3D Workspace
- AI-assisted workflows
- Future collaboration
- Future external integrations

The UI must present and operate on Atlas engineering knowledge without becoming
the canonical representation of that knowledge.

---

# Scope

ENG-039 defines:

- Atlas UI architectural boundaries
- Application interaction boundaries
- Commands
- Queries
- Presentation models
- UI state
- Engineering state
- Resource selection
- Workspace structure
- Panel architecture
- Explorer architecture
- Inspector architecture
- Toolbar/action architecture
- Agent/UI interaction
- UI extensibility
- Core/UI separation
- Future 3D Workspace boundary

ENG-039 does not define a specific frontend framework or rendering library.

---

# Non-Goals

ENG-039 does not implement:

- React
- Vue
- Angular
- Svelte
- Next.js
- Electron
- Three.js
- Babylon.js
- WebGL
- Desktop-specific implementation
- Mobile-specific implementation
- Final visual design
- Production UI components
- Full 3D rendering
- Geometry editing
- Collaboration UI
- Cloud UI

Technology choices belong to implementation specifications.

---

# Architectural Principle

The Atlas UI is a presentation and application boundary around the canonical
Atlas engineering model.

The UI presents Atlas knowledge and expresses user intent.

The UI does not become Atlas itself.

The fundamental interaction model is:

```text
User
  ↓
UI Interaction
  ↓
Command / Query
  ↓
Application Boundary
  ↓
Atlas Core
  ↓
Resources / Registry / Graph
  ↓
Semantics / Validation / Agents

For reads:

Atlas Core
    ↓
Query
    ↓
Presentation Model
    ↓
UI
Canonical Model Boundary

The Atlas Core remains the canonical source of engineering state.

The canonical model includes:

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
Agent Runtime
Orchestrator
Coordination

The UI must not create a competing canonical representation of these objects.

UI Does Not Own Engineering Truth

The UI must not become the authoritative source for:

Resource identity
Resource classification
Resource properties
Relationships
Semantic meaning
Lifecycle
Validation state
Project state

The UI may temporarily represent these concepts for presentation, but the
canonical values remain in Atlas Core.

Application Boundary

The UI should interact with Atlas Core through an application boundary.

Conceptually:

UI
 ↓
Application
 ├── Commands
 ├── Queries
 └── Presentation Models
 ↓
Atlas Core

This boundary prevents UI components from becoming tightly coupled to the
internal structure of the domain model.

Commands

Commands represent user or system intent that may change engineering state.

Examples:

CreateResource
UpdateResource
DeleteResource
AddRelationship
RemoveRelationship
SetProperty
ChangeLifecycle
ApplyClassification
AddSemanticTag
AddCategory
RunValidation

A command represents an intended operation.

A command does not itself define the engineering rules governing the operation.

Those rules remain with the Atlas domain and application services.

Queries

Queries retrieve Atlas information without changing engineering state.

Examples:

GetProject
GetResource
ListResources
FindResources
GetClassification
GetRelationships
GetSemanticTags
GetCategories
GetValidationResults

Queries should return information suitable for presentation without requiring
UI components to traverse internal domain structures unnecessarily.

Presentation Models

The UI may use presentation models or view models.

A presentation model is a representation prepared for a UI.

It is not the canonical Atlas Resource.

Example:

AtlasResource
      ↓
Resource Presentation Model
      ↓
Inspector UI

A presentation model may contain:

Display name
Formatted property values
Display labels
UI state
Human-readable relationship summaries
Validation summaries

Presentation models must not replace or mutate the underlying canonical model.

Engineering State vs UI State

This separation is mandatory.

Engineering State

Engineering state includes:

Resources
Classifications
Properties
Relationships
Semantics
Lifecycle
Constraints
Validation results
Project metadata
UI State

UI state includes:

Current selection
Active panel
Expanded tree nodes
Active filters
Search text
Workspace layout
Focused element
Temporary editing state
Viewport state
Camera state
Display preferences

UI state must not silently become engineering state.

Resource Selection

Resource selection must be identity based.

The canonical selected Resource identity should be represented through AtlasID.

Conceptually:

UI Selection
    ↓
AtlasID
    ↓
AtlasProject / Registry
    ↓
AtlasResource

The UI should not treat a copied UI object as the authoritative Resource.

This allows the same Resource to be selected and represented consistently across:

Explorer
Inspector
Future 3D Workspace
Search
Agents
Validation
Relationship views
Selection Invariant

A selected Resource must continue to refer to the same canonical Resource even
when:

The Resource is re-rendered
The Explorer is refreshed
The Inspector is reopened
The 3D Workspace updates
The UI layout changes
An Agent modifies presentation state
The Project is reloaded

The canonical identity remains the AtlasID.

Explorer

The Explorer presents navigable Atlas structure.

The Explorer may display:

Project
├── Classifications
├── Resources
├── Relationships
├── Categories
├── Semantic Tags
└── Other Project Structures

The Explorer is a navigation surface.

It must not become a second Resource Registry.

Resource retrieval remains the responsibility of Atlas Core and the application
boundary.

Explorer Responsibilities

The Explorer should:

Navigate
Search
Filter
Select
Expand and collapse
Present hierarchy
Present project structure

The Explorer should not:

Define Resource identity
Maintain a competing Resource database
Redefine relationships
Bypass domain validation
Implement engineering rules independently
Inspector

The Inspector presents detailed information about the current selection.

Conceptually:

Selected AtlasID
      ↓
AtlasResource
      ↓
Resource Presentation Model
      ↓
Inspector

The Inspector may present:

Identity
Classification
Properties
Metadata
Semantic Tags
Categories
Lifecycle
Relationships
Validation

The Inspector may provide editing controls, but editing must execute through
defined Commands or application operations rather than mutating hidden copies
of Atlas state.

Inspector Responsibilities

The Inspector should:

Display Resource information
Display engineering properties
Display relationships
Display semantic information
Display lifecycle
Present validation findings
Initiate supported edits

The Inspector should not:

Become a Resource database
Invent engineering values
Bypass validation
Modify internal domain state directly
Toolbar and Actions

The Toolbar provides access to application Commands.

Conceptually:

Toolbar Action
      ↓
Command
      ↓
Application Boundary
      ↓
Atlas Core

Examples:

Create
Edit
Delete
Undo
Redo
Validate
Search
Save
Load
Run Agent

Not every Toolbar action must directly modify engineering state.

Actions should map to explicit application operations.

Panels

Panels provide modular presentation surfaces within the Atlas workspace.

Initial panels include:

Dashboard
Explorer
Inspector
Toolbar

Future panels may include:

Validation
Relationships
Documents
Agents
Tasks
History
Collaboration
AI Assistant
Properties
Statistics
Search

Panels should remain independent presentation modules.

A panel must not create a private canonical copy of Atlas engineering state.

Dashboard

The Dashboard provides a project-level overview.

Potential information includes:

Project identity
Resource counts
Classification summaries
Validation summaries
Relationship summaries
Agent activity
Project status

The Dashboard is informational and application-oriented.

It does not become a second project model.

UI and Agents

Agents operate on Atlas knowledge through the existing Agent Runtime,
Orchestrator, and Coordination architecture.

The UI may request Agent operations through the application boundary.

Conceptually:

UI
 ↓
Agent Command / Request
 ↓
Application Boundary
 ↓
Agent Runtime
 ↓
Orchestrator / Coordination
 ↓
Atlas Agents
 ↓
Atlas Core

The UI must not directly implement Agent reasoning.

Similarly, Agents must not depend on specific UI components.

This permits:

UI → Agent
API → Agent
Automation → Agent
Future AI Planner → Agent

through shared execution contracts.

AI Interaction Boundary

Future AI systems may interact with Atlas through the application/core
boundary.

The architecture should support:

User
 ↓
UI
 ↓
AI Interaction
 ↓
Atlas Application
 ↓
Atlas Core

and:

Agent
 ↓
Atlas Application
 ↓
Presentation Model
 ↓
UI

AI output must not become canonical engineering state without passing through
the appropriate Atlas operations, validation, and authorization mechanisms.

3D Workspace Boundary

Phase 9 introduces the UI workspace boundary.

The deeper 3D implementation is defined separately by the Phase 10
3D Workspace capability.

ENG-039 therefore defines only the architectural interface between the UI shell
and future 3D visualization.

Atlas Application Boundary
          ↓
       3D View
          ↓
       Renderer

The renderer must consume Atlas presentation data and selection state.

The renderer must not become the canonical engineering model.

Future 3D Interaction

Future 3D operations should follow:

3D User Interaction
       ↓
Selection / Command
       ↓
Application Boundary
       ↓
Atlas Core

not:

3D Mesh
  ↓
modify Atlas independently

This ensures that future geometry systems remain views and interaction surfaces
over Atlas engineering state.

Event / Update Boundary

The UI must be able to react to changes in Atlas state without requiring
every component to directly manipulate domain objects.

Future implementations may use an event/update mechanism such as:

Atlas State Change
       ↓
Application Update
       ↓
Presentation Update
       ↓
UI Refresh

Events may represent:

ResourceCreated
ResourceUpdated
ResourceDeleted
RelationshipAdded
RelationshipRemoved
ClassificationChanged
ValidationCompleted
AgentCompleted
ProjectLoaded

The exact event implementation is outside the scope of ENG-039.

UI Refresh Invariant

Presentation state should be derived from canonical Atlas state.

When engineering state changes:

Atlas Core
   ↓
Application Update
   ↓
Presentation Model
   ↓
UI

The UI must not require manual hidden mutation of domain objects to remain
consistent.

Workspace Architecture

The initial Atlas workspace should support modular surfaces.

Conceptually:

Atlas Application
┌────────────────────────────────────────┐
│ Toolbar                                │
├────────────┬───────────────────┬───────┤
│ Explorer   │ Main Workspace    │Inspector│
│            │                   │       │
│            │ Future 3D View    │       │
│            │ / Other Views     │       │
├────────────┴───────────────────┴───────┤
│ Status / Context / Future Panels       │
└────────────────────────────────────────┘

The exact visual layout is an implementation and design concern.

The architectural requirement is modular separation between navigation,
presentation, actions, and future visualization.

UI Replaceability

The UI must remain replaceable without requiring replacement of the Atlas
domain model.

A future Atlas installation may provide:

Desktop UI
Web UI
Embedded UI
Mobile UI
3D UI
API Client
AI Interface

All should interact with Atlas through stable application/core contracts.

The existence of a particular UI technology must not become a domain
dependency.

Headless Operation

Atlas Core must remain capable of operating without the UI.

Examples:

Command line
Automated tests
Agents
Background processes
Future APIs
Future cloud services

UI presence must never be required for basic domain validity or core execution.

External Integration Compatibility

The UI architecture must remain compatible with ENG-038's external exchange
boundary.

Conceptually:

External System
      ↓
Exchange / Import
      ↓
Atlas Core
      ↓
Application Boundary
      ↓
UI

or:

UI
 ↓
Atlas Core
 ↓
Exchange / Export
 ↓
External System

External systems must not directly manipulate UI state as a substitute for
Atlas state.

Persistence Compatibility

The UI may trigger:

Save
Load
Import
Export

but persistence and exchange remain separate services.

Conceptually:

UI
 ↓
Application Command
 ↓
Persistence / Exchange
 ↓
Atlas Project

The UI itself does not implement serialization or filesystem persistence.

Validation Compatibility

Validation remains a core engineering capability.

The UI presents validation results.

Atlas Validation
      ↓
Validation Result
      ↓
Application Query
      ↓
Inspector / Validation Panel

The UI must not replace validation logic with presentation-level checks.

Collaboration Compatibility

Future collaboration capabilities may include:

Multiple Users
Human Review
Agent Review
Decision Tracking
Comments
History
Approval

ENG-039 must allow these capabilities to appear as additional application
services and panels without changing the canonical UI boundary.

History Compatibility

Future Resource history and revision systems must remain separate from UI state.

The UI may display:

Current State
History
Revisions
Changes
Impact

but the underlying history belongs to Atlas domain/application services.

Provenance Compatibility

Future provenance information may be presented through the UI.

Examples:

Source
Author
External System
Import
Derived From
AI Generated
Human Verified

The UI only presents provenance.

It does not own the canonical provenance model.

Interoperability Compatibility

The UI must remain compatible with future:

IFC
Revit
CAD
BIM
GIS
Documents
External APIs

through the application/exchange boundary.

UI components should not contain format-specific engineering logic unless that
capability is explicitly part of a future presentation feature.

Security Boundary

The UI is not the security authority.

Future permissions and authorization systems must operate through application
and platform boundaries.

A UI control being hidden or disabled must not be considered an authorization
mechanism.

Error Handling

Application errors must be represented to the UI through explicit result or
error contracts.

The UI must not interpret arbitrary domain internals to determine failure.

Examples:

Invalid Resource
Validation Failure
Unknown Resource
Unknown Command
Agent Failure
Persistence Failure
Exchange Failure

Errors should remain distinguishable between:

Engineering Error
Application Error
UI Presentation Error
Extensibility

The UI architecture must allow new presentation surfaces without changing the
canonical Atlas model.

Future additions may include:

Validation Panel
Agent Panel
Document Viewer
History Panel
Change Impact Panel
AI Assistant
Knowledge Graph Viewer
BIM Viewer
Material Browser
Approval Panel
Construction Dashboard
GIS View

These are application/presentation extensions.

They do not create competing engineering models.

Canonical State Rule

The canonical Atlas engineering state exists in the Atlas domain/application
layer.

UI state is transient unless explicitly persisted by a future UI/workspace
specification.

The following are examples of transient UI state:

Selected Resource
Open Panel
Expanded Tree
Search Text
Camera Position
Viewport Mode
Temporary Form State

They must not be mistaken for engineering truth.

Domain Independence

Atlas domain modules must not depend on UI modules.

The dependency direction is:

UI
 ↓
Application
 ↓
Atlas Domain

Never:

Atlas Domain
 ↓
UI

This prevents presentation concerns from contaminating the engineering model.

Application Independence

The application layer should remain usable by more than one UI.

Potential future consumers include:

Desktop UI
Web UI
CLI
AI Agents
Automation
API
Integration Services

This makes the application boundary a reusable Atlas interaction layer.

Future Architecture

The long-term Atlas interface architecture is:

                         ATLAS
                           │
                    Canonical Core
                           │
                Application Boundary
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
      UI                  AI                External
       │                   │                   │
 ┌─────┼──────┐       Agents / AI        Exchange
 │     │      │
Explorer Inspector 3D
 │     │      │
Panels Toolbar Workspace

The canonical engineering model remains at the center.

Architecture Review Criteria

A future UI capability should be considered compatible with ENG-039 when:

It does not create a competing Resource model.
It preserves AtlasID identity.
It uses application commands for engineering mutations.
It uses application queries for engineering reads.
It separates UI state from engineering state.
It does not bypass Atlas validation.
It does not implement engineering rules independently.
It does not create a second Resource/Relationship graph.
It can operate with future presentation technologies.
It remains compatible with Agents and external integrations.
It can evolve without changing Atlas Core unnecessarily.
It can be tested independently from UI rendering technology.
Relationship to Existing Specifications

ENG-039 depends conceptually on:

ENG-001 — Atlas Resource
ENG-002 — Resource Identity
ENG-003 — Resource Classification
ENG-004 — Resource Properties
ENG-005 — Resource Relationships
ENG-006 — Resource Semantics
ENG-007 — Resource Lifecycle
ENG-008 — Resource Validation
ENG-009 — Resource Serialization
ENG-010 — Atlas Resource Registry
ENG-025 — Resource Categories
ENG-026 — Resource Validation Runtime Model
ENG-027 — Property Constraints
ENG-028 — Agent Runtime
ENG-029 — Orchestrator Agent
ENG-030 — Resource Agent
ENG-031 — Registry Agent
ENG-032 — Semantic Agent
ENG-033 — Relationship Agent
ENG-034 — Validation Agent
ENG-035 — Multi-Agent Coordination
ENG-035A — Foundation Hardening
ENG-036 — Atlas JSON Serialization
ENG-037 — Project Save / Load
ENG-038 — Import / Export
Phase 9 Relationship

ENG-039 establishes the architecture for Phase 9 — User Interface.

Phase 9 includes:

Dashboard
Explorer
Inspector
Toolbar
Panels

The deeper 3D implementation is intentionally separated into the next phase.

Phase 10 Relationship

Phase 10 — 3D Workspace may introduce:

Scene
Camera
Navigation
Selection
Gizmos
Basic Editing

ENG-039 provides the UI/application boundary through which these capabilities
will interact with Atlas Core.

Acceptance Criteria

ENG-039 is complete when:

The UI is defined as a presentation/application boundary.
Atlas Core remains the canonical engineering model.
UI state is separate from engineering state.
Commands and Queries define the intended interaction boundary.
Resource selection is identity-based through AtlasID.
Explorer does not become a second Resource Registry.
Inspector does not become a second Resource model.
Toolbar actions map to explicit application operations.
Panels remain modular presentation surfaces.
Agents remain independent from UI components.
Future 3D Workspace can operate through the same boundary.
Future desktop/web/API/AI interfaces can reuse the application boundary.
Persistence and Exchange remain separate from UI implementation.
Validation remains a core responsibility.
Future collaboration, provenance, history, BIM, and interoperability can
integrate without replacing the UI architecture.
UI technology remains an implementation choice.
Atlas Core remains usable without the UI.
The architecture supports future extension without requiring replacement
of the canonical engineering model.
Verification Strategy

ENG-039 verification should initially focus on architectural contracts rather
than visual rendering.

The initial test layer should verify:

Command boundary
Query boundary
Selection identity
UI state isolation
Presentation model isolation
Application/Core separation
Agent independence
Persistence independence
Exchange independence
Extensibility contracts

Visual rendering tests belong to future UI implementation specifications.

Architectural Conclusion

ENG-039 establishes the Atlas UI as a replaceable presentation and application
boundary over the canonical Atlas engineering model.

The central principle is:

User
 ↓
UI
 ↓
Commands / Queries
 ↓
Application Boundary
 ↓
Atlas Core
 ↓
Engineering Knowledge

The UI presents engineering knowledge.

The UI does not become engineering knowledge.

This architecture allows Atlas to evolve from a foundation into:

Engineering Workspace
        ↓
3D Workspace
        ↓
AI-Assisted Workspace
        ↓
Collaborative Engineering Environment
        ↓
Engineering Intelligence Platform

without requiring replacement of the canonical Atlas engineering model.

The Atlas Core remains authoritative.
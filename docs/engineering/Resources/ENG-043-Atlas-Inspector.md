# ENG-043 — Atlas Inspector

**Document ID:** ENG-043  
**Title:** Atlas Inspector  
**Version:** 0.1.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-042 — Atlas Explorer  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas Application / Presentation layer

---

# Purpose

ENG-043 defines the Atlas Inspector as the detailed, Resource-level
presentation surface for the currently selected Atlas Resource.

The Inspector exposes the engineering identity, classification, lifecycle,
properties, metadata, semantic tags, categories, and relationship context of
the selected Resource.

The Inspector presents canonical Atlas information.

It does not replace or mutate the canonical Atlas Resource.

---

# Scope

ENG-043 defines:

- Inspector identity
- Selected Resource identity
- Resource presentation model
- Resource identity details
- Resource classification
- Resource name
- Resource lifecycle
- Resource properties
- Resource metadata
- Semantic tags
- Categories
- Relationship summary
- Relationship navigation targets
- Selection handling
- Empty selection state
- Missing Resource state
- Loading state
- Error state
- Read-only behavior
- Application query boundary
- Workspace integration
- Future editing boundary
- Future 3D integration
- Future AI integration

---

# Non-Goals

ENG-043 does not implement:

- Resource creation
- Resource deletion
- Resource property editing
- Classification editing
- Lifecycle mutation
- Relationship mutation
- Geometry editing
- 3D rendering
- Gizmos
- Validation rule editing
- Agent execution
- Persistence
- Import / Export
- Collaboration
- Frontend framework selection
- Visual styling system

The Inspector is initially a read-oriented detail surface.

---

# Architectural Position

The Inspector operates above the ENG-039 Application Boundary and inside the
ENG-040 UI Application Shell.

The architectural flow is:

```text
Atlas Core
    ↓
ENG-039 Application Boundary
    ↓
Selected AtlasID
    ↓
Inspector Query
    ↓
Inspector Presentation Model
    ↓
Inspector Panel
    ↓
Atlas Workspace

Inspector Principle

The Inspector answers:

"What is this Resource?"

The Explorer answers:

"What exists inside this project?"

The Dashboard answers:

"What is the state of this project?"

The Inspector therefore operates at Resource detail level.

Canonical Resource Identity

The selected Resource must be identified by AtlasID.

Conceptually:

Explorer
    ↓
AtlasID
    ↓
Workspace Selection
    ↓
Inspector
    ↓
AtlasApplication
    ↓
AtlasResource

The Inspector must not use:

list position
Resource name
UI node ID
generated UI identity

as the canonical engineering identity.

Inspector Identity

The Inspector must have a stable UI/application identity.

Recommended identity:

inspector

This is UI/application identity.

It is not an AtlasID.

Inspector Presentation Model

The Inspector should expose a dedicated presentation representation.

Conceptually:

AtlasResource
    ↓
Inspector Query
    ↓
AtlasInspectorPresentation
    ↓
Inspector Panel

The presentation model must not be an AtlasResource.

Inspector Presentation Structure

A future-ready presentation model may contain:

AtlasInspectorPresentation
├── resource_id
├── name
├── classification
├── lifecycle
├── properties
├── metadata
├── tags
├── categories
└── relationships
Resource Identity

The Inspector must present the canonical Resource identity.

Potential information includes:

Resource ID
Resource Name

The Resource ID must come from the canonical Resource AtlasID.

Resource Name

The Inspector presents the Resource name.

The Inspector must not derive a replacement engineering name.

If the Resource has no name, the Inspector must preserve the distinction between:

Unnamed Resource

and:

Missing Resource
Classification

The Inspector must present the Resource's canonical Classification.

Potential information includes:

Classification ID
Classification Name
Classification Path
Classification Depth

Classification information must originate from the canonical AtlasClassification.

The Inspector must not create a second Classification hierarchy.

Lifecycle

The Inspector must present the current Resource lifecycle.

Potential lifecycle values are those defined by the canonical Atlas lifecycle
model.

The Inspector must not create a parallel lifecycle system.

Properties

The Inspector must present canonical Resource Properties.

Potential information includes:

Property ID
Property Name
Value
Data Type
Unit
Description
Required

Properties remain owned by the canonical AtlasResource.

The Inspector does not duplicate the Property model as engineering truth.

Metadata

The Inspector may present canonical Resource metadata.

Metadata is presentation of the current Resource state.

The Inspector must not introduce a second metadata source.

Semantic Tags

The Inspector may present attached semantic tags.

Potential information includes:

Tag ID
Tag Name
Description

The Inspector must consume the canonical Semantic Tag model.

Categories

The Inspector may present Resource Categories.

Potential information includes:

Category ID
Category Name
Description

Categories remain owned by the Resource model.

Relationships

The Inspector may present relationships involving the selected Resource.

Potential information includes:

Relationship ID
Relationship Type
Source Resource ID
Target Resource ID
Description

Relationship information must come from the canonical Project Graph.

The Inspector must not create a second graph.

Relationship Navigation

Relationship entries may provide navigation targets.

Conceptually:

Inspector
    ↓
Relationship
    ↓
Target AtlasID
    ↓
Workspace Selection
    ↓
Inspector refresh

This allows users to navigate through the engineering graph without the
Inspector owning the graph.

Selection Handling

The Inspector consumes the Workspace selection context.

Conceptually:

Workspace Selection
        ↓
AtlasID
        ↓
Inspector

The Inspector should support:

Selection Changed
Selection Cleared
Selection Replaced
Selection State

The Inspector should not maintain an independent engineering selection.

The canonical selected identity comes from the Workspace/UI selection model.

The Inspector may maintain transient presentation state derived from that
selection.

Empty Selection

When no Resource is selected, the Inspector must present a valid empty state.

Example:

No Resource Selected

This is valid UI state.

It is not an error.

Missing Resource

A selected AtlasID may become stale if the underlying Resource is removed.

The Inspector must distinguish:

No Resource Selected

from:

Resource Unavailable

The Inspector must not create a replacement Resource.

Loading State

The Inspector may expose transient loading state.

Example:

Loading Resource...

Loading state is UI/application state.

It must not be written into the canonical Resource.

Error State

The Inspector should distinguish explicit retrieval failure.

Potential failures include:

Application Query Failure
Resource Unavailable
Relationship Query Failure
Property Query Failure

The Inspector must not silently present partial or fabricated engineering data.

Read-Only Principle

ENG-043 is initially read-oriented.

Inspector operations must not:

Create Resources
Delete Resources
Modify Resources
Modify Properties
Modify Classification
Modify Lifecycle
Modify Metadata
Modify Tags
Modify Categories
Modify Relationships
Modify Project identity
Future Editing Boundary

Future versions may introduce Resource editing.

That editing capability must be explicit and command-driven.

Conceptually:

Inspector
    ↓
Application Command
    ↓
Atlas Core Mutation

The Inspector must not directly mutate Atlas Core objects merely because it
displays them.

Property Presentation

Properties should remain deterministic.

For equivalent Resource state, equivalent Inspector queries should produce
equivalent property presentation.

The Inspector should preserve canonical Property identity.

Property Ordering

The initial implementation should preserve canonical Resource Property
ordering where available.

Future versions may introduce explicit deterministic sorting.

The Inspector must not silently redefine engineering semantics through
presentation ordering.

Metadata Presentation

Metadata keys and values should remain derived from canonical Resource state.

The Inspector must not normalize, reinterpret, or invent engineering metadata
without an explicit specification.

Tag Presentation

Tags should preserve canonical tag identity.

The Inspector may present Tag name and description.

Tag presentation must remain read-only in ENG-043.

Category Presentation

Categories should preserve canonical Category identity.

Category presentation must remain read-only in ENG-043.

Lifecycle Presentation

The Inspector must present the canonical lifecycle state.

It must not infer an alternative engineering lifecycle from UI state.

Relationship Presentation

Relationship entries should preserve:

Relationship ID
Relationship Type
Source
Target
Description

Endpoint Resource identity should use AtlasID.

Relationship Direction

The Inspector should preserve relationship direction.

A Relationship should not be presented as directionless merely because it is
shown in the context of a selected Resource.

For example:

Selected Resource
    ↓
supports
    ↓
Target Resource

must remain distinguishable from:

Selected Resource
    ↑
supported by
    ↑
Source Resource
Search / Navigation

The Inspector does not implement project-wide search.

Search remains an Explorer responsibility.

The Inspector may provide local navigation among:

Selected Resource
Relationships
Referenced Resources
Explorer Relationship

The Explorer selects a Resource.

The Inspector exposes its detailed state.

Explorer
    ↓
AtlasID
    ↓
Inspector

This is the primary ENG-042 → ENG-043 interaction.

Dashboard Relationship

The Dashboard remains project-level.

The Inspector remains Resource-level.

Dashboard
    ↓
Project summary
Inspector
    ↓
Selected Resource detail

The Dashboard and Inspector must not duplicate each other's domain
responsibilities.

3D Workspace Relationship

The Inspector may provide navigation to a future 3D View.

Conceptually:

Inspector
    ↓
Selected AtlasID
    ↓
3D View Focus

The Inspector does not implement 3D rendering.

Application Boundary

Inspector queries must operate through the ENG-039 Application Boundary.

Conceptually:

Inspector
    ↓
AtlasQuery
    ↓
AtlasApplication
    ↓
Atlas Core

The Inspector should not bypass the Application Boundary with independent
engineering logic.

Inspector Query

ENG-043 may introduce an Inspector-specific query.

Potential operation:

GetResourceDetails

The implementation may use an equivalent query structure provided the
Application Boundary remains intact.

Resource Lookup

The Inspector must resolve a selected AtlasID through canonical Atlas
application/project state.

A missing ID must produce an explicit unavailable state.

The Inspector must never manufacture a Resource to satisfy a missing lookup.

Presentation Copying

The Inspector may create a lightweight presentation representation.

Example:

AtlasResource
    ↓
Inspector Presentation

The reverse must never occur:

Inspector Presentation
    ↓
becomes AtlasResource
No Second Resource Model

The Inspector must not become:

InspectorResource

as an independent engineering model.

Presentation types are allowed.

A second engineering model is not.

No Second Graph

The Inspector must not become:

InspectorGraph

Relationships remain owned by the canonical Project Graph.

No Second Registry

The Inspector must not create a Resource Registry for inspected Resources.

Workspace Integration

The Inspector is hosted by the ENG-040 Workspace.

Conceptually:

AtlasWorkspace
    ↓
Inspector Panel
    ↓
Inspector Presentation

The Workspace remains responsible for:

Panel registration
Visibility
Active panel
Selection context
Workspace lifecycle
Inspector Panel Identity

Recommended panel identity:

inspector

This is UI/application identity.

It must not be confused with an Atlas Resource identity.

State Separation

Inspector UI state may include:

Selected Resource ID
Expanded Sections
Active Section
Loading
Error
Display Preferences

These remain UI/application state.

Engineering truth remains in Atlas Core.

Large Resource Compatibility

The Inspector must remain compatible with Resources that contain:

Many properties
Many metadata entries
Many tags
Many categories
Many relationships

Future implementations may use:

Lazy Sections
Paginated Relationships
Incremental Property Loading
Caching

without changing the canonical model.

Determinism

For unchanged Atlas Resource state, equivalent Inspector queries should produce
equivalent presentation.

Determinism is important for:

Testing
UI consistency
Reproducibility
Change detection
Caching
Error Boundaries

The Inspector must preserve the distinction between:

No Selection
Loading
Resource Unavailable
Query Error
Valid Resource

These are presentation/application states.

They must not be encoded into the engineering Resource as fake lifecycle or
status values.

AI Boundary

Future AI capabilities may assist with Resource interpretation.

Examples:

Explain this Resource
Summarize its properties
Identify unusual relationships
Suggest validation checks

AI-generated interpretation must remain distinguishable from canonical
engineering facts.

The Inspector must not silently promote AI output into engineering truth.

Agent Boundary

The Inspector does not execute Agents as part of normal presentation.

Future actions may invoke application-level Agent operations.

Agent execution remains owned by the Agent Runtime and orchestration layer.

Persistence Boundary

The Inspector does not implement:

JSON serialization
Save
Load
Filesystem persistence

Those responsibilities remain with ENG-036 and ENG-037.

Exchange Boundary

The Inspector does not implement:

IFC import
CAD import
Revit import
Export

Exchange remains governed by ENG-038.

Testing Strategy

ENG-043 tests should verify:

Inspector identity
Inspector presentation model
Selected AtlasID
Resource identity
Resource name
Classification
Classification path
Lifecycle
Properties
Metadata
Tags
Categories
Relationships
Relationship direction
Relationship targets
Empty selection
Missing Resource
Loading state
Error state
Selection handoff
Workspace integration
Application query boundary
Read-only behavior
Deterministic presentation
No second Resource model
No second Registry
No second Graph
Persistence isolation
Exchange isolation
Agent isolation
AI boundary
Public exports

Visual rendering tests belong to the eventual frontend implementation.

Acceptance Criteria

ENG-043 is complete when:

An Inspector capability exists within the Atlas UI architecture.
The Inspector is hosted by the ENG-040 Workspace.
Inspector data is obtained through the ENG-039 Application Boundary.
The Inspector exposes a stable UI/application identity.
The Inspector consumes AtlasID selection.
The Inspector can present Resource identity.
The Inspector can present Resource name.
The Inspector can present Classification.
The Inspector can present Lifecycle.
The Inspector can present Properties.
The Inspector can present Metadata.
The Inspector can present Semantic Tags.
The Inspector can present Categories.
The Inspector can present Relationship context.
Relationship direction is preserved.
Relationship targets remain AtlasID-based.
Empty selection is supported.
Missing Resources are handled explicitly.
Loading and error states are distinguishable.
Inspector navigation is read-only with respect to engineering state.
The Inspector does not own a second Resource model.
The Inspector does not own a Resource Registry.
The Inspector does not own a Resource Graph.
Persistence remains outside the Inspector.
Import/export remains outside the Inspector.
Agent execution remains outside the Inspector.
AI-generated interpretation remains distinct from canonical engineering truth.
Inspector presentation remains independent from frontend technology.
Existing Atlas Core behavior remains unchanged.
Relationship to ENG-042

ENG-042 establishes Resource navigation and selection.

ENG-043 consumes that selection and presents detailed Resource state.

Explorer
    ↓
AtlasID
    ↓
Workspace Selection
    ↓
Inspector

This establishes the primary navigation-to-detail workflow in Atlas.

Relationship to Future Editing

ENG-043 is initially read-only.

Future Resource editing should be introduced through explicit application
commands and mutation contracts rather than adding direct mutations to the
Inspector.

Relationship to Future 3D Workspace

The Inspector may provide actions that focus the selected Resource in the
future 3D View.

Inspector
    ↓
AtlasID
    ↓
3D View

The 3D View remains a separate presentation capability.

Architectural Conclusion

ENG-043 establishes the Atlas Inspector as the Resource-level detail surface.

The architectural flow is:

                     Atlas Core
                         │
                         ▼
               ENG-039 Application
                     Boundary
                         │
                         ▼
                  Workspace Selection
                         │
                         ▼
                    AtlasID
                         │
                         ▼
                Inspector Query
                         │
                         ▼
             Inspector Presentation
                         │
                         ▼
                 Inspector Panel

The Inspector completes the initial navigation chain:

Dashboard
    ↓
Project awareness


Explorer
    ↓
Resource navigation


Inspector
    ↓
Resource detail

Together, these surfaces provide the first coherent human-facing path through
the Atlas engineering model while preserving the canonical Resource,
Registry, Relationship, Semantics, Validation, and Agent architecture.
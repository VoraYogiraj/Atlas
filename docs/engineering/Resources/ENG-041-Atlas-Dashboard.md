# ENG-041 — Atlas Dashboard

**Document ID:** ENG-041  
**Title:** Atlas Dashboard  
**Version:** 0.1.0  
**Status:** Complete  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas Application / Presentation layer

---

# Purpose

ENG-041 defines the Atlas Dashboard as the project-level overview surface
within the Atlas UI Application Shell.

The Dashboard provides a high-level representation of the current Atlas
Project without becoming a second project model or engineering database.

The Dashboard helps users understand the current state of an Atlas Project
before navigating into detailed engineering structures.

---

# Scope

ENG-041 defines:

- Dashboard identity
- Dashboard presentation model
- Project overview
- Project identity summary
- Resource counts
- Classification summaries
- Relationship summaries
- Validation summaries
- Agent/activity summaries
- Project status
- Dashboard refresh behavior
- Dashboard read boundary
- Dashboard/Core separation
- Dashboard/Workspace integration
- Future Dashboard extensibility

---

# Non-Goals

ENG-041 does not implement:

- Full Explorer functionality
- Full Inspector functionality
- Full Validation Panel
- Full Agent Panel
- 3D rendering
- Geometry editing
- BIM visualization
- Knowledge Graph visualization
- Collaboration
- Project editing
- Resource creation
- Resource deletion
- Resource mutation
- Persistence implementation
- Import/export implementation
- Frontend framework selection
- Visual styling system

The Dashboard is primarily a read-oriented project overview.

---

# Architectural Position

ENG-041 operates above ENG-039 and inside the ENG-040 UI Application Shell.

The architectural flow is:

```text
Atlas Core
    ↓
ENG-039 Application Boundary
    ↓
Dashboard Queries
    ↓
Dashboard Presentation Model
    ↓
Dashboard Panel

The Dashboard does not directly manipulate Atlas Core objects.

Dashboard Principle

The Dashboard presents Atlas Project state.

It does not own Atlas Project state.

The canonical engineering state remains in Atlas Core.

Dashboard
    ↓
Presentation
    ↓
Atlas Application
    ↓
Atlas Core

The Dashboard must remain replaceable without changing the canonical Atlas
model.

Dashboard Responsibilities

The Dashboard provides a project-level summary of:

Project Identity
Resource Counts
Classification Summary
Relationship Summary
Validation Summary
Agent / Activity Summary
Project Status

These summaries should be derived from canonical Atlas state.

Project Identity

The Dashboard may present:

Project ID
Project name
Project metadata summary
Project lifecycle/status information where applicable

Example:

Project
Sample Building


Project ID
550e8400-e29b-41d4-a716-446655440000

Project identity must come from the canonical AtlasProject.

The Dashboard must not generate a replacement Project identity.

Resource Summary

The Dashboard provides a high-level summary of Resources.

Potential values include:

Total Resources
Active Resources
Archived Resources
Deleted Resources
Resources by Classification

Example:

Resources


Total: 128
Active: 117
Archived: 9
Deleted: 2

Resource counts must be derived from Atlas Core state.

The Dashboard must not maintain an independent Resource count database.

Classification Summary

The Dashboard may summarize the distribution of Resources by Classification.

Example:

Classification Summary


Walls       32
Doors       18
Windows     24
Rooms       15
Columns     12

Classification information must come from the Atlas Classification Registry
and Resource model.

The Dashboard must not create a second classification hierarchy.

Relationship Summary

The Dashboard may summarize relationships within the Project.

Potential information includes:

Total Relationships
Relationships by Type
Connected Resources
Unconnected Resources

Example:

Relationships


Total: 247


contains       82
connects       64
supports       51
references     50

Relationship summaries must derive from the canonical Project Graph.

The Dashboard must not create a second relationship graph.

Validation Summary

The Dashboard may present a high-level validation summary.

Potential values include:

Validation Status
Total Findings
Errors
Warnings
Passed Checks

Example:

Validation


Status: Attention Required


Errors:   3
Warnings: 7
Passed:   118

Validation remains an Atlas Core capability.

The Dashboard must consume validation results.

It must not reimplement validation rules.

Agent / Activity Summary

The Dashboard may present high-level Agent or application activity.

Potential information includes:

Active Agents
Completed Operations
Failed Operations
Recent Agent Activity
Last Agent Operation

Example:

Agent Activity


Active: 2
Completed: 37
Failed: 1

The Dashboard does not implement Agent reasoning.

Agent execution remains governed by the existing Agent Runtime,
Orchestrator, and Coordination architecture.

Project Status

The Dashboard may present a high-level Project status.

Status may be derived from existing Atlas state and application-level
information.

Possible values may include:

Ready
Active
Attention Required
Validation Required
Loading
Processing

The exact status model may be expanded by future specifications.

The Dashboard must not invent engineering status unsupported by Atlas Core.

Dashboard Presentation Model

The Dashboard should use a dedicated presentation representation.

Conceptually:

AtlasProject
      ↓
Dashboard Query
      ↓
AtlasDashboardPresentation
      ↓
Dashboard Panel

The presentation model is not an AtlasProject.

It should contain only information required to present the project overview.

Dashboard Presentation Model Structure

A future-ready Dashboard presentation model may contain:

Project Identity
Project Name
Resource Summary
Classification Summary
Relationship Summary
Validation Summary
Agent Summary
Project Status

Conceptual example:

AtlasDashboardPresentation
├── project_id
├── project_name
├── resource_summary
├── classification_summary
├── relationship_summary
├── validation_summary
├── agent_summary
└── project_status
Resource Summary Model

A Resource summary may contain:

Total
Active
Archived
Deleted
By Classification

The summary is derived data.

It must not become a second Resource Registry.

Classification Summary Model

A Classification summary may contain:

Classification ID
Classification Name
Resource Count

This remains presentation information.

Classification hierarchy remains owned by Atlas Core.

Relationship Summary Model

A Relationship summary may contain:

Relationship Type
Relationship Count

The relationship data remains owned by the Project Graph.

Validation Summary Model

A Validation summary may contain:

Overall Status
Error Count
Warning Count
Passed Count

The validation engine remains responsible for producing actual validation
results.

Agent Summary Model

An Agent summary may contain:

Active Count
Completed Count
Failed Count
Recent Activity

The Agent Runtime remains responsible for Agent execution state.

Dashboard Read Boundary

The Dashboard must retrieve engineering information through the ENG-039
Application Boundary.

Conceptually:

Dashboard
   ↓
AtlasQuery
   ↓
AtlasApplication
   ↓
Atlas Core

The Dashboard must not directly traverse internal Atlas infrastructure unless
such access is explicitly exposed through the application boundary.

Dashboard Query

ENG-041 may introduce a dashboard-specific query such as:

GetDashboard

or an equivalent application query.

The query should produce Dashboard presentation data rather than expose
internal domain structures directly to the UI.

Read-Only Principle

Dashboard rendering should not mutate engineering state.

Reading Dashboard information must not:

Create Resources
Modify Resources
Delete Resources
Modify Relationships
Change Classification
Change Lifecycle
Change Validation Rules
Change Project identity

The Dashboard is primarily a read surface.

Refresh

The Dashboard should support refreshing its presentation state.

Conceptually:

Atlas State
    ↓
Dashboard Query
    ↓
New Dashboard Presentation
    ↓
Dashboard Refresh

Refreshing the Dashboard must not mutate Atlas engineering state.

Consistency

The Dashboard should reflect the latest successfully retrieved Atlas state.

When underlying engineering state changes:

Atlas Core
    ↓
Application Update
    ↓
Dashboard Query
    ↓
Dashboard Presentation
    ↓
UI Refresh

The Dashboard must not rely on independently maintained engineering data.

Dashboard and Workspace

The Dashboard is hosted within the ENG-040 Workspace.

Conceptually:

AtlasWorkspace
      ↓
Dashboard Panel
      ↓
Dashboard Presentation

The Dashboard should therefore behave as a Workspace presentation surface.

The Workspace remains responsible for panel registration and visibility.

Dashboard Panel Identity

The Dashboard Panel should use a stable presentation identity.

Recommended identity:

dashboard

The identity is UI/application identity.

It must not be confused with an Atlas Resource or Project ID.

Dashboard and Selection

The Dashboard may display summaries or navigation targets.

A Dashboard interaction that selects a Resource should use the ENG-039
identity-based selection model.

Conceptually:

Dashboard Interaction
      ↓
AtlasID
      ↓
Workspace Selection
      ↓
Explorer / Inspector / Future 3D View

The Dashboard must not store a copied canonical Resource as selection state.

Dashboard Navigation

The Dashboard may provide navigation actions such as:

Open Explorer
Open Inspector
Open Validation
Open Agents
Open Relationships
Open 3D Workspace

These actions are presentation/application operations.

They must not bypass the Workspace or Application boundaries.

Dashboard and Agents

Agent activity may be represented on the Dashboard.

For example:

Active Agents
Recent Agent Operations
Completed Operations
Failures

The Dashboard does not execute Agents directly as part of rendering.

Agent execution remains an application/core concern.

Dashboard and Validation

The Dashboard may show validation health.

Example:

Validation Status: Attention Required
Errors: 3
Warnings: 7

Detailed validation remains outside the Dashboard.

A user may navigate from the Dashboard to a future Validation Panel.

Dashboard and Persistence

The Dashboard may display project state after loading.

The Dashboard itself must not implement:

JSON serialization
File persistence
Save
Load

Those responsibilities remain with ENG-036 and ENG-037.

Dashboard and Exchange

The Dashboard may expose navigation to Import or Export actions.

Import/export logic remains governed by ENG-038.

The Dashboard is not an importer or exporter.

Dashboard and 3D Workspace

The Dashboard may provide a navigation entry into a future 3D Workspace.

The architecture remains:

Dashboard
    ↓
Workspace View Selection
    ↓
3D View

The Dashboard does not implement 3D rendering.

Dashboard State

The Dashboard may maintain transient presentation state such as:

Is Loading
Last Refresh
Current Filter
Expanded Summary
Selected Summary Item
Display Preferences

This is UI state.

It must remain separate from engineering state.

Dashboard Caching

Future implementations may cache Dashboard summaries for performance.

Any cache must remain a derived presentation cache.

The cache must never become the canonical source of engineering truth.

Conceptually:

Atlas Core
    ↓
Dashboard Query
    ↓
Presentation Cache
    ↓
Dashboard
Error Handling

Dashboard retrieval failures must be explicit.

Potential failures include:

Project Not Available
Application Query Failure
Validation Data Unavailable
Agent Data Unavailable
Project Loading

The Dashboard should distinguish between:

Loading
Unavailable
Error
Valid Empty Result

A failure to retrieve a summary must not silently produce false engineering
information.

Empty Project

The Dashboard must support an empty Atlas Project.

For example:

Resources: 0
Relationships: 0
Validation: No findings
Agents: No activity

An empty project is valid UI state unless Atlas Core indicates otherwise.

Large Project Compatibility

The Dashboard should remain compatible with large engineering projects.

The presentation layer should avoid unnecessarily copying entire Resource
collections into the Dashboard.

Summaries should be calculated through efficient application queries.

Future implementations may use:

Aggregated Queries
Indexes
Caching
Incremental Updates
Background Computation

without changing the architectural contract.

Determinism

For an unchanged Atlas Project, equivalent Dashboard queries should produce
equivalent summary information.

This is important for:

Testing
UI consistency
Caching
Change detection
Reproducibility
Technology Independence

ENG-041 remains independent from:

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

The Dashboard specification defines behavior and architecture, not rendering
technology.

Domain Independence

The dependency direction must remain:

Dashboard
    ↓
ENG-039 Application Boundary
    ↓
Atlas Core

The following must never occur:

Atlas Core
    ↓
Dashboard UI

This preserves UI independence.

Future Extensibility

The Dashboard may eventually expose additional project intelligence:

Project Health
Engineering KPIs
Recent Changes
Impact Summary
Issue Trends
Approval Status
Construction Progress
Material Summary
Document Summary
AI Insights
Risk Indicators

These should be added as presentation/application capabilities without
replacing the canonical Atlas model.

Future AI Insights

Future Atlas versions may generate AI-assisted Dashboard insights.

Examples:

Potential anomalies
Validation trends
High-risk resources
Recent design changes
Possible relationship inconsistencies
Recommended review areas

AI-generated information must remain distinguishable from canonical
engineering facts.

The Dashboard must not silently treat AI-generated recommendations as
validated engineering truth.

Future Collaboration

Future collaboration features may display:

Recent User Activity
Review Status
Pending Decisions
Approvals
Agent Activity
Comments

These belong to future collaboration/application capabilities.

They do not change the core Dashboard boundary.

Testing Strategy

ENG-041 tests should verify:

Dashboard identity
Dashboard presentation model
Project identity summary
Resource counts
Classification summary
Relationship summary
Validation summary
Agent summary
Project status
Read-only behavior
Application query boundary
Workspace integration
Selection identity
UI state separation
Empty project behavior
Deterministic summary behavior
Error handling
Core independence
Persistence independence
Exchange independence

Visual rendering tests belong to the eventual frontend implementation.

Acceptance Criteria

ENG-041 is complete when:

A Dashboard capability exists within the Atlas UI architecture.
The Dashboard is hosted by the ENG-040 Workspace.
Dashboard data is obtained through the ENG-039 Application Boundary.
The Dashboard does not own an AtlasProject.
The Dashboard does not own a Resource Registry.
The Dashboard does not own a Resource Graph.
The Dashboard does not implement engineering validation.
The Dashboard does not implement Agent reasoning.
Project identity can be presented.
Resource counts can be presented.
Classification summaries can be presented.
Relationship summaries can be presented.
Validation summaries can be presented.
Agent/activity summaries can be presented.
Project status can be presented.
Dashboard rendering is read-only with respect to engineering state.
Dashboard refresh does not mutate engineering state.
Empty Projects are supported.
Dashboard failures are explicit.
Dashboard presentation remains separate from canonical Atlas objects.
Dashboard selection remains AtlasID-based.
Dashboard remains compatible with future 3D Workspace navigation.
Dashboard remains compatible with future AI and collaboration capabilities.
The implementation remains independent from frontend technology.
Existing Atlas Core behavior remains unchanged.
Relationship to ENG-039

ENG-039 establishes:

UI
 ↓
Application Boundary
 ↓
Atlas Core

ENG-041 applies that boundary to a concrete project-level presentation
capability.

Dashboard
    ↓
ENG-039
    ↓
Atlas Core
Relationship to ENG-040

ENG-040 establishes the UI Application Shell.

ENG-041 occupies that shell as the first concrete project-level UI
capability.

AtlasWorkspace
      ↓
Dashboard Panel
      ↓
Dashboard Presentation
Relationship to Future Explorer

The Dashboard is a project overview.

The future Explorer will provide detailed navigation through Atlas structures.

The intended distinction is:

Dashboard
    ↓
"What is the state of this project?"

versus:

Explorer
    ↓
"What exists inside this project?"

The two capabilities should share application contracts without becoming
duplicated data stores.

Relationship to Future Inspector

The Dashboard provides summary information.

The Inspector provides detailed information for a selected Resource.

Dashboard
    ↓
Project-level summary

versus:

Inspector
    ↓
Resource-level detail
Relationship to Future 3D Workspace

The Dashboard provides project-level navigation into the future 3D Workspace.

The 3D Workspace remains a separate presentation capability.

Architectural Conclusion

ENG-041 establishes the Atlas Dashboard as a project-level, read-oriented
presentation capability within the Atlas UI Application Shell.

The core architecture is:

                    Atlas Core
                        │
                        ▼
              ENG-039 Application
                    Boundary
                        │
                        ▼
                Dashboard Query
                        │
                        ▼
           Dashboard Presentation
                        │
                        ▼
                Dashboard Panel
                        │
                        ▼
                 Atlas Workspace

The Dashboard provides visibility into Atlas engineering state without owning
that state.

It is therefore a presentation layer over the canonical Atlas model rather
than a competing project model.

The Dashboard becomes the first concrete project-level window into Atlas,
while preserving the architectural path toward Explorer, Inspector, 3D,
AI-assisted workflows, collaboration, and Engineering Intelligence.
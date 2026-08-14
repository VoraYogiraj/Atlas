# ENG-042 — Atlas Explorer

**Document ID:** ENG-042  
**Title:** Atlas Explorer  
**Version:** 0.1.0  
**Status:** Proposed  
**Depends On:** ENG-039 — Atlas UI Architecture, ENG-040 — Atlas UI Application Shell, ENG-041 — Atlas Dashboard  
**Phase:** Phase 9 — User Interface  
**Implementation:** Atlas Application / Presentation layer

---

# Purpose

ENG-042 defines the Atlas Explorer as the primary navigation surface for
discovering and navigating engineering Resources and their structural context
inside an Atlas Project.

The Explorer provides users with a structured view of what exists inside the
current project.

The Explorer operates over the canonical Atlas Project and does not become a
second Resource Registry, Classification Registry, or Relationship Graph.

---

# Scope

ENG-042 defines:

- Explorer identity
- Explorer presentation model
- Resource navigation
- Classification navigation
- Resource grouping
- Relationship visibility
- Resource selection
- Selection handoff
- Search
- Filtering
- Expansion and collapse state
- Ordering
- Empty states
- Application query boundary
- Workspace integration
- Read-only behavior
- Large-project considerations
- Future 3D navigation
- Future Inspector integration

---

# Non-Goals

ENG-042 does not implement:

- Resource editing
- Resource creation
- Resource deletion
- Property editing
- Full Inspector functionality
- 3D rendering
- Geometry editing
- Gizmos
- BIM visualization
- Validation rule editing
- Agent execution
- Persistence
- Import / Export
- Collaboration
- Frontend framework selection
- Visual styling system

The Explorer is primarily a navigation and discovery surface.

---

# Architectural Position

The Explorer operates above the ENG-039 Application Boundary and inside the
ENG-040 UI Application Shell.

The architectural flow is:

```text
Atlas Core
    ↓
ENG-039 Application Boundary
    ↓
Explorer Queries
    ↓
Explorer Presentation Model
    ↓
Explorer Panel
    ↓
Atlas Workspace

The Explorer does not directly own Atlas engineering state.

Explorer Principle

The Explorer answers:

"What exists inside this project?"

The Dashboard answers:

"What is the state of this project?"

The Explorer provides navigation and discovery while the Dashboard provides
project-level overview.

Canonical Data Sources

Explorer information must come from canonical Atlas structures:

AtlasProject
    ├── Resource Registry
    ├── Classification Registry
    ├── Classification Hierarchy
    └── Resource Graph

The Explorer must not maintain independent copies of those structures as
engineering truth.

Explorer Identity

The Explorer must have a stable UI/application identity.

Recommended identity:

explorer

This identity is not an AtlasID.

It identifies the Explorer presentation capability.

Explorer Presentation Model

The Explorer should use dedicated presentation representations.

Conceptually:

AtlasProject
    ↓
Explorer Query
    ↓
Explorer Presentation Model
    ↓
Explorer Panel

The presentation model must not be an AtlasProject.

Explorer Node

The Explorer should expose a generic presentation node.

Conceptually:

AtlasExplorerNode
├── node_id
├── node_type
├── label
├── resource_id
├── classification_id
├── parent_id
├── children
└── expandable

Not every field is required for every node type.

Node Types

The Explorer may support node types such as:

Project
Classification
Resource
Relationship Group

Additional node types may be introduced by future specifications.

Project Node

The root Explorer node represents the current Atlas Project.

Example:

Sample Building

The Project node represents navigation context.

It must not become a replacement Project object.

Classification Nodes

The Explorer may represent classifications as hierarchical navigation nodes.

Example:

Building
├── Architectural
│   ├── Wall
│   ├── Door
│   └── Window
├── Structural
│   ├── Column
│   └── Beam
└── MEP
    ├── Pipe
    └── Equipment

Classification hierarchy must come from the canonical Atlas Classification
Hierarchy.

The Explorer must not create a second classification hierarchy.

Resource Nodes

Resource nodes represent canonical Atlas Resources.

Example:

Wall
├── External Wall 001
├── External Wall 002
└── Internal Wall 001

Each Resource node should retain the Resource's canonical AtlasID.

The Explorer must not replace AtlasID with a UI-generated Resource identity.

Resource Identity

Explorer selection and navigation must identify Resources by AtlasID.

Conceptually:

Explorer Resource Node
        ↓
     AtlasID
        ↓
Workspace Selection

The Explorer must not store a copied canonical Resource as its primary identity.

Resource Labels

Resource labels should be derived from canonical Resource state.

A label may use:

Resource Name
Classification Name
Other future presentation metadata

The Explorer must not invent engineering meaning merely to improve display
labels.

Resource Grouping

The Explorer should support grouping Resources by canonical engineering
structures.

Initial grouping may include:

Classification

Future grouping may include:

Lifecycle
Category
Location
Discipline
System
Phase

Future grouping must be based on actual Atlas semantics rather than UI-only
invented engineering structures.

Relationship Visibility

The Explorer may expose relationship context.

Example:

External Wall 001
├── Relationships
│   ├── connects → Door 001
│   ├── bounds → Room 101
│   └── supports → Beam 007

Relationship information must come from the canonical Atlas Resource Graph.

The Explorer must not maintain a second graph.

Relationship Groups

Relationships may be represented as grouped presentation nodes.

Conceptually:

Resource
└── Relationships
    ├── contains
    ├── connects
    ├── supports
    └── references

The grouping is presentation structure only.

Search

The Explorer should support searching navigable project entities.

Initial search may include:

Resource Name
Classification Name
Resource ID

Future search may include:

Tags
Categories
Properties
Metadata
Relationship Types
Semantic Properties

Search must operate against canonical Atlas information.

Search Semantics

Search must not modify Atlas engineering state.

Search produces presentation/query results.

Conceptually:

User Input
    ↓
Explorer Query
    ↓
Atlas Application
    ↓
Matching Atlas IDs
    ↓
Explorer Presentation
Filtering

The Explorer should support filtering navigable entities.

Initial filter capabilities may include:

Classification
Lifecycle
Resource Type

Future filters may include:

Category
Tag
Discipline
Location
Validation Status
Relationship Type

Filters are presentation/query state.

They must not modify canonical Atlas state.

Expansion and Collapse

Explorer nodes may have transient expanded/collapsed state.

Example:

expanded = true

This is UI state.

It must remain separate from Atlas engineering state.

Expansion State

Expansion state may be represented by node identity.

Conceptually:

Expanded Node IDs
    ↓
UI State

Resource or Classification objects must not contain UI expansion state merely
to support the Explorer.

Selection

Selecting an Explorer Resource must use the ENG-039 selection model.

Conceptually:

Explorer Click
    ↓
AtlasID
    ↓
AtlasResourceSelection
    ↓
Workspace Selection

The selected identity can then be consumed by:

Inspector
3D View
Validation
Relationship View
Future AI tools
Selection Handoff

The Explorer should support handoff to future UI surfaces.

Example:

Explorer
   ↓
Select Resource
   ↓
Workspace Selection
   ├── Inspector
   ├── 3D View
   ├── Validation
   └── Relationship View

The Explorer must not directly own those future surfaces.

Inspector Relationship

The Explorer and Inspector have distinct responsibilities.

Explorer:

"What exists?"

Inspector:

"What are the details of this selected Resource?"

The Explorer should therefore provide selection context for the future
Inspector.

3D Workspace Relationship

The Explorer may provide navigation into the future 3D Workspace.

Example:

Select Resource
    ↓
Workspace Selection
    ↓
3D View focuses selected Resource

The Explorer does not implement 3D rendering.

Application Boundary

Explorer queries must operate through the ENG-039 Application Boundary.

Conceptually:

Explorer
    ↓
AtlasQuery
    ↓
AtlasApplication
    ↓
Atlas Core

The Explorer should not bypass the application boundary by directly embedding
independent engineering logic.

Explorer Query

ENG-042 may introduce Explorer-specific queries.

Potential operations include:

GetExplorerTree
SearchExplorer
FilterExplorer
GetResourceNode
GetResourceRelationships

Exact query names may be refined during implementation provided the architectural
boundary remains unchanged.

Read-Only Principle

Explorer navigation must not mutate engineering state.

Explorer operations must not:

Create Resources
Delete Resources
Modify Resources
Modify Properties
Modify Relationships
Modify Classification
Modify Lifecycle
Modify Validation Rules
Modify Project identity
Empty Project

The Explorer must support an empty Atlas Project.

Example:

Sample Building


No Resources

A valid empty project is not an error.

The presentation should distinguish:

Empty

from:

Unavailable
Error
Loading
Missing Resource

A Resource referenced by a stale UI state may no longer exist.

The Explorer must handle this explicitly.

Possible result:

Resource unavailable

The Explorer must not invent a replacement Resource.

Loading State

The Explorer may expose transient loading state.

Example:

Loading project structure...

Loading is UI state.

It must not be written into Atlas engineering Resources.

Error Handling

Explorer retrieval failures must be explicit.

Potential failures include:

Project Unavailable
Application Query Failure
Resource Unavailable
Classification Unavailable
Search Failure
Relationship Query Failure

The Explorer must distinguish:

Loading
Empty
Unavailable
Error
Valid Results
Deterministic Ordering

For unchanged Atlas Project state, Explorer results should be deterministic.

Equivalent Explorer queries should produce equivalent ordering.

Stable ordering is important for:

Testing
UI consistency
Search
Selection
Change detection
Reproducibility

The Explorer should prefer canonical Registry order unless a query explicitly
requests another deterministic ordering.

Resource Registry Order

The existing Atlas Resource Registry defines canonical Resource registration
order.

The Explorer should preserve that ordering where no explicit sorting or
grouping has been requested.

The Explorer must not silently impose a different engineering ordering.

Search Ordering

Search results should use deterministic ordering.

A future search implementation may use:

Exact match
Prefix match
Contains match

but must provide stable results for equivalent inputs.

Classification Ordering

Classification navigation should follow the canonical Classification
Hierarchy and deterministic child ordering.

The Explorer must not reconstruct hierarchy independently.

Relationship Ordering

Relationship presentation should preserve canonical graph/query ordering where
possible.

The Explorer must not reorder relationships in a way that changes engineering
meaning.

Explorer State

The Explorer may maintain transient UI state such as:

Expanded nodes
Selected node
Search text
Active filters
Current root
Scroll position
Sort mode

This is UI state.

It must remain separate from Atlas engineering state.

Explorer State and AtlasID

Resource-related UI state should use stable AtlasID values.

Example:

selected_resource_id: AtlasID | None
expanded_resource_ids: tuple[AtlasID, ...]

The Explorer must not use transient list positions as engineering identity.

Large Project Compatibility

The Explorer must be designed for potentially large engineering projects.

It should avoid unnecessarily materializing every Resource into heavyweight UI
objects.

Future implementations may introduce:

Lazy Loading
Pagination
Virtualized Lists
Incremental Queries
Search Indexes
Caching
Background Queries

These are implementation strategies and must not change the canonical model.

Presentation vs Canonical Model

The Explorer presentation layer may transform canonical Atlas objects into
lightweight UI representations.

Example:

AtlasResource
    ↓
Explorer Resource Node

The reverse must not occur:

Explorer Resource Node
    ↓
becomes AtlasResource

The canonical Resource remains owned by Atlas Core.

No Second Registry

The Explorer must not become:

ExplorerResourceRegistry

containing independent engineering Resources.

A presentation index or cache may exist later for performance, but it must
remain derived state.

No Second Graph

The Explorer must not become:

ExplorerGraph

The canonical relationship graph remains owned by Atlas Project.

No Second Classification Hierarchy

The Explorer may display a tree.

That tree is a presentation of the canonical classification hierarchy.

It must not become another classification system.

Dashboard Relationship

The Dashboard and Explorer serve complementary purposes.

Dashboard
    ↓
Project-level summary
Explorer
    ↓
Project-level navigation

The Dashboard may navigate to the Explorer.

The Explorer may navigate back to the Dashboard.

Neither surface owns the other.

Workspace Integration

The Explorer is hosted by the ENG-040 Workspace.

Conceptually:

AtlasWorkspace
    ↓
Explorer Panel
    ↓
Explorer Presentation

The Workspace remains responsible for:

Panel registration
Panel visibility
Active panel
Selection context
Workspace lifecycle
Explorer Panel Identity

Recommended panel identity:

explorer

This is UI/application identity.

It must not be confused with an Atlas Resource ID.

Future Toolbar Integration

The Explorer may eventually receive commands from the Toolbar.

Examples:

Expand All
Collapse All
Refresh
Search
Filter
Clear Filter

Toolbar execution remains an application command concern.

Explorer should not implement a separate command system.

Persistence Boundary

The Explorer does not implement:

JSON serialization
Save
Load
File persistence

Those responsibilities remain with ENG-036 and ENG-037.

Exchange Boundary

The Explorer does not implement:

IFC import
CAD import
Revit import
Export

Exchange remains governed by ENG-038.

Agent Boundary

The Explorer does not execute Agents directly.

Future UI actions may invoke application-level Agent operations, but Agent
execution remains owned by the existing Agent Runtime and orchestration
architecture.

AI Boundary

Future AI capabilities may help users search or navigate the Explorer.

Examples:

"Show all external walls"
"Find rooms connected to Stair 01"
"Show unclassified resources"

AI results must still resolve to canonical Atlas identities and must not silently
create engineering truth.

Future Semantic Search

Future Atlas versions may introduce semantic or natural-language search.

The Explorer may become a presentation surface for that functionality.

The underlying semantic reasoning remains outside the Explorer itself.

Future Collaboration

Future collaboration may add:

Recently Viewed
Recently Changed
Assigned
Reviewed
Commented

These are future application capabilities.

They do not alter the Explorer's canonical-data boundary.

Testing Strategy

ENG-042 tests should verify:

Explorer identity
Explorer presentation model
Project root
Classification navigation
Resource navigation
Resource identity
Relationship visibility
Search
Filtering
Expansion/collapse state
Selection
Selection handoff
Workspace integration
Application query boundary
Read-only behavior
Empty project behavior
Missing Resource behavior
Error states
Deterministic ordering
Registry-order preservation
No second Resource Registry
No second Graph
No second Classification hierarchy
Persistence isolation
Exchange isolation
Agent isolation
AI boundary
Public exports

Visual rendering tests belong to the eventual frontend implementation.

Acceptance Criteria

ENG-042 is complete when:

An Explorer capability exists within the Atlas UI architecture.
The Explorer is hosted by the ENG-040 Workspace.
Explorer data is obtained through the ENG-039 Application Boundary.
The Explorer exposes a stable UI/application identity.
The Explorer provides a Project root.
The Explorer can represent Classification hierarchy.
The Explorer can represent Resources.
Resource identity is AtlasID-based.
The Explorer can expose Relationship context.
Search is supported at the application/query boundary.
Filtering is supported at the application/query boundary.
Expansion/collapse state remains UI state.
Resource selection uses AtlasID.
Selection can be handed to future Inspector/3D surfaces.
Empty Projects are supported.
Missing Resources are handled explicitly.
Loading and error states are distinguishable.
Explorer ordering is deterministic.
Canonical Registry order is preserved where applicable.
The Explorer does not own an independent Resource Registry.
The Explorer does not own an independent Resource Graph.
The Explorer does not own a second Classification hierarchy.
Explorer navigation is read-only with respect to engineering state.
Persistence remains outside the Explorer.
Import/export remains outside the Explorer.
Agent execution remains outside the Explorer.
AI-generated information remains distinct from canonical engineering truth.
The Explorer remains independent from frontend technology.
Existing Atlas Core behavior remains unchanged.
Relationship to ENG-041

ENG-041 provides project-level awareness.

ENG-042 provides project-level navigation.

Dashboard
    ↓
"What is the state of this project?"


Explorer
    ↓
"What exists inside this project?"

The two surfaces operate over the same canonical Atlas state.

Neither duplicates engineering truth.

Relationship to ENG-043

The future Inspector will consume selection state produced by the Explorer.

Conceptually:

Explorer
    ↓
AtlasID
    ↓
Workspace Selection
    ↓
Inspector

The Explorer should therefore establish a clean identity-based selection
contract.

Relationship to Future 3D Workspace

The Explorer may provide a navigation entry to the future 3D View.

Explorer
    ↓
Resource Selection
    ↓
3D View

The 3D renderer remains a separate presentation capability.

Architectural Conclusion

ENG-042 establishes the Atlas Explorer as the primary project navigation
surface.

The architectural flow is:

                    Atlas Core
                        │
                        ▼
              ENG-039 Application
                    Boundary
                        │
                        ▼
                 Explorer Query
                        │
                        ▼
             Explorer Presentation
                        │
                        ▼
                 Explorer Panel
                        │
                        ▼
                Atlas Workspace

The Explorer provides structured navigation through the current Atlas Project
while preserving the canonical Resource, Classification, Relationship, and
Project architecture.

It becomes the bridge between project-level Dashboard awareness and
resource-level Inspector and 3D workflows.
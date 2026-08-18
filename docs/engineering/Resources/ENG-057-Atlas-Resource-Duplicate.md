# ENG-057 — Atlas Resource Duplicate

**Status:** Proposed  
**Phase:** Phase 11 — Resource Editing  
**Depends On:** ENG-056 — Atlas Resource Delete  
**Previous:** ENG-056 — Atlas Resource Delete  
**Next:** Phase 12 — Validation

---

# 1. Purpose

ENG-057 introduces the **Duplicate** capability within Phase 11 — Resource Editing.

Phase 11 establishes canonical Resource editing capabilities in the following sequence:

```text
ENG-052  Create
    ↓
ENG-053  Move
    ↓
ENG-054  Rotate
    ↓
ENG-055  Scale
    ↓
ENG-056  Delete
    ↓
ENG-057  Duplicate
The Phase 11 deliverable is:
Resources become editable.

ENG-057 therefore establishes a deterministic, canonical, application-level operation for creating a new Atlas Resource from an existing Resource while preserving the appropriate Resource state and spatial state without duplicating engineering identity or graph relationships.
Duplicate is not an alias operation.
Duplicate is not a second reference to the same Resource.
Duplicate creates a new canonical Resource with:
a new AtlasID,
copied Resource state,
independent mutable Resource state,
copied project-scoped spatial state,
no automatically cloned AtlasRelationship objects.
The operation must extend the existing Resource Create, Move, Rotate, Scale, and Delete architecture without introducing:
a second Resource model,
a second Resource registry,
a second relationship graph,
a second spatial-state system,
renderer-owned engineering state.
2. Architectural Position
The canonical Atlas interaction path remains:
User / UI / Agent / External System
                ↓
          AtlasCommand
                ↓
       AtlasApplication
                ↓
          AtlasProject
                ↓
      Canonical Atlas state
For ENG-057:
AtlasCommand
    │
    │ duplicate_resource
    ▼
AtlasApplication.execute()
    │
    ▼
AtlasProject
    │
    ├── AtlasResourceRegistry
    │
    ├── AtlasResource
    │
    ├── AtlasResourceGraph
    │
    └── AtlasSpatialStateRegistry
The Application boundary remains a thin interaction layer.
It must not become a second engineering model.
The duplicate operation must therefore be represented as an application command and delegated into the canonical Project/Resource architecture.
3. Relationship to ENG-052 — Resource Create
ENG-052 established the canonical Resource creation flow:
AtlasCommand
      ↓
AtlasApplication
      ↓
AtlasResource
      ↓
AtlasProject
      ↓
AtlasResourceRegistry
ENG-057 must build on that architecture.
Conceptually:
Existing Resource
      ↓
Duplicate operation
      ↓
New AtlasResource
      ↓
AtlasProject.add_resource()
      ↓
AtlasResourceRegistry
The new Resource must enter the canonical Project through the same ownership boundary used by Resource creation.
ENG-057 must not bypass AtlasProject.
The duplicate must not be inserted directly into an internal registry.
4. What “Duplicate” Means
ENG-057 defines:
Duplicate(Resource) means: create a new canonical Atlas Resource whose Resource state is copied from the identified source Resource, whose engineering identity is newly generated, whose mutable state is independent from the source, whose canonical spatial state is copied, and whose graph relationships are not automatically duplicated.

Therefore:
Source Resource
      ↓
Duplicate
      ↓
New Resource
The result is a distinct engineering entity.
For example:
Source
AtlasID = A
Name = Wall
Position = (10, 5, 0)
Rotation = (0, 0, 90)
Scale = (2, 1, 1)
After duplication:
Source
AtlasID = A
Name = Wall

Duplicate
AtlasID = B
Name = Wall
and:
A != B
The spatial state is copied:
A Position  = (10, 5, 0)
B Position  = (10, 5, 0)

A Rotation  = (0, 0, 90)
B Rotation  = (0, 0, 90)

A Scale     = (2, 1, 1)
B Scale     = (2, 1, 1)
The two Resources then become independently editable.
5. Canonical Identity
AtlasID remains the canonical engineering identity.
The source Resource's identity must never be reused.
Given:
Source AtlasID = A
a successful duplicate must produce:
Duplicate AtlasID = B
where:
B != A
The duplicate must receive a newly generated AtlasID.
The caller must not provide the duplicate's AtlasID as a mechanism for overriding identity.
ENG-057 must not:
clone the source AtlasID,
mutate the source AtlasID,
create an alias identity,
maintain a duplicate-ID mapping as a second identity system.
6. Source Resource Resolution
The source Resource is identified by canonical AtlasID.
Conceptually:
AtlasCommand(
    name="duplicate_resource",
    payload={
        "resource_id": source_id,
    },
)
The exact command payload must use the existing Atlas command contract.
The source must be resolved through the canonical Project/Resource ownership boundary.
Conceptually:
AtlasID
   ↓
AtlasProject
   ↓
AtlasResourceRegistry
   ↓
AtlasResource
ENG-057 must not search arbitrary SceneNodes to identify the source.
It must not use:
AtlasSceneNode.node_id,
Selection state,
renderer object identity,
UI object identity,
as engineering Resource identity.
7. Source Existence
A duplicate operation requires an existing source Resource.
If the supplied AtlasID does not resolve to a Resource:
duplicate_resource
        ↓
source not found
        ↓
failure
No new Resource may be created.
No spatial state may be created.
No graph mutation may occur.
No partial duplicate may remain in the Project.
The failure must leave the Project unchanged.
8. New Resource Construction
The duplicate must be a distinct AtlasResource instance.
Conceptually:
source_resource is not duplicate_resource
The duplicate must not be:
source_resource
and must not be a proxy, alias, or shared Resource object.
The canonical Resource registry must contain both:
Source Resource
Duplicate Resource
after successful duplication.
9. Resource State to Copy
The following canonical Resource state is copied from the source:
Classification
Name
Properties
Metadata
Semantic Tags
Categories
Lifecycle semantics
The source AtlasID is excluded because the duplicate requires a new identity.
Relationships are handled separately and are explicitly excluded from automatic duplication by ENG-057.
10. Classification Semantics
The duplicate preserves the source Resource's Classification.
Example:
Source:
Classification = Structural > Wall
Duplicate:
Classification = Structural > Wall
Classification remains the canonical registered Classification.
ENG-057 must not:
create a duplicate Classification definition,
create a new Classification ID,
modify the Classification hierarchy,
mutate the source Classification.
Classification definitions remain shared canonical definitions.
11. Name Semantics
The duplicate initially preserves the source Resource's name.
Therefore:
Source:
name = "Wall"

Duplicate:
name = "Wall"
ENG-057 does not invent automatic suffixing such as:
Wall Copy
Wall (1)
Wall Duplicate
Wall_2
unless a future explicit naming specification establishes such behavior.
Duplicate identity is established through AtlasID, not through automatic name modification.
Names are therefore allowed to be identical between the source and duplicate.
12. Properties
Resource Properties must be copied as Resource state.
The duplicate must receive an independent property collection.
Conceptually:
Source Properties
        ↓
copy
        ↓
Duplicate Properties
The duplicate must not share the same mutable property container with the source.
Therefore:
source.properties is not duplicate.properties
where the current Resource API exposes mutable property state.
Mutating the duplicate's Properties must not mutate the source.
Mutating the source's Properties must not mutate the duplicate.
13. Property Value Isolation
Nested mutable property values must not become an unintended shared mutable state.
ENG-057 therefore requires a sufficiently independent copy of Resource Property state such that mutable nested values cannot cause cross-Resource mutation.
Conceptually:
Source
Properties
    ↓
independent copy
    ↓
Duplicate
Properties
The implementation must not use a shallow container copy if that would leave mutable nested values shared.
The exact existing property model must be respected.
ENG-057 must not introduce a new Property model merely to perform duplication.
14. Metadata
Metadata is copied into an independent mutable metadata collection.
The duplicate must preserve the source metadata values while preventing accidental shared mutable state.
Therefore:
source.metadata is not duplicate.metadata
where the existing API exposes metadata as mutable state.
Changes to duplicate metadata must not modify source metadata.
Changes to source metadata must not modify duplicate metadata.
ENG-057 must not create a second metadata system.
15. Semantic Tags
The duplicate preserves the source Resource's semantic tag membership.
Existing Atlas semantic definitions remain canonical.
If Tags are immutable/shared definitions, the duplicate may reference the same canonical Tag definitions.
The Resource membership collection itself must remain Resource-scoped.
Therefore:
Source Resource
    ↓
Tag membership
    ↓
Duplicate Resource
does not mean:
shared mutable Resource tag collection
The duplicate receives its own membership state.
Changing membership on the duplicate must not remove or add membership on the source.
Tag definitions themselves are not duplicated.
16. Categories
The duplicate preserves the source Resource's Category membership.
Category definitions remain canonical and may be shared.
The duplicate receives an independent Resource-scoped Category membership collection.
Therefore:
Source Categories
        ↓
copied membership
        ↓
Duplicate Categories
The Category definitions themselves are not duplicated.
Changing Category membership on the duplicate must not modify Category membership on the source.
17. Lifecycle
The duplicate is a newly created Resource.
The duplicate must therefore enter the canonical Resource lifecycle according to the existing Resource creation contract.
ENG-057 must not blindly copy a terminal or historical lifecycle state from the source if doing so would violate the existing creation lifecycle.
The duplicate must be treated as a newly created Resource by the canonical Project/Resource creation boundary.
The source lifecycle remains unchanged.
18. Spatial State
ENG-053, ENG-054, and ENG-055 established project-scoped canonical spatial state keyed by AtlasID.
The current spatial state consists of:
AtlasID
    ↓
AtlasSpatialStateRegistry
    ├── Position
    ├── Rotation
    └── Scale
ENG-057 must preserve this architecture.
Spatial state is not stored directly on AtlasResource.
19. Spatial State Duplication
A successful Resource duplication must copy the source Resource's current canonical spatial state to the new Resource.
Therefore:
Source AtlasID
    ↓
Position
Rotation
Scale
    ↓
copy
    ↓
Duplicate AtlasID
    ↓
Position
Rotation
Scale
The duplicate begins with the same spatial state as the source.
Example:
Source:
Position = (4, 8, 2)
Rotation = (0, 45, 90)
Scale    = (2, 1, 0.5)
Duplicate:
Position = (4, 8, 2)
Rotation = (0, 45, 90)
Scale    = (2, 1, 0.5)
20. Spatial State Independence
The duplicate must receive independent spatial state keyed by its own AtlasID.
After duplication:
Source AtlasID     → Spatial State A
Duplicate AtlasID  → Spatial State B
where:
A != B
Changing the duplicate's position must not change the source position.
Changing the duplicate's rotation must not change the source rotation.
Changing the duplicate's scale must not change the source scale.
The spatial registry remains canonical.
No second duplicate-specific spatial registry may be introduced.
21. Relationship Semantics
AtlasRelationship is a first-class graph entity.
ENG-057 must not automatically duplicate the source Resource's relationships.
Example:
A ──depends_on──> B
Duplicating A produces:
A
B

C = duplicate(A)
but does not automatically produce:
C ──depends_on──> B
and does not automatically produce:
C ──depends_on──> A
and does not automatically produce cloned relationships between C and other Resources.
22. Why Relationships Are Not Duplicated
Relationships encode engineering graph meaning.
Copying a Resource does not inherently establish that its relationships should also be copied.
Automatic relationship cloning could silently create:
duplicate dependencies,
duplicate references,
duplicate parent-child structures,
unintended graph topology,
circular relationships,
incorrect engineering meaning.
Therefore ENG-057 establishes the conservative invariant:
Duplicate copies Resource state, not graph topology.

A future explicit operation may define relationship duplication or topology-aware duplication.
That is outside ENG-057.
23. Resource Relationship Preservation
The source Resource's existing relationships remain completely unchanged.
The duplicate begins with:
no automatically created relationships
The Project Graph remains the single canonical relationship graph.
No second graph is created.
No relationship object is copied merely because its source Resource was duplicated.
24. Scene and SceneNode Semantics
ENG-057 operates on canonical engineering Resources.
AtlasScene and AtlasSceneNode remain presentation/workspace state.
ENG-057 must not require a Scene.
ENG-057 must not require a SceneNode.
ENG-057 must not clone SceneNodes.
ENG-057 must not create a second SceneNode automatically.
ENG-057 must not copy viewport hierarchy merely because a Resource is duplicated.
If a future UI/workspace capability needs to create a visual representation of the duplicate, that synchronization must be explicitly defined outside ENG-057.
25. Selection Independence
ENG-057 must not create, modify, or clear selection state.
Selection remains:
AtlasResourceSelection
AtlasSelectionState
A caller may obtain the source Resource identity from selection, but duplication itself does not own Selection.
After duplication, ENG-057 does not automatically:
select duplicate
and does not automatically:
deselect source
Selection behavior belongs to a future application/UI interaction layer.
26. Gizmo Independence
AtlasGizmo represents manipulation intent/state.
ENG-057 must not:
create a Gizmo,
modify a Gizmo,
attach a Gizmo,
detach a Gizmo,
begin a Gizmo session,
manipulate Gizmo state.
Duplication is an engineering Resource operation, not a Gizmo operation.
27. Renderer Independence
ENG-057 must not depend on:
Three.js
WebGL
WebGPU
OpenGL
D5
Lumion
or any other renderer.
No visual duplication is performed.
The canonical engineering duplicate must be valid without a renderer.
28. Command Contract
The proposed application command identity is:
duplicate_resource
Conceptually:
AtlasCommand(
    name="duplicate_resource",
    payload={
        "resource_id": source_resource_id,
    },
)
The payload identifies the source Resource.
The command must not contain:
new AtlasID
as the identity authority.
The new identity is generated by the canonical Resource creation process.
The command represents intent.
Domain state remains owned by AtlasProject and its canonical subsystems.
29. Command Result
A successful duplicate_resource operation should return the newly created AtlasResource.
Conceptually:
duplicate_resource
        ↓
AtlasResource
The returned Resource must be the same object that was registered in the Project.
The result must therefore represent the canonical newly created Resource, not a detached copy.
30. Application Boundary
ENG-057 must extend:
AtlasApplication.execute()
rather than introducing another command execution system.
The application boundary remains responsible for routing the command.
It must not become the owner of:
Resource state,
spatial state,
relationships,
registry state.
The canonical state remains in the existing Atlas architecture.
31. Project Ownership
AtlasProject remains the ownership boundary for the duplicate.
A successful duplicate must belong to the same Project as the source.
Therefore:
Source Resource
      ↓
Project A

Duplicate Resource
      ↓
Project A
The duplicate must not automatically create:
Project B
or another ownership context.
32. Resource Registry
The duplicate must be registered in the canonical:
AtlasResourceRegistry
After successful duplication:
Registry
├── Source Resource
└── Duplicate Resource
The source remains registered.
The duplicate receives its own registry entry keyed by its new AtlasID.
Registry identity must remain canonical.
33. Source Preservation
A successful duplication must not mutate the source Resource.
The following source state must remain unchanged:
AtlasID
Classification
Name
Properties
Metadata
Tags
Categories
Lifecycle
Relationships
Spatial Position
Spatial Rotation
Spatial Scale
The source remains the same engineering entity.
34. Atomicity
Duplicate must be atomic.
The implementation must validate and construct the duplicate state before committing the new Resource into canonical Project state wherever practical.
For an unsuccessful operation:
Initial Project
      ↓
Invalid Duplicate
      ↓
same Project
No partial state may remain.
Invalid duplication must not leave:
an unregistered Resource,
a partially registered Resource,
orphaned spatial state,
partial relationships,
modified source state.
35. Failure Atomicity
If any required step fails during duplication:
Resource creation
Classification validation
Registry registration
Spatial-state creation
the operation must not leave an inconsistent Project.
The source Resource must remain unchanged.
The implementation must not silently swallow failures that would leave canonical state inconsistent.
Where rollback is required to preserve atomicity, it must be local to the operation and must not introduce a general transaction framework.
36. Determinism
Given:
same Project state
+
same source Resource
the duplicate operation must produce equivalent observable Resource state except for:
AtlasID
which is intentionally newly generated identity.
The operation must not depend on:
renderer state,
UI state,
selection state,
timing,
random Resource properties,
external mutable state.
Identity generation is the only intentionally non-identical aspect.
The copied Resource state must be deterministic.
37. Resource Isolation
Duplicating Resource A must not mutate Resource B.
For:
A
B
after:
Duplicate(A)
Resource B must remain unchanged.
This includes:
Properties
Metadata
Tags
Categories
Spatial State
Relationships
No unrelated Resource may be modified.
38. Copy Isolation
The following mutable Resource collections must not accidentally be shared:
Properties
Metadata
Tag membership collection
Category membership collection
The duplicate must be independently mutable.
Shared immutable semantic definitions remain allowed where established by the existing Atlas model.
ENG-057 must distinguish:
shared definition
from:
shared mutable Resource state
39. Idempotency Boundary
Duplicate is intentionally not idempotent.
Two identical duplicate requests:
Duplicate(A)
Duplicate(A)
must create two distinct Resources:
A
B
C
where:
B != C
This is expected because Duplicate is a creation operation and each successful invocation creates a new engineering identity.
The operation must therefore not attempt to deduplicate repeated requests based only on source identity.
40. Repeated Duplication
A duplicate may itself be duplicated.
Example:
A
 ↓
Duplicate
 ↓
B
 ↓
Duplicate
 ↓
C
Each Resource receives a unique AtlasID.
Each duplicate copies the current state of its immediate source according to the ENG-057 rules.
Relationships are not automatically created.
Spatial state is copied from the immediate source.
41. Delete Compatibility
ENG-056 establishes Resource deletion immediately before Duplicate.
ENG-057 must remain compatible with deletion.
If:
A
 ↓
Duplicate
 ↓
B
and A is subsequently deleted:
Delete(A)
then B must remain a valid independent Resource.
Likewise, deleting B must not delete A.
Duplicate therefore creates independent canonical Resource ownership.
42. Spatial Editing Compatibility
The duplicate must remain compatible with:
ENG-053 Move
ENG-054 Rotate
ENG-055 Scale
Example:
Duplicate(A)
      ↓
B
      ↓
Move(B)
      ↓
Rotate(B)
      ↓
Scale(B)
These operations must modify only B's canonical spatial state.
The source A must remain unchanged.
43. Persistence Compatibility
ENG-057 does not introduce a new persistence format.
The duplicate is a normal canonical Atlas Resource.
Therefore existing:
Atlas JSON
Save
Load
Import
Export
architecture remains authoritative.
A duplicated Resource must be representable by the existing persistence system.
No duplicate-specific serialization format is introduced.
Any required persistence behavior must be implemented through the existing canonical serialization architecture.
44. Provenance Boundary
ENG-057 does not introduce a new provenance system.
The duplicate operation must not silently redefine:
AtlasID
as provenance.
Identity and provenance remain separate concerns.
If future Atlas provenance semantics establish:
duplicated_from
or equivalent lineage information, that must be explicitly specified by a future provenance capability.
ENG-057 does not invent such a field.
45. Explicit Non-Goals
ENG-057 does not include:
Resource Create
Resource Move
Resource Rotate
Resource Scale
Resource Delete
beyond using their established architecture.
It does not include:
Relationship duplication
Relationship remapping
Graph topology cloning
Hierarchy cloning
Scene cloning
SceneNode cloning
It does not include:
Selection changes
Gizmo changes
Picking
Raycasting
Rendering
Three.js
WebGL
WebGPU
Camera
Navigation
It does not include:
Undo / Redo
History
Event sourcing
Transactions
It does not include:
Geometry duplication
Mesh duplication
Physical dimension recalculation
Quantity recalculation
Cost recalculation
Structural recalculation
It does not include:
Constraint solving
Validation-runtime expansion
It does not include:
AI
LLM
Agents
Orchestration
It does not introduce:
DuplicateRegistry
ResourceCloneRegistry
CopyRegistry
Second Resource Model
Second Graph
Second Spatial Registry
46. Future Compatibility
ENG-057 must leave clean boundaries for:
Validation
Constraints
Geometry
Physical Dimensions
History
Persistence
Provenance
Agents
AI
UI
Renderer
BIM
Interoperability
None of these should require replacing:
AtlasResource
AtlasProject
AtlasResourceRegistry
AtlasResourceGraph
AtlasApplication
AtlasCommand
AtlasID
AtlasSpatialStateRegistry
Duplicate must remain a canonical Resource creation operation rather than becoming a special Resource subtype.
47. Architecture Invariants
ENG-057 must preserve:
AtlasID
    = canonical engineering identity

AtlasProject
    = Project ownership boundary

AtlasResourceRegistry
    = canonical Resource registry

AtlasResourceGraph
    = canonical relationship graph

AtlasSpatialStateRegistry
    = canonical Resource-associated spatial state

AtlasApplication
    = application interaction boundary

AtlasCommand
    = intent

AtlasResource
    = canonical Resource model

AtlasScene
    = presentation/workspace state

AtlasSceneNode
    = viewport identity + presentation transform

AtlasResourceSelection
AtlasSelectionState
    = selection state

AtlasGizmo
    = manipulation intent/state
No subsystem introduced by ENG-057 may violate these boundaries.
48. Final ENG-057 Architecture
                         ATLAS
                           │
                   AtlasApplication
                           │
                     AtlasCommand
                           │
                  duplicate_resource
                           │
                           ▼
                     AtlasProject
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
 Resource Registry    Resource Graph   Spatial Registry
          │                │                │
          ▼                │                ▼
     AtlasResource         │         Position / Rotation /
          │                │              Scale
          │                │
          └────────┐       │
                   │       │
                   ▼       │
              New AtlasID  │
                   │       │
                   ▼       │
            Duplicate Resource
                   │
                   │
          ┌────────┴─────────┐
          │                  │
     copied Resource     copied Spatial
         state               state
          │                  │
          └────────┐ ┌───────┘
                   │ │
                   ▼ ▼
             Independent
             new Resource

Resource Graph:
NO automatic relationship cloning
The central invariant is:
Duplicate = new Resource identity + copied Resource state
            + copied spatial state
            + independent mutable state
            + no automatic graph duplication
49. RED Test Contract
The RED phase must establish tests against this finalized ENG-057 specification.
Primary test file:
tests/test_resource_duplicate.py
The RED suite must cover at minimum:
Construction / command boundary
duplicate_resource command exists
application boundary is used
Source resolution
valid AtlasID duplicates existing Resource
missing Resource fails
invalid Resource ID fails
Identity
duplicate receives new AtlasID
source AtlasID is preserved
source and duplicate are distinct objects
Resource state
classification copied
name copied
properties copied
metadata copied
tags copied
categories copied
Isolation
properties are independently mutable
metadata is independently mutable
tag membership is independently mutable
category membership is independently mutable
source remains unchanged
Spatial state
position copied
rotation copied
scale copied
spatial state uses new AtlasID
editing duplicate spatial state does not modify source
Relationships
source relationships preserved
duplicate has no automatically cloned relationships
graph remains canonical
Project / Registry
duplicate belongs to same Project
duplicate is registered
source remains registered
registry contains both Resources
Lifecycle
duplicate follows Resource creation lifecycle
source lifecycle remains unchanged
Failure atomicity
failed duplication creates no Resource
failed duplication creates no orphan spatial state
source remains unchanged
Determinism
same source state produces equivalent duplicate state
Non-idempotency
Duplicate(A)
Duplicate(A)

creates two different Resources
Delete compatibility
deleting source does not delete duplicate
deleting duplicate does not delete source
Boundary isolation
no Scene required
no SceneNode required
no Selection mutation
no Gizmo mutation
no renderer dependency
no AI dependency
The RED tests must not weaken the specification to accommodate implementation behavior.
If implementation reality conflicts with the intended architectural contract:
Specification
    ↓
revise specification
    ↓
revise RED contract
    ↓
implementation
The reverse direction is prohibited.
50. Implementation Principle
The implementation must provide the smallest complete architectural slice necessary to establish Resource Duplicate.
Required:
canonical source resolution
        +
new AtlasID
        +
new AtlasResource
        +
independent Resource state
        +
canonical Project registration
        +
copied spatial state
        +
no relationship cloning
        +
atomic failure behavior
        +
tests
It must not introduce speculative infrastructure.
In particular, implementation must not introduce:
generic clone framework
transaction engine
history system
provenance engine
graph cloning engine
new Resource abstraction
merely to support ENG-057.
51. Completion Criteria
ENG-057 is complete only when all of the following are true.
Specification
Duplicate semantics explicitly defined       ✅
Identity semantics defined                   ✅
Copy semantics defined                      ✅
Isolation semantics defined                 ✅
Spatial semantics defined                   ✅
Relationship semantics defined              ✅
Lifecycle semantics defined                 ✅
Atomicity defined                            ✅
Canonical ownership defined                 ✅
RED
tests/test_resource_duplicate.py exists      ⏳
Focused tests fail for expected reasons     ⏳
Tests are not weakened                      ⏳
Implementation
duplicate_resource command                   ⏳
Canonical source resolution                 ⏳
New AtlasID generation                      ⏳
Independent Resource state                  ⏳
Project registration                        ⏳
Spatial state duplication                   ⏳
Relationship non-duplication                ⏳
Atomic failure behavior                     ⏳
GREEN
Focused Duplicate tests pass                ⏳
Regression
Full Atlas suite passes                     ⏳
No ENG-052 regression                       ⏳
No ENG-053 regression                       ⏳
No ENG-054 regression                       ⏳
No ENG-055 regression                       ⏳
No ENG-056 regression                       ⏳
No Agent regression                         ⏳
No Persistence regression                   ⏳
Checkpoint
ENG-057 = COMPLETE
52. Decision Freeze
The following decisions are the proposed non-negotiable ENG-057 contract:
1. Duplicate is a Resource creation operation.

2. Duplicate creates a new AtlasResource instance.

3. Duplicate always receives a new AtlasID.

4. The source AtlasID is never reused.

5. Source and duplicate are distinct engineering identities.

6. Duplicate belongs to the same AtlasProject as the source.

7. Duplicate is registered in the canonical AtlasResourceRegistry.

8. Source remains registered after duplication.

9. Classification is copied.

10. Name is copied unchanged.

11. Properties are copied into independent mutable state.

12. Metadata is copied into independent mutable state.

13. Semantic Tag membership is copied.

14. Category membership is copied.

15. Shared immutable Tag/Category definitions are not duplicated.

16. Duplicate follows the canonical Resource creation lifecycle.

17. Source lifecycle is not modified.

18. Canonical spatial Position is copied.

19. Canonical spatial Rotation is copied.

20. Canonical spatial Scale is copied.

21. Spatial state is keyed by the new AtlasID.

22. Source and duplicate spatial state are independent.

23. AtlasResource does not gain spatial fields.

24. AtlasScene is not required.

25. AtlasSceneNode is not duplicated.

26. Selection is not modified.

27. Gizmo state is not modified.

28. Renderer state is not required.

29. AtlasRelationship objects are not automatically duplicated.

30. The canonical AtlasResourceGraph remains authoritative.

31. Duplicate does not automatically create new graph topology.

32. Source relationships remain unchanged.

33. Failed duplication is atomic.

34. Failed duplication creates no orphan Resource.

35. Failed duplication creates no orphan spatial state.

36. Source Resource state is never modified by duplication.

37. Duplicate is intentionally not idempotent.

38. Repeated duplication creates distinct new Resources.

39. Duplicate can itself be duplicated.

40. Duplicate is compatible with Move, Rotate, Scale, and Delete.

41. Existing persistence architecture remains authoritative.

42. No duplicate-specific serialization architecture is introduced.

43. Provenance is not invented by ENG-057.

44. Mutation enters through AtlasApplication.execute().

45. Commands represent intent.

46. AtlasProject remains the ownership boundary.

47. AtlasResourceRegistry remains canonical.

48. AtlasSpatialStateRegistry remains canonical.

49. No second Resource model is introduced.

50. No speculative infrastructure is introduced.
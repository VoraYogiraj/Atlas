ENG-059 — Atlas v0.1 Architecture Documentation Baseline

**Document ID:** ENG-059  
**Title:** Atlas v0.1 Architecture Documentation Baseline  
**Version:** 0.1.0  
**Status:** Proposed  
**Phase:** Phase 13 — Documentation  
**Previous:** ENG-058 — Atlas Core Validation Baseline  
**Depends On:** ENG-001 through ENG-058  
**Type:** Documentation-only engineering task  
**Proposed Path:** `docs/Engineering/Resources/ENG-059-Atlas-v0.1-Architecture-Documentation-Baseline.md`

---

# 1. Purpose

ENG-059 establishes the authoritative architecture documentation baseline for Atlas v0.1.

The objective is to document the architecture that has already been designed, implemented, tested, and validated through ENG-058.

ENG-059 does not introduce new engineering capability.

The documentation provides a stable reference for:

- Atlas canonical engineering identity
- Resource representation
- Registry ownership
- Project ownership
- Relationship representation
- Semantics and classification
- Categories and semantic tags
- Constraints and validation
- Project-scoped spatial state
- Resource lifecycle
- Application boundaries
- Agent and AI boundaries
- UI / Scene / 3D boundaries
- Resource editing operations
- Cross-capability architectural invariants
- Future extension rules

The documentation describes the actual Atlas v0.1 architecture rather than a speculative future implementation.

---

# 2. Atlas v0.1 Architectural Position

Atlas is centered on the representation of the engineering world through canonical Resources and their explicit relationships.

The foundational architecture is:

```text
Resource
    ↓
Registry
    ↓
Relationships
    ↓
Semantics
    ↓
Constraints / Validation
    ↓
Agents
    ↓
UI / AI
```

The canonical interaction path is:

```text
User / UI / Agent / External System
                ↓
          AtlasCommand
                ↓
        AtlasApplication
                ↓
           AtlasProject
                ↓
       Canonical Atlas State
```

Every higher-level interaction ultimately operates against the canonical Atlas model rather than creating a competing engineering representation.

---

# 3. Core Architectural Principles

## 3.1 Canonical identity

`AtlasID` is the canonical engineering identity of a Resource.

Resource identity does not depend on Python object identity, SceneNode identity, UI identity, renderer identity, selection identity, or agent identity.

## 3.2 Canonical ownership

`AtlasProject` owns project-scoped canonical state.

The Resource Registry, Relationship Graph, and Spatial State Registry participate in this project-owned canonical model.

## 3.3 Explicit relationships

Engineering relationships are explicit graph state.

They are not implicitly owned by UI objects, SceneNodes, or agent state.

## 3.4 Separation of concerns

Atlas separates engineering identity, Resource state, relationship state, semantic state, validation, spatial state, application interaction, agent behavior, and UI / Scene presentation.

## 3.5 Canonical state over presentation state

The canonical Atlas model is authoritative. UI, Scene, renderer, agents, and AI may operate around the model but must not silently replace it.

## 3.6 Additive evolution

Future Atlas capabilities must extend the established foundation rather than introduce competing foundational systems.

---

# 4. AtlasID and Engineering Identity

`AtlasID` is the canonical identity of an engineering Resource.

A Resource's identity remains stable while its mutable state changes.

Established invariants include:

- Resource creation produces a new AtlasID.
- Resource duplication produces a new AtlasID.
- Resource deletion does not transfer identity to another Resource.
- Move, Rotate, and Scale do not change Resource identity.
- Resource identity does not depend on Python object identity.
- Resource identity does not depend on UI identity.
- Resource identity does not depend on SceneNode identity.

The canonical rule is:

```text
AtlasID = engineering Resource identity
```

---

# 5. AtlasResource

`AtlasResource` is the canonical engineering Resource model.

A Resource carries its established domain state, including identity, classification, name, properties, tags, categories, metadata, and lifecycle.

The Resource model intentionally does not become a container for presentation-specific spatial or UI state.

Position, Rotation, and Scale are maintained through the canonical project-scoped spatial-state architecture.

There must not be a second Resource model that becomes authoritative for any of these concerns.

---

# 6. AtlasProject

`AtlasProject` is the canonical owner and coordination boundary for project-scoped Atlas state.

The established architecture places canonical project state behind the Project boundary:

```text
AtlasApplication
        ↓
AtlasProject
        ↓
Canonical Atlas State
```

Project-scoped canonical state includes the established Resource Registry, Relationship Graph, classification state, and Spatial State Registry.

The application layer does not become a competing engineering model.

---

# 7. Resource Registry

The canonical Resource Registry is `AtlasResourceRegistry`.

The Registry is the canonical authority for Resources within a Project.

Registry invariants include:

- successfully created Resources are registered;
- successfully duplicated Resources are registered;
- deleted Resources are removed;
- invalid operations do not leave partial registry entries;
- duplication increases Resource count by exactly one;
- deletion decreases Resource count by exactly one;
- Move, Rotate, and Scale do not change Resource count;
- unrelated Resources remain registered during operations on another Resource.

No operation may silently maintain a second authoritative Resource collection.

---

# 8. Relationship Graph

`AtlasResourceGraph` is the canonical relationship representation.

Relationships are first-class engineering relationships between Resources.

The graph provides the canonical representation for relationship insertion, relationship validation, Resource-specific relationship queries, traversal, relationship counts, and relationship integrity.

Resource deletion removes relationships involving the deleted Resource according to the established Resource Delete contract.

The graph is not duplicated by Scene, UI, agents, or presentation state.

---

# 9. Semantics and Classification

Atlas provides semantic mechanisms for expressing Resource meaning.

These include:

- classifications
- classification registries
- classification hierarchy
- categories
- semantic tags
- Resource classification membership
- project-scoped classification behavior

Semantics describe engineering meaning.

Presentation state must not be treated as semantic identity.

Classification and semantic membership remain part of the canonical Atlas model and must remain compatible with Resource identity and Project ownership.

---

# 10. Constraints

Atlas includes a constraint architecture for expressing domain rules around Resource state.

Constraints belong to the canonical semantic/validation architecture.

ENG-059 documents the established constraint capability but does not introduce new constraint types or a new constraint engine.

Future domain-specific constraints may extend the existing architecture through explicit engineering specifications.

---

# 11. Validation Architecture

Atlas already contains a validation runtime established by earlier engineering specifications, including the validation engine, rules, categories, severities, and results.

ENG-059 documents that existing architecture; it does not create another validation system.

The distinction is:

```text
Existing Validation Runtime
        ↓
Defines validation behavior

ENG-058
        ↓
Verified Atlas architecture using automated validation/tests

ENG-059
        ↓
Documents the proven architecture
```

Validation observes and verifies canonical Atlas state.

It must not create a shadow representation of engineering state.

The canonical principle is:

```text
Canonical Atlas State
        ↓
Validation
        ↓
Verified Invariants
```

not:

```text
Canonical Atlas State
        ↓
Validation Model
        ↓
Second Engineering State
```

Validation is observational with respect to Resource state.

---

# 12. Spatial State Architecture

Spatial state is deliberately separated from the canonical Resource model.

The established project-scoped spatial architecture represents:

- Position
- Rotation
- Scale

keyed by `AtlasID`.

Conceptually:

```text
AtlasResource
     +
AtlasSpatialStateRegistry
```

rather than embedding spatial state into `AtlasResource`.

The established defaults are:

```text
Position = (0, 0, 0)
Rotation = (0, 0, 0)
Scale    = (1, 1, 1)
```

Move, Rotate, and Scale operate on the canonical spatial state associated with the Resource's AtlasID.

---

# 13. Resource Lifecycle

Resource lifecycle is part of the canonical Resource architecture.

The established Resource editing sequence is:

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
```

Lifecycle semantics remain distinct from presentation state.

Duplication creates a new canonical Resource and therefore a new AtlasID. The duplicate enters the established CREATED lifecycle state rather than silently inheriting an ACTIVE or ARCHIVED lifecycle state.

---

# 14. Application Boundary

`AtlasApplication` and the established `AtlasCommand` boundary provide the application-level interaction mechanism for Resource operations.

The canonical interaction path is:

```text
Input
  ↓
AtlasCommand
  ↓
AtlasApplication
  ↓
AtlasProject
  ↓
Canonical Atlas State
```

The application boundary:

- resolves Resources through Project state;
- operates on canonical Resources;
- preserves canonical state ownership;
- rejects invalid command input deterministically;
- does not require UI state;
- does not require Scene state;
- does not require Selection state;
- does not require Gizmo state;
- does not require renderer state.

The application layer is an interaction boundary, not a second engineering model.

---

# 15. Agents and AI Boundary

Agents and AI operate around the canonical Atlas model.

They may interpret Atlas state, extract information, reason over Resources and relationships, plan, generate candidates, and invoke established Atlas capabilities.

They must not become the canonical source of engineering state or identity.

The architectural relationship is:

```text
Agent / AI
     ↓
interpret / reason / propose / invoke
     ↓
Canonical Atlas Model
```

not:

```text
Agent / AI
     ↓
canonical engineering state
```

Agent state is therefore not a replacement for Project, Registry, Graph, Spatial State, or Validation state.

---

# 16. UI / Scene / 3D Boundary

UI and 3D systems are presentation/workspace mechanisms.

Established presentation concepts include:

- Scene
- SceneNode
- Selection
- Gizmo
- Camera
- Toolbar
- Panels
- Explorer
- Inspector
- UI shell
- renderer state

These systems may present or manipulate Atlas state through established application boundaries.

They do not own canonical engineering identity.

In particular:

- SceneNode identity is not AtlasID.
- Selection is not canonical Resource state.
- Gizmo state is not canonical spatial authority.
- Renderer state is not engineering state.
- UI state is not the Resource Registry.
- UI state is not the Relationship Graph.

---

# 17. Resource Editing Operations

## 17.1 Create — ENG-052

Create establishes a new canonical Resource while preserving canonical Resource identity and Project/Registry ownership.

## 17.2 Move — ENG-053

Move changes the Resource's canonical project-scoped Position.

Move does not change AtlasID, modify Resource meaning, create UI-owned spatial state, or modify relationships.

## 17.3 Rotate — ENG-054

Rotate changes the canonical project-scoped Rotation.

Rotate does not change Resource identity or unrelated Resource state.

## 17.4 Scale — ENG-055

Scale changes the canonical project-scoped Scale.

Scale values are numeric, finite, positive, with semantic rejection of boolean values.

Scale does not change Resource identity, relationships, or unrelated state.

## 17.5 Delete — ENG-056

Delete removes a Resource from canonical Project state.

Established Delete behavior includes:

- resolving the source through Project;
- removing relationships involving the Resource;
- unregistering the Resource;
- removing its Position, Rotation, and Scale;
- preserving atomic invalid-operation behavior.

Delete does not introduce tombstones, history, undo/redo, or speculative transaction infrastructure.

## 17.6 Duplicate — ENG-057

Duplicate creates a new canonical Resource with a new AtlasID.

The established Duplicate contract includes:

- copied classification/name;
- deep-copied mutable properties;
- isolated metadata;
- copied tag/category membership;
- CREATED lifecycle state;
- copied Position / Rotation / Scale;
- independent spatial state;
- no relationship cloning;
- preservation of source and unrelated Resources;
- intentional non-idempotence;
- compatibility with Delete, Move, Rotate, and Scale;
- no Scene, Selection, Gizmo, or Renderer dependency.

Repeated duplication intentionally produces distinct Resources:

```text
Duplicate(A) → B
Duplicate(A) → C

B != C
```

---

# 18. Cross-Capability Architectural Invariants

1. **Single canonical Resource model** — Atlas has one canonical `AtlasResource` model.
2. **Single canonical Registry** — Atlas has one canonical Resource Registry.
3. **AtlasID is engineering identity** — `AtlasID` is the canonical identity used to identify engineering Resources.
4. **Project owns canonical state** — `AtlasProject` owns canonical project-scoped state.
5. **Relationships are explicit** — engineering relationships are represented through the canonical Relationship Graph.
6. **Spatial state is separate** — Position, Rotation, and Scale are maintained through the canonical spatial-state architecture rather than duplicated inside Resources or UI objects.
7. **Validation is canonical** — Atlas has one canonical validation architecture.
8. **Validation is observational** — validation does not mutate canonical Resource state.
9. **UI is not canonical** — Scene/UI/3D state is not the source of engineering identity or canonical engineering state.
10. **Agents are not canonical** — Agents and AI do not own canonical engineering state.
11. **Determinism** — equivalent initial canonical state and equivalent valid commands produce equivalent canonical outcomes, subject to intentionally non-idempotent operations such as Duplicate.
12. **Additive evolution** — future capabilities extend the canonical Atlas architecture rather than replacing or duplicating its foundation.

---

# 19. Canonical Ownership Rules

| Concern | Canonical authority |
|---|---|
| Resource identity | `AtlasID` |
| Resource model | `AtlasResource` |
| Project state | `AtlasProject` |
| Resource collection | `AtlasResourceRegistry` |
| Relationships | `AtlasResourceGraph` |
| Classification | Atlas classification architecture |
| Semantic tags | Atlas semantic-tag architecture |
| Constraints | Atlas constraint architecture |
| Validation | `AtlasValidationEngine` |
| Position | Project Spatial State Registry |
| Rotation | Project Spatial State Registry |
| Scale | Project Spatial State Registry |
| Editing boundary | `AtlasApplication` / `AtlasCommand` |
| UI presentation | UI / Scene layer |
| Agent behavior | Agent runtime |
| AI reasoning | AI / Agent layer |

No non-canonical layer may silently become authoritative for a concern listed above.

---

# 20. Non-Canonical and Forbidden Parallel Systems

The following are prohibited as competing foundational systems under Atlas v0.1:

- second Resource model;
- second Resource Registry;
- second Relationship Graph;
- second Spatial State Registry;
- second Validation Engine;
- renderer-owned engineering state;
- UI-owned canonical engineering state;
- Scene-owned engineering identity;
- Agent-owned canonical engineering state;
- AI-owned canonical engineering state;
- speculative transaction framework;
- speculative clone framework;
- speculative provenance/history framework introduced as architectural replacement.

Future capabilities may require explicit new specifications, but they must preserve the canonical architecture.

---

# 21. Architecture Extension Rules

Before introducing a major subsystem, evaluate:

### Identity
Can the subsystem preserve Atlas Resource identity?

### Representation
Does it operate on or map to canonical Atlas Resources?

### Relationships
Can its entities participate in the Atlas Resource Graph?

### Semantics
Can its meaning be represented through existing semantic mechanisms or explicit extensions?

### Validation
Can its rules be represented through the existing validation / constraint architecture?

### Context
Can project-specific behavior remain project/context scoped?

### Provenance
Can external source information remain separate from canonical identity?

### History
Can future revisions be introduced without replacing the current Resource model?

### Agents
Can Agents operate on the subsystem through Atlas interfaces?

### Extensibility
Does the subsystem extend Atlas rather than create a competing engineering model?

---

# 22. ENG-058 Validation Evidence

ENG-058 established the Atlas Core Validation Baseline and verified the canonical architecture across multiple boundaries.

| Validation area | Result |
|---|---:|
| Focused ENG-058 validation | 5 passed |
| Core cross-capability validation | 494 passed |
| Agent / AI boundary | 284 passed |
| Semantics / Classification / Constraints | 241 passed |
| UI / Application boundary | 512 passed |
| Combined targeted validation | 1,536 passed |
| Phase 11 regression | 1,930 passed |
| Failures | 0 |
| Repository state | Clean |
| ENG-058 checkpoint | Completed |

The core cross-capability validation exercised:

```text
Resource
   ↓
Project
   ↓
Registry
   ↓
Relationship Graph
   ↓
Spatial State
   ↓
Lifecycle
   ↓
Validation
   ↓
Application Boundary
   ↓
UI Boundary
```

The Agent / AI validation exercised the established agent runtime, Resource Agent, Relationship Agent, Validation Agent, Semantic Agent, multi-agent coordination, and orchestrator boundaries.

The semantics validation exercised classification, hierarchy, classification registry, project classification, classification queries, Resource classification, Resource Registry classification, categories, semantic tags, and constraints.

The UI/application validation exercised Scene, Selection, Gizmo, Camera, Toolbar, Panels, Explorer, Inspector, and UI shell boundaries.

Existing Python 3.14 / `pytest-asyncio` deprecation warnings observed during these runs are not Atlas test failures. Dependency modernization is outside this documentation baseline.

---

# 23. Architecture Stability Statement

Atlas v0.1 is a foundational engineering representation centered on Resources and their relationships.

The validated foundation is:

```text
Resource
    ↓
Registry
    ↓
Relationships
    ↓
Semantics
    ↓
Constraints / Validation
    ↓
Application
    ↓
Agents
    ↓
UI / AI
```

This foundation is not a temporary implementation detail.

Future Atlas versions may add capabilities, domains, representations, integrations, and intelligence, but those capabilities must extend the canonical foundation rather than silently replace it.

> **Atlas evolves by extension of canonical engineering state, not by creation of competing canonical state.**

---

# 24. Documentation-Only Constraints

ENG-059 itself introduces no production capability.

The following constraints apply:

1. No production Python/API behavior may change.
2. No new Resource model may be introduced.
3. No new Registry may be introduced.
4. No new Relationship Graph may be introduced.
5. No new Spatial State system may be introduced.
6. No new Validation Engine may be introduced.
7. No transaction framework may be introduced.
8. No clone framework may be introduced.
9. No provenance/history framework may be introduced as a replacement architecture.
10. No UI/Scene redesign may be introduced.
11. No Agent/AI architecture redesign may be introduced.
12. Documentation must describe existing behavior rather than speculative behavior.
13. Existing contracts from ENG-001 through ENG-058 must not be weakened or contradicted.

---

# 25. Non-Goals

ENG-059 does not implement:

- new Resource editing operations;
- new Resource types;
- new registries;
- new relationship models;
- new spatial systems;
- new validation engines;
- regulatory compliance rules;
- building-code rules;
- automatic correction;
- AI-generated validation rules;
- AI-based validation decisions;
- UI redesign;
- renderer implementation;
- Scene architecture changes;
- persistence redesign;
- collaboration;
- distributed validation;
- undo/redo;
- history systems;
- transaction frameworks;
- future-domain implementation.

Future domains may be supported by future specifications, but their implementation is outside ENG-059.

---

# 26. Verification Criteria

ENG-059 is GREEN when:

## Documentation completeness

- [ ] Required architectural sections exist.
- [ ] AtlasID and Resource identity are documented.
- [ ] AtlasResource is documented.
- [ ] AtlasProject ownership is documented.
- [ ] Resource Registry is documented.
- [ ] Relationship Graph is documented.
- [ ] Semantics and classification are documented.
- [ ] Constraints are documented.
- [ ] Validation architecture is documented.
- [ ] Spatial State architecture is documented.
- [ ] Lifecycle is documented.
- [ ] Application boundary is documented.
- [ ] Agent / AI boundary is documented.
- [ ] UI / Scene / 3D boundary is documented.
- [ ] ENG-052 through ENG-057 are represented.
- [ ] Cross-capability invariants are explicitly stated.
- [ ] ENG-058 validation evidence is recorded.
- [ ] Future extension rules are documented.

## Architecture integrity

- [ ] No production source files are modified by the documentation task.
- [ ] No new API is introduced.
- [ ] No duplicate Resource model is introduced.
- [ ] No duplicate Registry is introduced.
- [ ] No duplicate Graph is introduced.
- [ ] No duplicate Spatial State system is introduced.
- [ ] No duplicate Validation Engine is introduced.
- [ ] No speculative transaction/clone/provenance architecture is introduced.
- [ ] No UI/Scene object is declared canonical.
- [ ] No Agent/AI component is declared canonical.

## Consistency

- [ ] Documentation agrees with ENG-001 through ENG-058.
- [ ] Documentation agrees with the validated implementation.
- [ ] Documentation does not contradict the ENG-058 checkpoint.
- [ ] Existing tests remain unaffected.

---

# 27. Completion Criteria

ENG-059 may be marked complete when:

```text
ENG-059 Specification
        ↓
Documentation written
        ↓
Documentation reviewed
        ↓
Architecture consistency verified
        ↓
No production changes
        ↓
Regression remains GREEN
        ↓
Checkpoint
        ↓
ENG-059 COMPLETE
```

The resulting checkpoint represents the documented Atlas v0.1 architecture as implemented and validated.

---

# 28. Final Architectural Principle

Atlas v0.1 is built around a foundational idea:

> **The engineering world is represented through canonical Resources and their relationships.**

Everything above that foundation exists to give those Resources meaning, constraints, behavior, interaction, intelligence, or presentation.

```text
                    Atlas v0.1
                        │
                     Resource
                        │
                     Registry
                        │
                  Relationships
                        │
                    Semantics
                        │
              Constraints / Validation
                        │
                   Application
                        │
                     Agents
                        │
                    UI / AI
```

The canonical Atlas model remains the source of truth.

Agents do not replace it.

AI does not replace it.

UI does not replace it.

Scene state does not replace it.

Validation does not replace it.

Future domain modules do not replace it.

They extend and operate around the canonical foundation.

---

# 29. Deliverable

**Authoritative document:**

```text
docs/Engineering/Resources/ENG-059-Atlas-v0.1-Architecture-Documentation-Baseline.md
```

**Document type:** Atlas v0.1 architecture baseline  
**Engineering capability introduced:** None  
**Purpose:** Establish the authoritative documentation reference for the validated Atlas v0.1 foundation.

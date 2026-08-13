# ENG-036 — Atlas JSON Serialization

**Document ID:** ENG-036  
**Title:** Atlas JSON Serialization  
**Version:** 0.1.0  
**Status:** Complete  
**Depends On:** ENG-001 through ENG-035A  
**Implementation:** `packages/atlas/src/atlas/serialization/`

---

# Purpose

ENG-036 defines the canonical JSON representation of the Atlas domain model.

The purpose of this specification is to establish a stable, deterministic,
portable representation of Atlas engineering information.

Serialization must preserve Atlas engineering meaning while remaining
independent from filesystem persistence, databases, transport mechanisms,
and external-format adapters.

The serialization layer is a representation boundary.

```text
Atlas Domain Model
        ↓
Atlas JSON Serialization
        ↓
JSON Representation
Scope

ENG-036 defines serialization and deserialization of:

AtlasProject
AtlasID
AtlasClassification
AtlasResource
AtlasProperty
AtlasRelationship
AtlasSemanticTag
AtlasCategory
AtlasLifecycle
Project metadata
Resource metadata

ENG-036 also defines:

Serialization version
Atlas version
Deterministic representation
Project round-trip behavior
Resource round-trip behavior
Relationship reference representation
Classification hierarchy representation
JSON text encoding and decoding
Non-Goals

ENG-036 does not implement:

Filesystem persistence
Project save/load workflows
Import/export adapters
Databases
Remote storage
Network transport
Synchronization
Provenance
Revision history
Change tracking
BIM/IFC
CAD
Revit
PDF interpretation
Excel interpretation

Filesystem persistence is defined by ENG-037.

External exchange boundaries are defined by ENG-038.

Architectural Position

Serialization is a representation of the Atlas domain model.

It does not become a second domain model.

Atlas Domain Model
        ↓
      Serializer
        ↓
Portable JSON Representation

The serializer must not define:

engineering meaning
validation rules
relationship semantics
classification semantics
lifecycle rules
agent behavior

Those responsibilities remain with the Atlas domain model.

Design Principles

ENG-036 follows these principles:

Preserve Atlas engineering meaning.
Preserve stable Atlas identity.
Preserve relationships.
Preserve semantic information.
Preserve lifecycle state.
Preserve project context.
Remain deterministic.
Remain versioned.
Remain extensible.
Avoid recursive duplication.
Avoid mutation of source objects.
Remain independent from file persistence.
Serialization Envelope

A serialized Atlas Project is wrapped in an Atlas envelope.

Canonical structure:

{
  "atlas": {
    "serialization_version": "0.1.0",
    "atlas_version": "0.1.0"
  },
  "project": {
    "id": "project-id",
    "name": "Project Name",
    "metadata": {},
    "classifications": [],
    "resources": [],
    "relationships": []
  }
}

The atlas section identifies the serialization and Atlas versions.

The project section contains the canonical project representation.

Versioning

Serialized Atlas data must identify:

Serialization version
Atlas version

The serialization version identifies the structure and interpretation of the
serialized representation.

The Atlas version identifies the Atlas model version represented by the data.

Example:

{
  "atlas": {
    "serialization_version": "0.1.0",
    "atlas_version": "0.1.0"
  }
}

Future serialization versions may evolve while preserving the underlying Atlas
domain architecture.

Project Representation

A Project contains:

Identity
Name
Metadata
Classifications
Resources
Relationships

Canonical representation:

{
  "project": {
    "id": "project-id",
    "name": "Sample Building",
    "metadata": {},
    "classifications": [],
    "resources": [],
    "relationships": []
  }
}

Project identity must be preserved through serialization.

Project Identity

AtlasProject.aid is represented as a string containing the UUID value.

Example:

{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}

Deserialization must reconstruct the same AtlasID.

Serialization must never replace Atlas identity with:

array position
object memory identity
file location
database-generated identity
temporary import identity
Classification Representation

Classifications are reusable project-scoped objects.

A Classification contains:

ID
Name
Description
Parent reference

Example:

{
  "id": "wall",
  "name": "Wall",
  "description": "A wall element.",
  "parent": "building-element"
}

Root classifications have:

{
  "parent": null
}

The derived values:

path
depth
is_root

are not serialized because they can be reconstructed from the hierarchy.

Classification Registry

Classifications are serialized at the Project level.

They are not duplicated inside every Resource.

Example:

{
  "classifications": [
    {
      "id": "physical-resource",
      "name": "Physical Resource",
      "description": "",
      "parent": null
    },
    {
      "id": "building-element",
      "name": "Building Element",
      "description": "",
      "parent": "physical-resource"
    },
    {
      "id": "wall",
      "name": "Wall",
      "description": "",
      "parent": "building-element"
    }
  ]
}

This preserves reusable classification identity and hierarchy.

Resource Representation

A Resource contains:

Identity
Classification reference
Name
Properties
Metadata
Semantic Tags
Categories
Lifecycle

Example:

{
  "id": "resource-id",
  "classification": "wall",
  "name": "External Wall",
  "properties": {},
  "metadata": {},
  "tags": [],
  "categories": [],
  "lifecycle": "active"
}
Resource Identity

The Resource's AtlasID is serialized as the Resource's id.

Example:

{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}

Deserialization must recreate the same AtlasID.

This is mandatory for engineering identity preservation.

Resource Classification

A Resource references its Classification by Classification ID.

Example:

{
  "classification": "wall"
}

The full Classification object is not duplicated inside the Resource.

During Project deserialization, the Resource's classification reference must
resolve against the Project Classification Registry.

Property Representation

Each Resource Property contains:

ID
Name
Value
Data type
Unit
Description
Required state

Example:

{
  "id": "thickness",
  "name": "Thickness",
  "value": 150,
  "data_type": "number",
  "unit": "mm",
  "description": "Wall thickness.",
  "required": true
}

Property values must preserve their serialized value.

The serializer must not apply engineering validation or unit conversion during
serialization.

Metadata Representation

Project and Resource metadata are serialized as dictionaries.

Example:

{
  "metadata": {
    "discipline": "architecture",
    "source": "engineer"
  }
}

Metadata remains an extensibility mechanism and is not interpreted by the
serializer.

Semantic Tag Representation

Semantic Tags are serialized as Resource-level objects.

Each Tag contains:

ID
Name
Description

Example:

{
  "id": "load-bearing",
  "name": "Load Bearing",
  "description": "Structural load-bearing element."
}

Tags preserve their Resource association through the Resource representation.

Category Representation

Categories are serialized as Resource-level objects.

Each Category contains:

ID
Name
Description

Example:

{
  "id": "structural",
  "name": "Structural",
  "description": "Structural building elements."
}
Lifecycle Representation

A Resource lifecycle state is serialized using its canonical string value.

Example:

{
  "lifecycle": "active"
}

Supported states include:

created
active
archived
deleted

Deserialization must reconstruct the corresponding AtlasLifecycle.

The serializer must not bypass the lifecycle model's transition rules.

Relationship Representation

Relationships are first-class Atlas objects and therefore must be preserved.

However, Resources must not recursively contain full Resource objects through
their Relationships.

Canonical Project representation:

{
  "relationships": [
    {
      "id": "rel-001",
      "relationship_type": "contains",
      "source": "resource-001",
      "target": "resource-002",
      "description": ""
    }
  ]
}

Relationship endpoints are represented using stable Atlas Resource IDs.

Relationship Reconstruction

During deserialization:

Classifications are reconstructed.
Resources are reconstructed and registered.
Resource IDs are indexed.
Relationships are reconstructed from source/target IDs.
Relationship endpoints are resolved against the reconstructed Resources.
Relationships are added to the Project Graph.

A relationship referencing a nonexistent Resource must fail explicitly.

The serializer must never silently create placeholder Resources for missing
relationship endpoints.

Avoiding Recursive Serialization

This is invalid:

{
  "source": {
    "id": "resource-001",
    "relationships": [
      {
        "source": {
          "...": "..."
        }
      }
    ]
  }
}

The canonical approach is:

{
  "source": "resource-001",
  "target": "resource-002"
}

This prevents:

recursive structures
duplicated Resources
inconsistent Resource state
oversized representations
graph reconstruction ambiguity
Determinism

Serializing the same unchanged Atlas state must produce deterministic output.

Equivalent Atlas states should result in equivalent serialized structures.

Determinism is important for:

testing
caching
synchronization
change detection
version control
future distributed systems

The implementation uses deterministic JSON encoding and stable structural
ordering.

JSON Text Representation

The serializer supports conversion between:

AtlasProject
      ↕
Python dictionary representation
      ↕
JSON text

JSON text must be valid JSON.

UTF-8 handling belongs to file persistence and is implemented by ENG-037.

ENG-036 itself defines the JSON representation and JSON text conversion.

Round-Trip Invariant

For valid Atlas data:

Atlas Project
     ↓
Serialize
     ↓
JSON
     ↓
Deserialize
     ↓
Atlas Project'

The reconstructed Project must preserve:

Project identity
Project name
Project metadata
Classification hierarchy
Resource identity
Resource classification
Resource name
Properties
Resource metadata
Semantic Tags
Categories
Lifecycle
Relationships
Relationship endpoints
Resource Round-Trip

For a Resource:

Resource
   ↓
JSON Dictionary
   ↓
Resource

the following must remain equivalent:

AtlasID
Classification
Name
Properties
Metadata
Tags
Categories
Lifecycle
Project Round-Trip

For a Project:

Project
   ↓
JSON
   ↓
Project'

the following must remain equivalent:

Project identity
Project name
Project metadata
Classification Registry
Classification hierarchy
Resource Registry
Resource identities
Resource state
Resource Graph
Relationships
Source Immutability

Serialization must not modify the source Project or Resource.

Serialization must not:

change identity
change names
add or remove Properties
add or remove Tags
add or remove Categories
alter Metadata
alter Relationships
alter Lifecycle state

Deserialization creates new domain objects rather than mutating an unrelated
existing object.

Validation Boundary

Serialization is not validation.

The serializer is responsible for representing valid Atlas state and for
rejecting malformed serialized structures when reconstruction is impossible.

Engineering validation remains the responsibility of:

Atlas validation rules
Constraints
Project integrity mechanisms

The serializer must not silently convert invalid state into valid state.

Error Handling

The serializer must explicitly fail when it encounters invalid data such as:

Missing Project section
Missing required Project identity
Missing required Resource identity
Unknown Resource Classification
Unresolvable Classification hierarchy
Unknown Relationship endpoint
Invalid lifecycle value
Invalid JSON text
Invalid structural types

Errors must not result in partial or silently corrupted Atlas state.

Extensibility

The serialized structure must permit future Atlas evolution.

Future extensions may include:

Provenance
Geometry
Documents
External identifiers
Revision references
Change information
Additional semantic systems
Future engineering domains

New serialization fields should extend the representation without changing the
canonical Atlas identity model.

Relationship to Persistence

ENG-036 defines representation.

ENG-037 defines filesystem persistence.

The architecture is:

AtlasProject
     ↓
ENG-036
     ↓
JSON
     ↓
ENG-037
     ↓
Project File

ENG-036 must not depend on ENG-037.

Relationship to Import / Export

ENG-036 defines the canonical Atlas JSON representation.

ENG-038 defines the external exchange boundary.

The architecture is:

Atlas Project
     ↓
ENG-036
     ↓
Canonical JSON
     ↓
ENG-038 / External Adapter
     ↓
External Representation

External formats must not replace the canonical Atlas model.

Implementation Boundary

ENG-036 is implemented by:

atlas.serialization.json_serializer.AtlasJSONSerializer

The implementation exposes operations for:

Resource → Dictionary
Dictionary → Resource
Project → Dictionary
Dictionary → Project
Project → JSON text
JSON text → Project

The implementation remains independent from filesystem persistence.

Acceptance Criteria

ENG-036 is complete when:

Atlas Projects can be serialized into deterministic JSON-compatible data.
Atlas Projects can be reconstructed from serialized data.
Atlas Resource identity is preserved.
Project identity is preserved.
Classification hierarchy is preserved.
Resource Properties are preserved.
Semantic Tags are preserved.
Categories are preserved.
Lifecycle is preserved.
Metadata is preserved.
Relationships are preserved.
Relationship endpoints are reconstructed through AtlasID references.
Serialization does not recursively duplicate Resources.
Serialization does not mutate source objects.
Serialization includes version information.
Invalid serialized structures fail explicitly.
Full Atlas regression remains green.
Verification

ENG-036 implementation verification:

Focused ENG-036 tests: 47 passed
Full Atlas regression: 943 passed
Failures: 0
Errors: 0

The ENG-036 serialization contract is therefore implemented and verified.

Architectural Conclusion

ENG-036 establishes the canonical JSON representation of the Atlas model.

The fundamental boundary is:

                 Atlas Domain Model
                         │
                         ▼
                Atlas JSON Model
                         │
                         ▼
                    JSON Text

The serialized representation preserves Atlas engineering identity and meaning
without becoming a competing engineering model.

Persistence, external exchange, provenance, history, and future integrations
remain separate architectural layers.

The canonical Atlas model remains authoritative.
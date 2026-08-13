# ENG-038 — Atlas Import / Export

**Document ID:** ENG-038  
**Title:** Atlas Import / Export Boundary  
**Version:** 0.1.0  
**Status:** Draft  
**Depends On:** ENG-036, ENG-037

---

# Purpose

ENG-038 defines the generic import and export boundary of Atlas.

Import and Export allow Atlas to exchange engineering information with external
representations while preserving the Atlas canonical domain model.

The purpose of this specification is to establish an extensible adapter
architecture.

ENG-038 does not implement any specific external format.

---

# Core Principle

Atlas remains the canonical engineering model.

External representations are translated into or from Atlas.

```text
External Representation
        ↓
     Importer
        ↓
 Atlas Canonical Model

and:

Atlas Canonical Model
        ↓
     Exporter
        ↓
External Representation

External formats must not become competing canonical representations inside
Atlas.

Scope

ENG-038 defines:

Generic Importer contract
Generic Exporter contract
Import / Export result contracts
Format identification
Validation of adapter inputs
Adapter independence from Atlas core
Error propagation
Round-trip expectations where supported

ENG-038 does not define:

IFC implementation
BIM implementation
CAD implementation
Revit implementation
PDF interpretation
Excel interpretation
CSV implementation
Database adapters
Remote APIs
Synchronization
Provenance
Revision history

Those capabilities belong to future specifications.

Architectural Position

Import and Export belong outside the Atlas canonical domain model.

                    Atlas Core
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     Resources     Relationships   Semantics
        │              │              │
        └──────────────┼──────────────┘
                       │
                 Import / Export
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
      IFC             CAD           BIM
      Revit           CSV           Other

The adapter layer translates external information into Atlas concepts.

Importer Contract

An Importer represents an adapter capable of converting an external
representation into an AtlasProject.

Conceptual contract:

Importer
    ↓
External Input
    ↓
AtlasProject

An Importer should expose:

Stable format identifier
Human-readable name
Capability information
Import operation

Conceptually:

class AtlasImporter:
    format_id: str
    name: str

    def import_data(...) -> AtlasProject:
        ...

The exact concrete interface may be refined during implementation.

Exporter Contract

An Exporter represents an adapter capable of converting an AtlasProject
into an external representation.

Conceptual contract:

AtlasProject
    ↓
Exporter
    ↓
External Output

An Exporter should expose:

Stable format identifier
Human-readable name
Capability information
Export operation

Conceptually:

class AtlasExporter:
    format_id: str
    name: str

    def export_data(...) -> ...:
        ...

The exact concrete interface may be refined during implementation.

Format Identity

Every adapter must have a stable format identifier.

Examples:

atlas-json
ifc
revit
dwg
dxf
csv
pdf

The identifier is used to distinguish adapters.

Format identity must not depend on:

Python class name
Module path
UI label
Memory identity
Adapter Independence

Format-specific implementations must depend on the generic Importer or Exporter
contract rather than changing the Atlas core model.

Conceptually:

Atlas Core
    ↑
Adapter Contract
    ↑
Format Adapter

A new external format should normally be introduced by adding a new adapter,
not by modifying the canonical Resource architecture.

Import Semantics

Import transforms external information into Atlas domain objects.

The imported result may contain:

Project
Classifications
Resources
Relationships
Properties
Semantics
Metadata

The importer must construct valid Atlas domain state.

Imported information must therefore respect existing Atlas project integrity
rules.

For example:

Resource classifications must be registered before Resources are added.
Relationship endpoints must belong to the Project.
Invalid Atlas state must not be silently accepted.
Export Semantics

Export transforms the canonical Atlas model into an external representation.

Exporters must treat Atlas as the source model.

An exporter must not mutate the source project as part of normal export.

Error Handling

Import and Export must expose clear failures for:

Unsupported format
Invalid external input
Invalid Atlas state
Adapter configuration errors
Conversion failures
I/O failures

Failures must not silently produce incomplete engineering data.

Capability Model

Future adapters may support different capabilities.

Examples:

Import
Export
Partial Import
Partial Export
Geometry
Metadata
Relationships
Properties
Semantics

Capability information should be discoverable without performing a conversion.

Result Model

Import and Export may require structured results rather than returning only
the primary object.

Future results may include:

Imported Project
Exported representation
Warnings
Errors
Conversion statistics
Skipped entities
Unsupported entities

ENG-038 establishes the boundary for such structured results without requiring
full reporting functionality in v0.1.

Validation Boundary

Imported data must pass through Atlas's existing project/domain integrity
mechanisms.

The importer is responsible for translation.

Atlas remains responsible for canonical validity.

Conceptually:

External Data
      ↓
Translation
      ↓
Atlas Project
      ↓
Atlas Integrity
      ↓
Validation / Constraints

Importers must not replace Atlas validation with format-specific assumptions.

Export Boundary

Exporters may transform Atlas semantics to fit an external format.

However, the Atlas model remains authoritative.

An exporter must not modify Atlas merely because the target format has different
constraints.

Round-Trip Principle

Where an external format supports sufficient information, the following should
be possible:

Atlas
  ↓
Export
  ↓
External Representation
  ↓
Import
  ↓
Atlas'

Atlas' should preserve the information supported by both directions.

Exact equality is not universally required because external formats may be
lossy or structurally different.

Lossy Conversion

Adapters may be lossy.

When information cannot be represented by the target format, the adapter must
not silently redefine the Atlas model.

Future implementations may report:

Unsupported properties
Unsupported relationships
Unsupported semantics
Geometry loss
Metadata loss
Source Immutability

Export must not mutate the source AtlasProject.

Import must construct a new AtlasProject rather than mutating an unrelated
existing Project.

Security / Trust Boundary

External representations are untrusted input.

Future adapters must validate and safely interpret external data before creating
Atlas domain state.

ENG-038 does not prescribe a security implementation, but the adapter boundary
must be treated as a trust boundary.

Extensibility

Adding support for a new format should require adding an adapter rather than
changing:

AtlasResource
AtlasRelationship
AtlasProject
AtlasResourceGraph
Atlas validation core

unless the external format exposes a genuine missing Atlas capability.

Non-Goals

ENG-038 does not implement:

IFC
BIM
Revit
CAD
DWG
DXF
PDF
Excel
CSV
GIS
External APIs
Remote synchronization
Provenance
Revision history
Change impact analysis
Acceptance Criteria

ENG-038 is complete when:

Atlas has a generic Importer boundary.
Atlas has a generic Exporter boundary.
Formats have stable identifiers.
Format adapters are independent of Atlas core internals.
Import produces valid Atlas domain state.
Export does not mutate the source Project.
Adapter failures are explicit.
Capability discovery is possible.
The architecture supports multiple future external formats.
No format-specific implementation is required for ENG-038.
Existing Atlas functionality remains unaffected.
Full regression remains green.
Architectural Conclusion

Import / Export is an integration boundary around the canonical Atlas model.

                 Atlas Canonical Model
                         │
               ┌─────────┴─────────┐
               ↓                   ↓
            Import               Export
               ↓                   ↓
      External → Atlas       Atlas → External

Future engineering systems should connect through this boundary rather than
creating competing representations of engineering reality.

The canonical Atlas model remains authoritative.
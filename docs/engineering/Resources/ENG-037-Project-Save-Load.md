# ENG-037 — Project Save / Load

**Document ID:** ENG-037
**Title:** Atlas Project Save / Load
**Version:** 0.1.0
**Status:** Draft
**Depends On:** ENG-036

---

# Purpose

ENG-037 defines file persistence for an `AtlasProject`.

The specification provides a thin file-system boundary over the canonical
Atlas JSON serialization defined by ENG-036.

The save/load subsystem must not implement domain serialization itself.

---

# Architecture

```text
AtlasProject
     ↓
AtlasJSONSerializer
     ↓
JSON text
     ↓
Project File

Loading reverses the same flow:

Project File
     ↓
JSON text
     ↓
AtlasJSONSerializer
     ↓
AtlasProject
Responsibilities

ENG-037 is responsible for:

Opening and writing project files
Reading project files
Encoding and decoding UTF-8 text
Handling filesystem errors
Applying explicit overwrite policy
Delegating representation to AtlasJSONSerializer

ENG-037 is not responsible for:

Resource serialization
Relationship serialization
Classification reconstruction
Property serialization
Semantic serialization
Lifecycle reconstruction

Those responsibilities belong to ENG-036.

File Format

The project file contains the canonical JSON representation produced by
AtlasJSONSerializer.

ENG-037 does not define a second file schema.

Encoding

Project files must use UTF-8 text encoding.

Save Contract

Saving a project must:

Serialize the project through AtlasJSONSerializer.
Produce UTF-8 JSON text.
Write the complete representation to the target path.
Preserve the project identity and state.
Not mutate the source project.
Overwrite Policy

The save API must make overwrite behavior explicit.

Default behavior must prevent accidental overwriting of an existing file.

An explicit overwrite option may permit replacement.

Load Contract

Loading a project must:

Read the complete file as UTF-8 text.
Delegate JSON interpretation to AtlasJSONSerializer.
Return a reconstructed AtlasProject.

Loading must not mutate an existing project instance.

Error Behavior

The persistence boundary must expose clear errors for:

Missing files
Invalid JSON
Invalid Atlas project data
Unsupported or invalid serialization versions
Invalid paths
Filesystem write failures
Attempted overwrite without explicit permission

Errors should not silently produce partial projects.

Round-Trip Invariant

For a valid project:

Project
   ↓ save
File
   ↓ load
Project'

The following must remain equivalent:

Project identity
Project name
Project metadata
Classifications
Classification hierarchy
Resources
Resource identities
Properties
Semantic tags
Categories
Lifecycle
Relationships
Relationship endpoints
Determinism

Saving the same unchanged project through the same serializer must produce
deterministically equivalent file contents.

Immutability

Neither saving nor loading may mutate an existing source project.

Architectural Boundary

ENG-037 must remain a file persistence layer.

The dependency direction is:

ENG-037
   ↓
ENG-036
   ↓
Atlas Domain Model

ENG-036 must not depend on ENG-037.

Acceptance Criteria

ENG-037 is complete when:

A valid AtlasProject can be saved to a file.
A saved project can be loaded back.
Round-trip identity is preserved.
Round-trip Resources are preserved.
Round-trip Relationships are preserved.
Classification hierarchy is preserved.
UTF-8 is used consistently.
Saving does not mutate the source project.
Loading produces a new project instance.
Existing files cannot be overwritten accidentally.
Explicit overwrite works.
Missing and invalid files produce clear errors.
ENG-037 delegates representation to ENG-036.
Full regression remains green.
Non-Goals

ENG-037 does not implement:

Import
Export
Database storage
Remote storage
Distributed persistence
File synchronization
Version migration
Provenance
Revision history
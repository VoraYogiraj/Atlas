# ENG-002 — Resource Identity

**Document ID:** ENG-002  
**Title:** Resource Identity  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** YYYY-MM-DD  
**Last Updated:** YYYY-MM-DD  
**Reviewers:** TBD  
**Depends On:** ENG-001 — Atlas Resource

---

# Purpose

This specification defines the identity model for Atlas Resources.

Resource Identity provides every Atlas Resource with a globally unique, stable, and persistent identity throughout its lifecycle.

Identity enables Atlas to distinguish Resources independently of their names, properties, classifications, or relationships.

It forms the foundation for traceability, interoperability, collaboration, versioning, and AI reasoning.

---

# Scope

This specification defines:

- Resource Identity
- Identity lifecycle
- Identity characteristics
- Identity types
- Identity constraints
- Identity usage
- Identity responsibilities

This specification does not define:

- Resource classification
- Resource properties
- Relationships
- Validation
- Serialization

These are covered by separate Engineering Specifications.

---

# Definition

A **Resource Identity** is the permanent identifier assigned to an Atlas Resource.

Identity uniquely distinguishes one Atlas Resource from every other Resource within the Atlas ecosystem.

Identity exists independently of:

- Name
- Display Name
- Classification
- Properties
- Geometry
- Relationships
- Metadata

Identity never changes during the lifetime of a Resource.

---

# Design Goals

The Resource Identity model is designed to provide:

- Global uniqueness
- Persistence
- Stability
- Traceability
- Interoperability
- Machine readability
- Human usability
- AI compatibility

---

# Identity Principles

## Principle 1 — Identity Is Permanent

Once assigned, a Resource Identity shall never change.

A Resource may evolve, but its identity remains constant.

---

## Principle 2 — Identity Is Unique

No two Atlas Resources may share the same identity.

Uniqueness must be guaranteed across the entire Atlas ecosystem.

---

## Principle 3 — Identity Is Independent

Identity is independent of every other Resource characteristic.

Changing a Resource's:

- Name
- Properties
- Geometry
- Relationships
- Classification

does not affect its identity.

---

## Principle 4 — Identity Is Immutable

Identity is immutable.

Resources may be archived or deprecated, but their identities are never reassigned.

---

## Principle 5 — Identity Enables References

Resources should reference one another using Resource Identity rather than human-readable names.

Names may change.

Identity does not.

---

# Identity Model

Every Atlas Resource has three complementary identities.

---

## 1. System Identity

Used internally by Atlas.

Characteristics:

- Globally unique
- Machine-readable
- Immutable
- Persistent

Example:

```
ar_01J2XZ7B3P7RQFQ2A8V9T4N6XK
```

The exact encoding format is implementation-defined and may evolve.

---

## 2. Human Identity

Used by engineers and users.

Examples:

- Wall W-101
- Door D-015
- Room R-203

Human Identity improves readability but is not used as the primary system reference.

Human Identity may change.

---

## 3. Semantic Identity

Represents the engineering meaning of a Resource.

Example:

```
Physical Resource
    ↓
Building Element
        ↓
Wall
            ↓
Exterior Wall
```

Semantic Identity enables intelligent reasoning and classification.

Semantic Identity is defined further in ENG-006.

---

# Identity Lifecycle

Every Resource Identity follows the same lifecycle.

```
Generate

↓

Assign

↓

Reference

↓

Maintain

↓

Archive
```

Identity is never modified.

Only its associated Resource evolves.

---

# Identity Usage

Resource Identity is used for:

- Resource references
- Relationship definitions
- Version tracking
- Serialization
- Import and export
- Synchronization
- Collaboration
- AI reasoning
- Knowledge graphs
- APIs

Identity should never depend on display names.

---

# Identity Constraints

Every Resource Identity shall:

- Be globally unique.
- Remain immutable.
- Exist for the lifetime of the Resource.
- Never be reused.
- Be independent of implementation details.
- Support distributed systems.
- Support offline creation.
- Support future interoperability.

---

# Identity Responsibilities

Resource Identity is responsible only for identifying a Resource.

Identity is not responsible for:

- Classification
- Properties
- Validation
- Geometry
- Relationships
- Metadata

Each concern is addressed by its own Engineering Specification.

---

# Examples

## Example 1

```
System Identity

ar_01J2XZ7B3P7RQFQ2A8V9T4N6XK
```

Human Identity

```
Bedroom Wall
```

Semantic Identity

```
Physical Resource

↓

Wall

↓

Interior Wall
```

---

## Example 2

The Resource is renamed.

Before:

```
Bedroom Wall
```

After:

```
North Bedroom Wall
```

System Identity remains unchanged.

References remain valid.

AI reasoning remains valid.

---

# Future Evolution

Future versions of Atlas may introduce:

- Federated identity
- Cross-organization identity
- Identity namespaces
- Digital signatures
- Resource ownership
- Identity verification

These additions must preserve the fundamental principles defined in this specification.

---

# Relationship to Other Specifications

This specification is related to:

- ENG-001 — Atlas Resource
- ENG-003 — Resource Classification
- ENG-005 — Resource Relationships
- ENG-009 — Resource Serialization
- ENG-010 — Atlas Resource Registry

---

# Closing Statement

Identity is the foundation of continuity.

Names may change.

Properties may evolve.

Relationships may expand.

Knowledge may grow.

But an Atlas Resource remains the same Resource because its identity remains constant.
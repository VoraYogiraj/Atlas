# ENG-008 — Resource Validation

**Document ID:** ENG-008
**Title:** Resource Validation
**Version:** 0.1.0
**Status:** Draft
**Owner:** Project Atlas
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Reviewers:** TBD
**Depends On:** ENG-001, ENG-002, ENG-003, ENG-004, ENG-005, ENG-006, ENG-007

---

# Purpose

This specification defines the Resource Validation Model used throughout Atlas.

Validation ensures that Atlas Resources are complete, consistent, accurate, and compliant with engineering rules before they are used by people, AI agents, or external systems.

Validation improves engineering quality while providing transparent and explainable feedback.

---

# Scope

This specification defines:

- Validation principles
- Validation categories
- Validation rules
- Validation severity
- Validation results
- Validation responsibilities

This specification does not define:

- Approval workflows
- Business processes
- User permissions
- Regulatory compliance engines

These concerns are specified separately.

---

# Definition

Resource Validation is the process of evaluating an Atlas Resource against defined engineering rules.

Validation determines whether a Resource satisfies the requirements expected for its classification, properties, relationships, semantics, and lifecycle.

Validation evaluates engineering quality.

It does not modify the Resource.

---

# Design Goals

The Resource Validation Model is designed to provide:

- Engineering correctness
- Data consistency
- Explainability
- Early error detection
- AI confidence
- Interoperability
- Trust

---

# Validation Principles

## Principle 1 — Validation Never Changes a Resource

Validation observes.

It does not modify.

Atlas may recommend corrections, but validation itself never alters engineering information.

---

## Principle 2 — Validation Is Explainable

Every validation result must explain:

- What was checked
- Why it matters
- What failed
- How it can be resolved

Validation should educate rather than simply reject.

---

## Principle 3 — Validation Is Rule-Based

Every validation result must be traceable to one or more explicit engineering rules.

Atlas should never report unexplained validation failures.

---

## Principle 4 — Validation Is Context Aware

Validation considers:

- Resource Classification
- Properties
- Relationships
- Semantics
- Lifecycle Stage

Different Resources may require different validation rules.

---

## Principle 5 — Validation Is Extensible

Organizations may introduce additional validation rules without changing the Atlas Validation Model.

---

# Validation Categories

Atlas supports multiple validation categories.

---

## Identity Validation

Checks:

- Identity exists
- Identity uniqueness
- Identity integrity

---

## Classification Validation

Checks:

- Valid classification
- Supported classification
- Classification hierarchy

---

## Property Validation

Checks:

- Required properties
- Property types
- Units
- Allowed ranges
- Constraints

---

## Relationship Validation

Checks:

- Valid references
- Relationship integrity
- Cardinality
- Missing dependencies

---

## Semantic Validation

Checks:

- Engineering consistency
- Meaning completeness
- Context consistency

---

## Lifecycle Validation

Checks:

- Valid lifecycle stage
- Allowed transitions
- Historical consistency

---

## Custom Validation

Organizations may define additional engineering validation rules.

---

# Validation Severity

Validation results are classified into four levels.

---

## Information

Provides useful engineering observations.

No action required.

---

## Warning

Potential engineering issue.

Review recommended.

---

## Error

Engineering inconsistency detected.

Correction required before proceeding.

---

## Critical

Resource integrity is compromised.

Immediate correction required.

Critical validation failures may prevent further processing.

---

# Validation Result

Every validation result should include:

- Validation ID
- Resource ID
- Validation Category
- Severity
- Rule
- Message
- Explanation
- Suggested Resolution
- Timestamp

---

# Validation Workflow

```
Resource

↓

Validation Rules

↓

Validation Engine

↓

Results

↓

User / AI Review

↓

Correction (if required)
```

Validation itself never performs corrections.

---

# Validation Responsibilities

The Validation Model is responsible for:

- Detecting engineering inconsistencies
- Supporting engineering quality
- Providing explainable feedback
- Supporting AI reasoning
- Improving interoperability
- Increasing engineering confidence

Validation is not responsible for:

- Editing Resources
- Approving Resources
- Executing workflows
- Assigning responsibilities

---

# Examples

## Example 1

Resource:

```
Wall
```

Validation:

```
Error

Required Property Missing

Height has not been specified.
```

---

## Example 2

Resource:

```
Door
```

Validation:

```
Warning

Door Width is below recommended minimum.
```

---

## Example 3

Resource:

```
HVAC Unit
```

Validation:

```
Critical

Required electrical connection is missing.
```

---

## Example 4

Resource:

```
Specification Document
```

Validation:

```
Information

Revision history is complete.
```

---

# AI-Assisted Validation

Atlas Intelligence may provide:

- Suggested corrections
- Engineering explanations
- Related standards
- Similar Resources
- Alternative solutions

AI recommendations are advisory.

Final engineering decisions remain under human control unless explicitly delegated.

---

# Future Evolution

Future versions of Atlas may introduce:

- Real-time validation
- Distributed validation
- Regulatory validation packs
- Simulation-assisted validation
- Predictive validation
- Organization-specific validation profiles

The core Validation Model remains stable.

---

# Relationship to Other Specifications

Related specifications include:

- ENG-001 — Atlas Resource
- ENG-003 — Resource Classification
- ENG-004 — Resource Properties
- ENG-005 — Resource Relationships
- ENG-006 — Resource Semantics
- ENG-007 — Resource Lifecycle
- ENG-009 — Resource Serialization

---

# Closing Statement

Validation builds trust.

It confirms that a Resource is complete, consistent, and meaningful.

Atlas does not validate to reject engineering work.

Atlas validates to improve engineering quality through transparent, explainable, and actionable feedback.
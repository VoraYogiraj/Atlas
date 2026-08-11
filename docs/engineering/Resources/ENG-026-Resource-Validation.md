# ENG-026 — Resource Validation

**Document ID:** ENG-026
**Title:** Resource Validation Runtime Model
**Version:** 0.1.0
**Status:** Draft
**Owner:** Project Atlas
**Created:** 2026-08-11
**Last Updated:** 2026-08-11
**Reviewers:** TBD
**Depends On:** ENG-001, ENG-003, ENG-004, ENG-005, ENG-006, ENG-007, ENG-008

---

# Purpose

This specification defines the runtime model for Resource Validation in
Atlas.

ENG-008 defines the conceptual Resource Validation Model.

ENG-026 defines the minimal runtime structures required to represent:

- Validation Categories
- Validation Severity
- Validation Rules
- Validation Results
- Validation Execution

The runtime model provides the foundation for future engineering validation
rules without embedding specific engineering rules into the validation
engine itself.

---

# Scope

This specification defines:

- Validation Category
- Validation Severity
- Validation Result
- Validation Rule
- Validation Engine
- Rule registration
- Validation execution
- Validation result collection
- Validation immutability
- Validation explainability

This specification does not define:

- Specific engineering validation rules
- Regulatory compliance engines
- Approval workflows
- User permissions
- Business workflows
- Automatic correction
- AI-generated validation rules
- Serialization
- Distributed validation

---

# Validation Model

Atlas validation follows the following model:

```text
Atlas Resource
      |
      v
Validation Rules
      |
      v
Validation Engine
      |
      v
Validation Results
      |
      v
User / AI Review

Validation observes a Resource.

Validation does not modify a Resource.

Validation Categories

Atlas defines the following validation categories.

IDENTITY
CLASSIFICATION
PROPERTY
RELATIONSHIP
SEMANTIC
LIFECYCLE
CUSTOM

These correspond to the validation categories defined by ENG-008.

A validation rule shall belong to exactly one validation category.

Validation Severity

Atlas defines four validation severity levels.

INFORMATION
WARNING
ERROR
CRITICAL

Severity represents the significance of a validation result.

Information

Provides useful engineering observations.

No action is required.

Warning

Indicates a potential engineering issue.

Review is recommended.

Error

Indicates an engineering inconsistency.

Correction is required before proceeding.

Critical

Indicates compromised Resource integrity.

Immediate correction is required.

Critical validation failures may prevent further processing.

Validation Category Model

A validation category is represented by:

AtlasValidationCategory

The category shall be an enumeration.

The enumeration shall expose:

IDENTITY
CLASSIFICATION
PROPERTY
RELATIONSHIP
SEMANTIC
LIFECYCLE
CUSTOM

The enumeration values shall use lowercase string values:

identity
classification
property
relationship
semantic
lifecycle
custom
Validation Severity Model

Validation severity is represented by:

AtlasValidationSeverity

The severity shall be an enumeration.

The enumeration shall expose:

INFORMATION
WARNING
ERROR
CRITICAL

The enumeration values shall use lowercase string values:

information
warning
error
critical

Severity ordering shall be:

INFORMATION
    <
WARNING
    <
ERROR
    <
CRITICAL

The ordering represents increasing validation significance.

Validation Result

A validation result represents one validation finding.

A result shall contain:

AtlasValidationResult
│
├── id
├── resource_id
├── category
├── severity
├── rule
├── message
├── explanation
├── suggested_resolution
└── timestamp

These fields correspond to the validation result information defined by
ENG-008.

Validation Result Identity

Every validation result shall have a unique validation ID.

The validation ID identifies the result itself.

The Resource ID identifies the Resource that was evaluated.

These identities are independent.

Resource Identity

The resource_id field shall contain the Resource's Atlas identity.

Validation results must therefore be traceable back to the Resource that
produced them.

Validation Rule

A validation rule represents an explicit engineering check.

A rule shall contain:

AtlasValidationRule
│
├── id
├── category
└── validate(resource)

The rule ID shall uniquely identify the rule.

The rule category identifies which validation category the rule belongs to.

The validate() operation evaluates a Resource and returns zero or more
validation results.

A rule shall not modify the Resource.

Validation Rule Contract

A validation rule shall provide:

rule.id
rule.category
rule.validate(resource)

The validation engine shall treat the rule as an explicit source of
validation logic.

Validation results must therefore be traceable to a rule.

Validation Engine

The validation engine is represented by:

AtlasValidationEngine

The engine manages registered validation rules and executes them against
Resources.

The engine shall support:

register_rule()
unregister_rule()
rules
validate()
Rule Registration

Rules shall be explicitly registered with the Validation Engine.

Example:

engine = AtlasValidationEngine()

engine.register_rule(rule)

A rule with an existing rule ID shall not be registered twice.

Duplicate registration shall raise:

ValueError
Rule Removal

The engine shall support removal of a rule by ID.

Example:

engine.unregister_rule("required-height")

Removing a missing rule shall return:

None

Removing an existing rule shall return the removed rule.

Rule Lookup

The engine shall support lookup by rule ID.

Example:

engine.get_rule("required-height")

A missing rule shall return:

None
Rule Collection

The engine shall expose registered rules through:

rules

Rules shall preserve registration order.

The returned collection shall not expose the engine's internal mutable
storage.

Validation Execution

The engine shall support:

engine.validate(resource)

Validation executes all registered rules against the Resource.

The engine returns a collection of:

AtlasValidationResult

Results shall preserve rule execution order.

Empty Validation

If no rules are registered:

engine.validate(resource)

shall return an empty result collection.

Validation of a Resource with no registered rules shall not modify the
Resource.

Multiple Rules

Multiple rules may evaluate the same Resource.

Example:

Resource
   |
   +-- Required Height Rule
   |
   +-- Required Width Rule
   |
   +-- Lifecycle Rule
   |
   +-- Relationship Rule

Each rule may produce zero or more validation results.

Validation Result Ordering

Validation results shall preserve the order in which rules are executed.

If:

Rule A
Rule B
Rule C

are registered in that order, their results shall appear in:

Rule A results
Rule B results
Rule C results

order.

Non-Mutating Validation

Validation shall never modify:

Resource identity
Resource classification
Resource properties
Resource relationships
Resource metadata
Resource semantic tags
Resource categories
Resource lifecycle

A validation engine must therefore be observational.

Explainability

Every validation result shall identify:

What was checked through the rule
Why the result matters through the explanation
What failed through the message
How the issue may be resolved through the suggested resolution

Validation results shall therefore remain explainable.

Validation Result Immutability

Validation results shall be immutable after creation.

The following fields shall not change:

ID
Resource ID
Category
Severity
Rule
Message
Explanation
Suggested Resolution
Timestamp

If a different result is required, a new validation result shall be created.

Validation Rule Immutability

Validation rules shall be immutable definitions.

A rule's:

ID
Category

shall not change after creation.

Validation Engine Independence

The Validation Engine shall not own or modify Resources.

Resources remain independent objects.

The engine only evaluates Resources through registered rules.

Future Resource Integration

ENG-026 v0.1 does not require AtlasResource to expose a direct
validate() method.

Validation is performed explicitly through:

engine.validate(resource)

Future versions may provide Resource-level convenience APIs without
changing the underlying validation model.

Validation Failure Handling

A validation failure represented by a rule shall produce a validation
result.

The engine shall not automatically modify the Resource in response to a
validation result.

The engine shall not automatically:

fix properties
change classifications
change relationships
change lifecycle
remove tags
remove categories
Validation Architecture

The v0.1 implementation shall use the following package structure:

atlas/
└── validation/
    ├── __init__.py
    ├── category.py
    ├── severity.py
    ├── result.py
    ├── rule.py
    └── engine.py

The package shall expose:

AtlasValidationCategory
AtlasValidationSeverity
AtlasValidationResult
AtlasValidationRule
AtlasValidationEngine
Example

A required-height rule may conceptually operate as follows:

Resource
    |
    v
Required Height Rule
    |
    v
Height missing
    |
    v
Validation Result

Result:

Category:
PROPERTY

Severity:
ERROR

Rule:
required-height

Message:
Required property missing.

Explanation:
Height is required for this Resource.

Suggested Resolution:
Specify the Resource height.

The rule reports the problem.

It does not add the missing property.

Relationship to ENG-008

ENG-008 defines the conceptual Resource Validation Model.

ENG-026 defines its initial runtime representation.

ENG-008 remains the authoritative specification for:

Validation purpose
Validation principles
Validation categories
Validation severity
Validation result information
Validation responsibilities
Validation workflow

ENG-026 defines the runtime contracts required to implement those concepts.

Future Evolution

Future versions may introduce:

Built-in engineering rules
Rule registries
Rule dependencies
Rule priorities
Validation profiles
Project-specific rules
Organization-specific rules
Regulatory validation
Parallel validation
Incremental validation
AI-assisted validation
Validation history
Validation persistence
Validation reporting

These capabilities are outside the scope of ENG-026 v0.1.

Closing Statement

ENG-026 provides the runtime foundation for Atlas Resource Validation.

Validation Rules define what is checked.

The Validation Engine executes those rules.

Validation Results explain what was discovered.

Validation never modifies the Resource.

This establishes an explicit, extensible, and explainable foundation for
future engineering validation intelligence.


## Important architectural decision

Notice that I have **not** added `validate()` to `AtlasResource`.

The specification explicitly allows validation to remain external:

```python
engine.validate(resource)

That keeps validation independent from the Resource itself and matches ENG-008's principle that validation observes rather than modifies.
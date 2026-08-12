# ENG-027 — Property Constraints & Unit-Aware Evaluation

**Document ID:** ENG-027  
**Title:** Property Constraints & Unit-Aware Evaluation  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-004, ENG-008, ENG-026

---

# Purpose

This specification defines the runtime model for engineering constraints
applied to Atlas Resource Properties.

Constraints represent requirements that a Resource is expected to satisfy.

Constraints are evaluated through the Atlas Validation Model.

ENG-027 does not define universal engineering values.

Constraint values may vary according to:

- Project
- Resource classification
- Engineering discipline
- Applicable standard
- Jurisdiction
- Project requirements
- Organization rules
- Engineering context

---

# Scope

This specification defines:

- Property constraints
- Constraint identity
- Constraint operators
- Expected values
- Expected units
- Unit compatibility
- Unit conversion
- Constraint context
- Constraint source
- Constraint evaluation
- Validation integration

This specification does not define:

- Regulatory databases
- Building-code rule packs
- Automatic engineering inference
- Approval workflows
- Constraint optimization
- AI-generated constraints
- Persistent constraint registries
- Constraint versioning

---

# Definition

A Constraint is an explicit engineering requirement against a Resource
Property.

A Constraint answers:

> "What condition must this property satisfy?"

Example:

```text
Wall Height >= 2400 mm

The Constraint defines the requirement.

The current Resource Property provides the actual value.

Validation determines whether the requirement is satisfied.

Constraint and Validation

Constraints are not independent validation systems.

The architecture is:

Property
    +
Constraint
    |
    v
Constraint Evaluation
    |
    v
Validation Result

ENG-026 remains responsible for validation results.

ENG-027 defines how property constraints are represented and evaluated.

Constraint Independence

A Constraint shall not assume that one engineering value is universally
valid.

For example:

Project A:
Wall Height >= 2400 mm

Project B:
Wall Height >= 2700 mm

Both constraints may be valid in their respective contexts.

Therefore, engineering values must remain data defined by the applicable
constraint rather than being hard-coded into AtlasProperty.

Constraint Model

A Constraint consists of:

Constraint
│
├── id
├── property_id
├── operator
├── expected_value
├── expected_unit
├── context
├── source
└── severity
Constraint Identity

Every Constraint shall have a stable identifier.

The identifier identifies the specific requirement.

Two Constraints with different IDs represent different requirements even
when they target the same Property.

Property Reference

A Constraint shall reference a Resource Property using its Property ID.

Example:

property_id = "height"

A Constraint therefore evaluates a specific Property rather than an
arbitrary Resource field.

Constraint Operators

ENG-027 v0.1 shall support:

EQUAL
NOT_EQUAL
GREATER_THAN
GREATER_THAN_OR_EQUAL
LESS_THAN
LESS_THAN_OR_EQUAL
IN
NOT_IN
MATCHES

Examples:

height >= 2400 mm

temperature < 45 °C

material IN ["AAC", "Brick"]

material MATCHES "^AAC.*"
Expected Value

The expected value represents the requirement defined by the Constraint.

Examples:

2400
3000
"Brick"
["AAC", "Brick"]
"^AAC.*"

The interpretation of expected_value depends on the operator.

Units

Measurement Constraints shall explicitly define their expected unit.

Example:

expected_value = 2400
expected_unit = "mm"

Atlas shall never silently assume a measurement unit.

Unit Conversion

Compatible units shall be convertible during Constraint evaluation.

Examples:

mm ↔ cm
mm ↔ m
mm ↔ in
mm ↔ ft
cm ↔ m
m ↔ ft
in ↔ ft

Equivalent measurements shall produce equivalent evaluation results.

Example:

Constraint:
Height >= 2400 mm

Property:
Height = 2.4 m

The Constraint shall evaluate successfully because:

2.4 m == 2400 mm
Unit Independence

Changing the project's preferred display or input unit shall not alter
the engineering meaning of a Constraint.

Example:

Constraint:
Height >= 2400 mm

may be displayed as:

2.4 m

or:

94.488 in

without changing the underlying requirement.

Unit Compatibility

Only compatible physical dimensions may be converted.

Examples:

3000 mm ↔ 3 m

is valid.

3000 mm ↔ 9.84 ft

is valid.

3000 mm ↔ 50 kg

is invalid.

3000 mm ↔ 20 °C

is invalid.

Incompatible units shall raise a validation/evaluation error rather than
performing an arbitrary conversion.

Canonical Evaluation

Constraint evaluation shall normalize compatible measurement values into a
common representation before comparison.

For example:

Property:
3000 mm

Constraint:
>= 2.5 m

may be normalized to:

3000 mm >= 2500 mm

The conversion is an evaluation operation.

It does not rewrite the stored Property or Constraint.

Stored Values

Constraint evaluation shall not mutate:

Property value
Property unit
Constraint expected value
Constraint expected unit

Conversion exists only for comparison.

Context

A Constraint may contain contextual information describing where or why
the requirement applies.

Context may include:

Project
Discipline
Building type
Resource classification
Jurisdiction
Organization
Design stage

Context is descriptive in ENG-027 v0.1.

Automatic context matching is outside the scope of this version.

Source

A Constraint may identify its engineering source.

Examples:

Project Standard
IS Code
Local Regulation
Organization Standard
Design Requirement
Client Requirement

The source is explanatory metadata and does not itself execute the
Constraint.

Severity

A Constraint may specify the Validation Severity to use when the
Constraint is violated.

Example:

severity = ERROR

ENG-026 remains responsible for producing the final Validation Result.

Constraint Result

A Constraint evaluation shall produce one of:

SATISFIED
VIOLATED
NOT_EVALUABLE
SATISFIED

The current Resource Property satisfies the Constraint.

Example:

Constraint:
Height >= 2400 mm

Property:
Height = 3000 mm

Result:

SATISFIED
VIOLATED

The current Resource Property does not satisfy the Constraint.

Example:

Constraint:
Height >= 2400 mm

Property:
Height = 2100 mm

Result:

VIOLATED

The evaluator shall not modify the Property.

NOT_EVALUABLE

A Constraint is NOT_EVALUABLE when Atlas cannot safely evaluate it.

Examples:

Required Property is missing
Value is incompatible with expected type
Units are incompatible
Required context is unavailable

NOT_EVALUABLE shall not be silently treated as SATISFIED.

Constraint Evaluation

Constraint evaluation shall be deterministic for the same:

Property Value
Property Unit
Constraint
Context

Repeated evaluation of the same inputs shall produce the same logical
result.

Constraint Integration with Validation

Constraint violations shall integrate with ENG-026.

Example:

Constraint:
Height >= 2400 mm

Property:
Height = 2100 mm

Constraint evaluation:

VIOLATED

Validation:

Category:
PROPERTY

Severity:
ERROR

Rule:
constraint:wall-height-minimum

Message:
Property constraint violated.

Explanation:
Wall Height must be at least 2400 mm.

Suggested Resolution:
Increase the Wall Height to satisfy the project requirement.
Constraint Attachment

ENG-027 v0.1 shall support constraints as explicit definitions associated
with Resource Properties.

The implementation shall not require a global Constraint Registry.

Project-level and organization-level Constraint Registries may be
introduced in future versions.

Multiple Constraints

A single Property may have multiple Constraints.

Example:

Height >= 2400 mm
Height <= 4200 mm

Both Constraints may be evaluated independently.

Constraint Independence

Constraints do not modify:

Resource identity
Classification
Properties
Relationships
Semantic Tags
Categories
Lifecycle

Constraint evaluation is observational.

Property Types

Constraint evaluation shall respect the Property data type.

Examples:

Numeric:

Height >= 2400 mm

Enumeration:

Material IN ["AAC", "Brick"]

String:

Material MATCHES "^AAC.*"

A Constraint that is incompatible with the Property data type shall be
NOT_EVALUABLE.

Enumeration Constraints

The IN and NOT_IN operators may evaluate enumeration-like values.

Example:

Material IN ["AAC", "Brick", "Concrete"]
Regular Expression Constraints

The MATCHES operator may evaluate string values using regular expressions.

Regex constraints apply only to string-compatible Property values.

A regex applied to an incompatible Property type shall be
NOT_EVALUABLE.

Dependency Constraints

Dependency rules are outside the core scalar comparison model.

ENG-027 v0.1 reserves dependency constraints for future extension.

Examples include:

If Fire Rating >= 2 Hours
then Fire Door Type must be specified.

Dependency evaluation may be introduced in a future version without
changing the fundamental Constraint model.

Error Handling

The evaluator shall reject:

Unknown operators
Invalid units
Incompatible units
Invalid expected values
Unsupported type/operator combinations

Errors shall never result in silent acceptance of a Constraint.

Architecture

The v0.1 architecture is:

AtlasProperty
      |
      v
AtlasConstraint
      |
      v
ConstraintEvaluator
      |
      v
ConstraintEvaluation
      |
      v
AtlasValidationRule
      |
      v
AtlasValidationEngine
      |
      v
AtlasValidationResult
Proposed Package Structure
atlas/
└── constraints/
    ├── __init__.py
    ├── constraint.py
    ├── operator.py
    ├── result.py
    └── evaluator.py

The initial public API shall expose:

AtlasConstraint
AtlasConstraintOperator
AtlasConstraintResult
AtlasConstraintEvaluator
Unit System

ENG-027 v0.1 shall support explicit unit conversion for common engineering
length units:

mm
cm
m
in
ft

Additional units may be added in future versions.

The conversion system shall be extensible.

Future Evolution

Future versions may introduce:

Area units
Volume units
Mass units
Temperature units
Force units
Pressure units
Energy units
Compound engineering units
Unit dimension registry
Project unit systems
Unit formatting
Automatic unit suggestions
Constraint registries
Constraint inheritance
Constraint precedence
Jurisdiction-specific rules
Standard-specific rules
Dependency constraints
Constraint composition
AND / OR logic
Conditional constraints
Time-dependent constraints
Relationship to Other Specifications

ENG-027 depends on:

ENG-004 — Resource Properties
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model

ENG-004 defines Properties.

ENG-008 defines Validation.

ENG-026 defines the Validation runtime.

ENG-027 defines Property Constraints and their unit-aware evaluation.

Closing Statement

Constraints represent engineering requirements.

Properties represent current engineering information.

Validation evaluates whether the current information satisfies the
requirements.

Units must remain explicit, compatible, and convertible without changing
engineering meaning.

Atlas therefore separates:

Requirement
    ↓
Constraint

Current Information
    ↓
Property

Evaluation
    ↓
Validation

This separation allows different projects, standards, jurisdictions, and
engineering contexts to define different requirements while preserving a
stable Atlas Resource model.


This is the architecture I'd use as the starting point.

One thing I deliberately **did not** do is put `minimum`, `maximum`, or a universal engineering value directly onto `AtlasProperty`. The constraint is a separate requirement, which lets Project A and Project B impose different requirements on the same property.

Also, **unit conversion does not rewrite stored data**. It happens during comparison.
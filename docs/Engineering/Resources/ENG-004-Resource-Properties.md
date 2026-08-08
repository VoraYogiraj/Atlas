# ENG-004 — Resource Properties

**Document ID:** ENG-004  
**Title:** Resource Properties  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** YYYY-MM-DD  
**Last Updated:** YYYY-MM-DD  
**Reviewers:** TBD  
**Depends On:** ENG-001 — Atlas Resource, ENG-002 — Resource Identity, ENG-003 — Resource Classification

---

# Purpose

This specification defines the Resource Property Model used throughout Atlas.

Resource Properties describe the measurable, descriptive, and behavioral characteristics of an Atlas Resource.

Properties provide the information required for engineering workflows, semantic understanding, validation, interoperability, and intelligent reasoning.

---

# Scope

This specification defines:

- Resource Properties
- Property categories
- Property inheritance
- Property characteristics
- Property constraints
- Property responsibilities

This specification does not define:

- Resource Identity
- Resource Classification
- Resource Relationships
- Resource Semantics
- Resource Validation

These concepts are defined in separate Engineering Specifications.

---

# Definition

A **Resource Property** is a characteristic associated with an Atlas Resource.

Properties describe the Resource without changing its identity.

Properties answer questions such as:

- What are its dimensions?
- What material is it made of?
- What is its status?
- Who manufactured it?
- What performance does it provide?

---

# Design Goals

The Resource Property Model is designed to provide:

- Engineering precision
- Flexibility
- Extensibility
- Reusability
- Validation support
- AI compatibility
- Interoperability
- Consistency

---

# Property Principles

## Principle 1 — Every Property Has Meaning

Every property must represent meaningful engineering information.

Properties should never exist solely for storage convenience.

---

## Principle 2 — Properties Do Not Define Identity

Changing a property does not create a new Resource.

For example:

Changing a Wall's height does not change its identity.

Changing a Door's material does not create a new Door.

---

## Principle 3 — Classification Determines Properties

Resource Classification determines which properties are applicable.

Example:

Wall

Applicable Properties:

- Height
- Thickness
- Material
- Fire Rating

Document

Applicable Properties:

- Author
- Revision
- Publication Date

Properties must be appropriate to the Resource Classification.

---

## Principle 4 — Properties Are Extensible

New properties may be introduced without changing the Resource Model.

Atlas supports domain-specific property extensions while maintaining compatibility.

---

## Principle 5 — Properties Are Typed

Every property has a defined data type.

Examples:

- Text
- Integer
- Decimal
- Boolean
- Date
- Time
- Enumeration
- Reference
- Collection
- Geometry

Typed properties enable validation and interoperability.

---

# Property Categories

Properties are organized into logical categories.

---

## Core Properties

Common to every Atlas Resource.

Examples:

- Name
- Description
- Status
- Tags

---

## Engineering Properties

Describe engineering characteristics.

Examples:

- Length
- Width
- Height
- Thickness
- Volume
- Weight
- Capacity
- Fire Rating
- Thermal Resistance

---

## Material Properties

Describe material composition.

Examples:

- Material
- Density
- Finish
- Color
- Manufacturer

---

## Performance Properties

Describe operational behavior.

Examples:

- Load Capacity
- Energy Rating
- Acoustic Rating
- Durability
- Efficiency

---

## Administrative Properties

Support project management.

Examples:

- Cost
- Supplier
- Warranty
- Installation Date
- Maintenance Schedule

---

## Domain Properties

Specialized properties introduced by specific engineering disciplines.

Examples:

- Structural
- Mechanical
- Electrical
- Plumbing
- Sustainability
- Manufacturing

---

# Property Characteristics

Every property should define:

- Name
- Identifier
- Description
- Data Type
- Unit (if applicable)
- Default Value (optional)
- Required or Optional
- Editable or Read-only
- Validation Rules

---

# Property Inheritance

Properties may be inherited from parent classifications.

Example:

```
Building Element

↓

Wall

↓

Exterior Wall
```

Exterior Wall inherits the properties defined by:

- Building Element
- Wall

while adding its own specialized properties.

Inheritance reduces duplication and maintains consistency.

---

# Property Values

A property consists of two parts:

```
Property Definition

↓

Property Value
```

Example:

Property Definition

```
Height
```

Property Value

```
3000 mm
```

The definition remains constant.

The value changes between Resources.

---

# Units

Engineering properties should support explicit units.

Examples:

- mm
- cm
- m
- in
- ft
- kg
- N
- kN
- °C
- W/m²K

Atlas should never assume measurement units.

Units must always be explicit.

---

# Property Constraints

Properties may define constraints.

Examples:

- Minimum value
- Maximum value
- Allowed range
- Enumeration values
- Regular expressions
- Dependency rules

Constraint validation is defined in ENG-008.

---

# Examples

## Example 1

Resource

```
Interior Wall
```

Properties

```
Height: 3000 mm

Thickness: 150 mm

Material: AAC Block

Fire Rating: 2 Hours
```

---

## Example 2

Resource

```
Engineering Drawing
```

Properties

```
Author: John Smith

Revision: B

Scale: 1:100

Sheet Size: A1
```

---

# Responsibilities

Resource Properties are responsible for:

- Describing Resources
- Supporting engineering calculations
- Enabling validation
- Supporting AI reasoning
- Supporting interoperability
- Driving user interfaces

Properties are not responsible for:

- Identity
- Classification
- Relationships
- Lifecycle

---

# Future Evolution

Future versions of Atlas may introduce:

- Computed Properties
- Dynamic Properties
- Formula-based Properties
- Unit Conversion
- Property Templates
- Shared Property Libraries
- Organization-specific Property Sets

The fundamental Property Model remains unchanged.

---

# Relationship to Other Specifications

This specification is related to:

- ENG-001 — Atlas Resource
- ENG-002 — Resource Identity
- ENG-003 — Resource Classification
- ENG-005 — Resource Relationships
- ENG-006 — Resource Semantics
- ENG-008 — Resource Validation

---

# Closing Statement

Properties describe a Resource.

Identity distinguishes it.

Classification defines what it is.

Properties define what is known about it.

Together, they transform an Atlas Resource into a meaningful engineering entity.
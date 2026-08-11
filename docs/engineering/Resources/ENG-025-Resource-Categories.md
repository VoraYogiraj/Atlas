# ENG-025 — Resource Categories

**Document ID:** ENG-025  
**Title:** Resource Categories  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-11  
**Last Updated:** 2026-08-11  
**Reviewers:** TBD  
**Depends On:** ENG-001, ENG-003, ENG-006, ENG-024

---

# Purpose

This specification defines the Resource Category Model used throughout Atlas.

Categories provide a reusable organizational mechanism for grouping Atlas
Resources without changing their identity, classification, properties,
relationships, lifecycle, or semantic tags.

Categories allow Atlas to organize Resources according to engineering,
functional, operational, project, or other meaningful groupings.

---

# Scope

This specification defines:

- Resource Categories
- Category identity
- Category membership
- Category reuse
- Multiple category membership
- Category querying
- Category independence
- Category lifecycle within a Resource

This specification does not define:

- Resource Identity
- Resource Classification
- Resource Properties
- Resource Relationships
- Semantic Tags
- Resource Validation
- Resource Serialization

---

# Definition

A **Resource Category** is a reusable organizational concept that groups
Atlas Resources according to a meaningful criterion.

Categories answer the question:

> **"Which organizational group or groups does this Resource belong to?"**

Categories are independent from Resource Classification.

---

# Classification vs Category

Classification and Category serve different purposes.

## Classification

Classification answers:

> **"What is this Resource?"**

Example:

```text
Atlas Resource
    ↓
Physical Resource
    ↓
Building Element
    ↓
Wall

Classification is hierarchical and defines the engineering type of a
Resource.

Category

Category answers:

"Which group does this Resource belong to?"

Example:

Resource:
North Exterior Wall

Classification:
Wall

Categories:
- Exterior
- Structural
- Ground Floor

A Category does not redefine the Resource's classification.

Design Goals

The Category Model is designed to provide:

Reusable organization
Multiple membership
Stable identity
Clear separation from classification
Project organization
Engineering grouping
Filtering and querying
Future interoperability
Extensibility
Category Principles
Principle 1 — Categories Have Stable Identity

Every Category shall have a unique identifier.

Example:

id = "structural"

The identifier is used for category lookup and membership.

Principle 2 — Categories Are Reusable

A Category may be assigned to multiple Resources.

Example:

Structural
    ↓
Wall A
Wall B
Column A
Beam A

The Category represents one reusable concept.

Principle 3 — Resources May Have Multiple Categories

A Resource may belong to zero, one, or many Categories.

Example:

North Wall

Categories:
- Structural
- Exterior
- Ground Floor

Category membership does not imply exclusivity.

Principle 4 — Categories Do Not Replace Classification

Adding or removing a Category shall not modify:

Resource identity
Resource classification
Resource properties
Resource relationships
Resource lifecycle
Principle 5 — Category Membership Is Explicit

Atlas shall not infer category membership merely from:

Resource name
Classification
Property values
Geometry
Relationships

Unless a future semantic or rules engine explicitly performs such
inference.

Principle 6 — Category Definitions Are Reusable

A Category definition may be shared by multiple Resources.

Resources reference the same Category concept rather than creating
duplicate Category definitions.

Category Model

A Category consists of:

Category
│
├── id
├── name
└── description

Example:

id:
    structural

name:
    Structural

description:
    Resources that participate in the structural system.
Category Identity

Category identity is defined by its ID.

Two Categories with the same ID represent the same Category identity within
the applicable Atlas context.

A Resource shall not contain the same Category ID more than once.

Category Immutability

Category definitions shall be immutable.

Once created:

ID cannot change
Name cannot change
Description cannot change

If a different concept is required, a new Category shall be created.

Category Membership

Resources expose Category membership through a dedicated API.

The Resource shall support:

categories
add_category()
get_category()
has_category()
remove_category()
Category Collection

The Resource Category collection shall:

Preserve insertion order
Prevent duplicate Category IDs
Allow multiple different Categories
Allow zero Categories
Return Categories without exposing internal storage

Example:

resource.add_category(structural)
resource.add_category(exterior)

resource.categories

returns:

[
    structural,
    exterior,
]
Category Sharing

The same Category object may be assigned to multiple Resources.

Example:

structural = AtlasCategory(
    id="structural",
    name="Structural",
)

wall.add_category(structural)
column.add_category(structural)
beam.add_category(structural)

All three Resources reference the same Category definition.

Category Removal

Removing a Category from a Resource removes only the membership.

It does not delete the Category definition.

Example:

wall.remove_category("structural")

The Category may remain assigned to other Resources.

Category Queries

Resources shall support:

resource.get_category("structural")
resource.has_category("structural")

Missing Categories shall return:

None

for get_category() and:

False

for has_category().

Validation

The Category API shall reject invalid inputs.

Adding a non-Category object shall raise:

TypeError

Using a non-string Category ID for lookup, membership testing, or removal
shall raise:

TypeError

Adding a Category with an ID that already exists on the Resource shall
raise:

ValueError
Independence

Category membership is independent of:

Classification
Properties
Relationships
Lifecycle
Semantic Tags

Changing a Resource's Category membership shall not automatically modify
these systems.

Examples
Example 1 — Structural Group

Resource:

North Wall

Classification:

Building Element
    ↓
Wall

Categories:

Structural
Exterior
Example 2 — Multiple Resources

Category:

Structural

Resources:

Column A
Beam A
Wall A
Foundation A

All Resources may share the same Category.

Example 3 — Independent Classification

Resource:

Emergency Exit Door

Classification:

Building Element
    ↓
Door

Categories:

Safety
Egress
Ground Floor

The Categories do not change the Resource's classification.

Future Evolution

Future versions of Atlas may introduce:

Hierarchical Categories
Category Registries
Project-scoped Categories
Category inheritance
Category rules
Automatic categorization
Category-based validation
Category-based search
Category permissions
Category analytics

These capabilities are outside the scope of ENG-025 v0.1.

Relationship to Other Specifications

This specification is related to:

ENG-001 — Atlas Resource
ENG-003 — Resource Classification
ENG-006 — Resource Semantics
ENG-024 — Semantic Tags

Classification defines what a Resource is.

Semantic Tags provide explicit semantic labels.

Categories provide reusable organizational groupings.

Together they provide complementary mechanisms for representing
engineering Resources.

Closing Statement

Classification tells Atlas what a Resource is.

Semantic Tags provide explicit semantic labels.

Categories tell Atlas which organizational groups a Resource belongs to.

Categories provide flexible, reusable organization without changing the
fundamental identity or engineering classification of a Resource.
# ENG-032 — Semantic Agent

**Document ID:** ENG-032  
**Title:** Semantic Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-003, ENG-006, ENG-024, ENG-025, ENG-028, ENG-029

---

# Purpose

This specification defines the Semantic Agent used by the Atlas Agent
Runtime.

The Semantic Agent provides agent-facing access to the semantic information
already represented by Atlas Resources.

The Semantic Agent operates on:

- Resource Classification
- Classification hierarchy
- Semantic Tags
- Categories

The Semantic Agent does not replace these domain models.

---

# Scope

This specification defines:

- Semantic Agent identity
- Classification inspection
- Classification hierarchy inspection
- Semantic Tag queries
- Semantic Tag membership
- Semantic Tag attachment
- Semantic Tag removal
- Category queries
- Category membership
- Category attachment
- Category removal
- Semantic context inspection
- Project-scoped execution
- Agent Result traceability

This specification does not define:

- LLM reasoning
- ML inference
- Automatic semantic classification
- Automatic Tag inference
- Automatic Category inference
- Ontology reasoning
- Regulatory reasoning
- Constraint evaluation
- Validation
- Relationship reasoning
- Natural-language understanding
- Semantic knowledge generation

---

# Definition

The **Semantic Agent** is a specialized Atlas Agent responsible for
interacting with the explicit semantic model of an Atlas Resource.

It exposes existing semantic information through the Agent Runtime.

The Semantic Agent does not invent engineering meaning.

---

# Semantic Model

Atlas currently represents Resource meaning through:

```text
Classification
      +
Semantic Tags
      +
Categories
      +
Properties
      +
Relationships

ENG-032 v0.1 focuses on the explicit semantic structures already defined
by Atlas:

Classification
Semantic Tags
Categories
Semantic Responsibilities

The Semantic Agent may:

Inspect a Resource's Classification
Inspect Classification hierarchy
Read Semantic Tags
Add Semantic Tags
Remove Semantic Tags
Test Semantic Tag membership
Read Categories
Add Categories
Remove Categories
Test Category membership
Return a consolidated semantic context
Non-Inference Principle

ENG-032 v0.1 shall not infer semantic meaning.

For example:

Wall

shall not automatically cause:

"Structural"
"Exterior"
"Load Bearing"

to be added merely because the Resource is classified as Wall.

Semantic membership must remain explicit.

Automatic semantic inference is a future AI capability.

Identity

The Semantic Agent shall use:

id:
semantic-agent

name:
Semantic Agent
Project Context

Semantic operations require an AtlasProject through Agent Context.

Example:

AtlasAgentContext(
    project=project,
)

The Semantic Agent shall operate only within the supplied Project boundary.

Resource Reference

Semantic operations shall receive a Resource through Agent Request metadata.

Metadata:

resource

The value shall be an AtlasResource.

For read operations, the Resource must belong to the supplied Project.

For mutation operations, the Resource must also belong to the supplied
Project.

Supported Actions

ENG-032 v0.1 supports:

get_classification
get_classification_path
list_semantic_tags
get_semantic_tag
has_semantic_tag
add_semantic_tag
remove_semantic_tag
list_categories
get_category
has_category
add_category
remove_category
get_semantic_context
Classification
get_classification

Returns the Resource's current AtlasClassification.

A Resource always exposes its classification.

Result:

COMPLETED
output = AtlasClassification
Classification Path
get_classification_path

Returns the complete classification hierarchy represented by the Resource's
Classification.

Example:

Atlas Resource
Physical Resource
Building Element
Wall
Exterior Wall

The output shall be the existing Classification path representation.

The Semantic Agent shall not construct a second hierarchy model.

Semantic Tags
list_semantic_tags

Returns the Resource's Semantic Tags.

The output shall preserve Resource Tag collection order.

The returned collection shall not expose mutable internal storage.

get_semantic_tag

Metadata:

tag_id

Returns:

AtlasSemanticTag

when attached.

Returns:

None

when not attached.

has_semantic_tag

Metadata:

tag_id

Returns:

True

or:

False
add_semantic_tag

Metadata:

tag

The value shall be an AtlasSemanticTag.

The operation delegates to the Resource's existing semantic-tag API.

Duplicate Tag IDs shall remain governed by the Resource semantic-tag
implementation.

The Resource's Classification shall not change.

The Resource's Categories shall not change.

remove_semantic_tag

Metadata:

tag_id

The operation delegates to the Resource's existing semantic-tag API.

Removing a missing Tag returns:

None

Removing a Tag does not change:

Classification
Categories
Properties
Relationships
Lifecycle
Categories
list_categories

Returns the Resource's Categories.

The output shall preserve Resource Category collection order.

The returned collection shall be independent from internal storage.

get_category

Metadata:

category_id

Returns the attached AtlasCategory, or:

None

when the Category is absent.

has_category

Metadata:

category_id

Returns:

True

or:

False
add_category

Metadata:

category

The value shall be an AtlasCategory.

The operation delegates to the Resource Category API.

Category membership shall not modify:

Classification
Semantic Tags
Properties
Relationships
Lifecycle
remove_category

Metadata:

category_id

The operation delegates to the Resource Category API.

Removing a missing Category returns:

None
Semantic Context
get_semantic_context

The Semantic Agent shall provide a deterministic summary of the explicit
semantic information of a Resource.

The output shall contain:

classification
classification_path
semantic_tags
categories

Example:

{
    "classification": Wall,
    "classification_path": (
        "Physical Resource",
        "Building Element",
        "Wall",
    ),
    "semantic_tags": [
        Structural,
        Exterior,
    ],
    "categories": [
        Building Envelope,
    ],
}

The Semantic Context describes existing information.

It does not infer additional meaning.

Project Boundary

A Resource belonging to another Project shall not be operated on through the
current Semantic Agent context.

Cross-project semantic access is outside ENG-032 v0.1.

Ownership

Semantic Tags and Categories remain owned by the Resource.

The Semantic Agent does not own:

Classification
Semantic Tags
Categories

The Agent invokes the existing Resource APIs.

Classification Immutability

The Semantic Agent shall never modify the Resource's Classification.

Classification remains an immutable part of the Resource identity model.

Tag and Category Independence

Adding or removing a Semantic Tag shall not automatically add or remove a
Category.

Adding or removing a Category shall not automatically add or remove a
Semantic Tag.

Classification shall remain independent from both.

Mutation Boundary

ENG-032 allows explicit Tag and Category membership changes because those
operations already exist in the Resource semantic model.

The Agent must use:

resource.add_tag()
resource.remove_tag()
resource.add_category()
resource.remove_category()

or their equivalent existing public APIs.

The Agent shall not modify Resource internal dictionaries directly.

Errors

The Semantic Agent shall return:

FAILED

for:

Missing Project context
Missing Resource
Resource from another Project
Missing required metadata
Invalid Tag type
Invalid Category type
Invalid Tag ID
Invalid Category ID
Unsupported action

The underlying Resource API remains responsible for enforcing its own
semantic integrity rules.

Traceability

Every Semantic Agent Result shall preserve:

agent_id
request_id
status
output
error

The Request ID shall remain unchanged.

Non-AI Implementation

ENG-032 v0.1 is deterministic.

No machine-learning model or LLM is required.

The Semantic Agent exposes existing explicit semantic information.

Future AI Evolution

Future versions may allow a Semantic Agent to:

Infer semantic Tags
Suggest Categories
Identify likely classifications
Compare semantic contexts
Detect semantic conflicts
Discover semantic relationships
Use engineering ontologies
Use language models
Explain inferred meaning
Assign semantic confidence scores

Any inferred result must eventually distinguish:

Explicit

from:

Inferred
Architecture
Orchestrator
      |
      v
Semantic Agent
      |
      v
Atlas Resource
      |
      +------------------+
      |                  |
      v                  v
Classification      Semantic Tags
      |
      +
   Categories
Example

Resource:

North Wall

Classification:

Building Element
    >
Wall

Semantic Tags:

Structural
Exterior

Categories:

Building Envelope

Semantic Agent:

get_semantic_context()

returns the explicit semantic information above.

It does not decide whether the Wall is structurally significant.

Relationship to Phase 6

The Semantic Agent consumes the explicit semantic structures created by
Phase 6:

Classification       ✅
Semantic Tags        ✅
Categories           ✅
Validation           ✅
Constraints          ✅

It does not duplicate those systems.

Relationship to Phase 7

ENG-032 implements:

Orchestrator Agent
        |
        v
Semantic Agent
        |
        v
Atlas Semantic Model

The Semantic Agent becomes the Phase 7 bridge between the deterministic
semantic model and future intelligent reasoning.

Future Evolution

Future versions may introduce:

Semantic inference
Ontology integration
Knowledge graphs
Semantic search
Multi-language concepts
Semantic confidence
Context-aware interpretation
AI-generated semantic explanations
Semantic reasoning chains

These capabilities are outside ENG-032 v0.1.

Closing Statement

The Semantic Agent exposes the explicit engineering meaning already
represented by Atlas.

Classification defines what a Resource is.

Semantic Tags provide explicit semantic labels.

Categories provide reusable organizational concepts.

The Semantic Agent connects these existing structures to the Agent Runtime.

It does not invent meaning in v0.1.

Future intelligent reasoning may build upon this deterministic semantic
foundation.
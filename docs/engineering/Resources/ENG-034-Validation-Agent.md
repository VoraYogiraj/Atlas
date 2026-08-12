# ENG-034 — Validation Agent

**Document ID:** ENG-034  
**Title:** Validation Agent  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  
**Created:** 2026-08-12  
**Last Updated:** 2026-08-12  
**Reviewers:** TBD  
**Depends On:** ENG-008, ENG-026, ENG-027, ENG-028, ENG-029

---

# Purpose

This specification defines the Validation Agent used by the Atlas Agent
Runtime.

The Validation Agent provides agent-facing access to the Atlas Validation
Runtime.

It allows Agents to execute explicit validation rules against Atlas
Resources and inspect the resulting validation findings.

The Validation Agent does not replace AtlasValidationEngine,
AtlasValidationRule, or AtlasValidationResult.

---

# Scope

This specification defines:

- Validation Agent identity
- Resource validation
- Validation rule inspection
- Rule lookup
- Rule registration
- Rule removal
- Validation result inspection
- Severity inspection
- Validation category inspection
- Project-scoped validation access
- Validation traceability

This specification does not define:

- New validation logic
- Automatic rule generation
- AI validation inference
- Regulatory interpretation
- Constraint authoring
- Resource mutation
- Automatic correction
- Approval workflows
- Human review workflows

---

# Definition

The **Validation Agent** is a specialized Atlas Agent responsible for
executing and inspecting explicit Atlas validation rules.

The Agent delegates validation execution to the existing
`AtlasValidationEngine`.

It does not implement a second validation engine.

---

# Architecture

```text
Orchestrator
      |
      v
Validation Agent
      |
      v
AtlasValidationEngine
      |
      v
AtlasValidationRule
      |
      v
AtlasValidationResult
Relationship to ENG-026

ENG-026 defines the Validation Runtime Model.

It provides:

AtlasValidationEngine
AtlasValidationRule
AtlasValidationResult
AtlasValidationCategory
AtlasValidationSeverity

ENG-034 exposes those capabilities through the Agent Runtime.

Relationship to ENG-027

ENG-027 defines the Property Constraint Runtime.

Constraint evaluation may eventually be represented through validation
rules.

The Validation Agent does not duplicate the Constraint Engine.

Relationship to ENG-029

The Orchestrator may route validation requests to the Validation Agent.

Orchestrator
      |
      v
Validation Agent
      |
      v
Validation Engine
Identity

The Validation Agent shall use:

id:
validation-agent

name:
Validation Agent
Validation Engine Context

The Validation Agent requires an AtlasValidationEngine.

The engine shall be supplied through the Agent Context.

Example:

AtlasAgentContext(
    validation_engine=engine,
)

The Validation Agent shall not silently create a separate engine for each
request.

Resource Context

Validation operations require an AtlasResource.

Example:

AtlasAgentContext(
    validation_engine=engine,
    metadata={
        "resource": resource,
    },
)

The Resource itself is observed.

Validation shall never modify the Resource.

Supported Actions

ENG-034 v0.1 supports:

validate_resource
list_rules
get_rule
register_rule
unregister_rule
validate_resource

The validate_resource action shall delegate to:

engine.validate(resource)

The output shall be:

list[AtlasValidationResult]

The order of validation results shall preserve the existing
AtlasValidationEngine rule execution order.

Validation Result Semantics

A validation result may contain:

id
resource_id
category
severity
rule
message
explanation
suggested_resolution
timestamp

The Validation Agent shall return these existing result objects without
rewriting their content.

Empty Validation

If no registered rules produce findings:

COMPLETED
output = []

Validation with zero findings is a successful validation execution.

Validation Failure

If the Validation Engine itself raises an exception while executing a
validation request, the Agent shall return:

FAILED

with an explanatory error.

The Agent shall not fabricate validation results.

list_rules

The list_rules action shall return the registered validation rules.

The order shall preserve Validation Engine registration order.

The Agent shall return a new list rather than exposing internal engine
storage.

get_rule

Metadata:

rule_id

The operation shall delegate to:

engine.get_rule(rule_id)

A found rule returns:

COMPLETED
output = AtlasValidationRule

A missing rule returns:

COMPLETED
output = None

A missing rule is not itself an execution failure.

register_rule

Metadata:

rule

The value shall be an AtlasValidationRule.

The Agent shall delegate registration to:

engine.register_rule(rule)

A successful registration returns:

COMPLETED
output = registered_rule

Duplicate Rule IDs shall remain governed by the Validation Engine.

unregister_rule

Metadata:

rule_id

The Agent shall delegate to:

engine.unregister_rule(rule_id)

A removed Rule returns:

COMPLETED
output = removed_rule

A missing Rule returns:

COMPLETED
output = None
Rule Integrity

The Validation Agent shall not mutate an AtlasValidationRule.

Validation rules are immutable.

Validation Result Integrity

The Validation Agent shall not mutate an AtlasValidationResult.

Validation Results are immutable.

Non-Mutation Principle

Validation must remain observational.

Executing:

validate_resource

must not modify:

Resource identity
Classification
Properties
Relationships
Semantic Tags
Categories
Lifecycle
Metadata
Validation Categories

The Agent shall preserve the existing:

IDENTITY
CLASSIFICATION
PROPERTY
RELATIONSHIP
SEMANTIC
LIFECYCLE
CUSTOM

validation categories.

The Agent shall not invent additional categories within ENG-034.

Validation Severity

The Agent shall preserve the existing:

INFORMATION
WARNING
ERROR
CRITICAL

severity levels.

The Agent shall not reinterpret severity.

Missing Validation Engine

If no AtlasValidationEngine exists in Agent Context, the Agent shall
return:

FAILED

with an explanatory error.

Missing Resource

If a validation request does not contain an AtlasResource, the Agent shall
return:

FAILED

with an explanatory error.

Invalid Rule Metadata

register_rule shall reject metadata that is not an
AtlasValidationRule.

The underlying Validation Engine remains responsible for duplicate Rule ID
validation.

Invalid Rule ID

Rule lookup and removal require a valid Rule ID.

Missing required Rule IDs shall return:

FAILED

with an explanatory error.

Unsupported Actions

Unknown actions shall return:

FAILED

with an explanatory error.

The Agent shall not guess another validation action.

Project Boundary

ENG-034 v0.1 does not require AtlasProject for validation itself.

Validation is performed by an explicit AtlasValidationEngine against an
explicit AtlasResource.

Project ownership may be introduced in a future validation profile.

Non-AI Implementation

ENG-034 v0.1 is deterministic.

It does not require:

LLM
Machine Learning model
AI provider
Semantic inference engine

Validation behavior is determined by explicitly registered rules.

AI Evolution

Future versions may allow the Validation Agent to:

Suggest validation rules
Generate candidate rules
Explain findings
Identify probable missing information
Recommend corrective actions
Reference engineering standards
Predict potential validation failures
Prioritize findings
Perform evidence-backed engineering reasoning

AI-generated recommendations must remain distinguishable from explicit
validation results.

Example

Resource:

Wall

Registered rule:

Wall Height Required

Validation:

validate_resource

Result:

ERROR

Height has not been specified.

The Validation Agent returns the explicit
AtlasValidationResult.

It does not correct the Resource.

Example — Multiple Rules

A Resource may be evaluated against:

Rule 1 → Classification
Rule 2 → Required Properties
Rule 3 → Relationships
Rule 4 → Semantic consistency
Rule 5 → Custom organization rule

The Validation Agent returns the findings in Validation Engine execution
order.

Example — Severity

Results may contain:

Information
Warning
Error
Critical

The Agent preserves the original severity.

It does not automatically escalate or downgrade results.

Relationship to Phase 6

ENG-034 consumes the deterministic validation infrastructure established
during Phase 6:

Validation
Constraints
Semantic Model
Resource Model

It does not duplicate those systems.

Relationship to Phase 7

ENG-034 completes the initial specialized Agent set:

Orchestrator Agent
        |
        +-- Resource Agent
        +-- Registry Agent
        +-- Semantic Agent
        +-- Relationship Agent
        +-- Validation Agent
Future Multi-Agent Reasoning

Once ENG-034 is available, the Orchestrator can eventually coordinate
validation with other Agents.

Example:

User
 |
 v
Orchestrator
 |
 +--> Resource Agent
 |       |
 |       +--> retrieve Resource
 |
 +--> Semantic Agent
 |       |
 |       +--> retrieve semantic context
 |
 +--> Relationship Agent
 |       |
 |       +--> retrieve dependencies
 |
 +--> Validation Agent
         |
         +--> execute validation rules
 |
 v
Combined Agent Results

This creates the foundation for future evidence-based multi-agent
engineering reasoning.

Future Evolution

Future versions may introduce:

Validation profiles
Project-specific validation engines
Organization-specific rule packs
Regulatory validation
Constraint-aware validation
Multi-resource validation
Cross-resource validation
Continuous validation
AI-assisted validation
Validation prioritization
Validation history

These capabilities are outside ENG-034 v0.1.

Closing Statement

The Validation Agent connects the Atlas Agent Runtime to the deterministic
Validation Engine.

The Validation Engine executes rules.

Validation Rules define checks.

Validation Results represent findings.

The Validation Agent coordinates these capabilities without duplicating
validation logic.

Future AI agents may reason about validation findings, but the underlying
engineering validation remains explicit, deterministic, traceable, and
explainable.
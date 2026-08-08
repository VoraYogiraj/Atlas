# Atlas Engineering Guidelines

**Version:** 1.0.0  
**Status:** Active  
**Applies To:** All contributors, human and AI

---

# Purpose

This document defines the engineering standards used throughout Project Atlas.

Every contributor, whether human or AI, must follow these guidelines to ensure consistency, maintainability, scalability, and engineering excellence.

These guidelines are technology-independent whenever possible and should evolve carefully over time.

---

# Engineering Philosophy

Atlas is an engineering platform, not a collection of features.

Every line of code should contribute to:

- Clarity
- Simplicity
- Correctness
- Extensibility
- Explainability
- Testability

The architecture always takes priority over implementation speed.

---

# Engineering Principles

Every implementation should follow the Atlas Principles.

In particular:

- Engineering First
- Semantic by Design
- Explainable Intelligence
- Interoperability by Default
- Build Intelligence, Not Commodity
- Simplicity Before Complexity
- Extensibility Without Breaking Existing Systems

If an implementation conflicts with these principles, the implementation should be reconsidered.

---

# Architecture Principles

Atlas follows Clean Architecture and Domain-Driven Design.

Dependencies should always point inward.

```
Infrastructure

↓

Application

↓

Domain
```

The Domain layer must never depend on:

- Frameworks
- Databases
- User Interfaces
- AI Providers
- Web APIs

Infrastructure depends on the Domain.

Never the reverse.

---

# Domain First

Every feature begins in the Domain.

Do not start implementation with:

- React
- FastAPI
- PostgreSQL
- Three.js
- OpenAI SDK

Instead begin with:

- Atlas Resources
- Engineering concepts
- Domain models

Infrastructure is attached after the domain is stable.

---

# Naming Conventions

Names should describe engineering concepts.

Prefer:

- AtlasResource
- AtlasProject
- AtlasResourceRegistry
- AtlasSerializer
- AtlasID

Avoid generic names such as:

- Manager
- Helper
- Utils
- Misc
- Thing
- Data

Names should communicate intent without additional explanation.

---

# Single Responsibility

Every class should have one responsibility.

Every module should represent one engineering concept.

Every function should perform one logical operation.

Avoid classes that accumulate unrelated responsibilities.

---

# Simplicity

Prefer simple implementations over clever implementations.

Readable code is preferred over shorter code.

Avoid unnecessary abstraction.

Only introduce complexity when it solves a demonstrated engineering problem.

---

# Documentation

Every public class, method, and module should include documentation.

Documentation should explain:

- Purpose
- Responsibilities
- Inputs
- Outputs
- Constraints

Documentation should explain *why*, not repeat *what* the code already says.

---

# Type Safety

All public interfaces should include explicit type annotations.

Avoid ambiguous types whenever practical.

Engineering models should be strongly typed.

---

# Testing

Every feature must include automated tests.

Testing should verify:

- Expected behavior
- Edge cases
- Invalid input
- Regression prevention

Untested code is considered incomplete.

---

# Error Handling

Errors should be:

- Explicit
- Actionable
- Explainable

Never silently ignore failures.

Avoid generic exceptions where domain-specific exceptions improve clarity.

---

# Dependencies

Every dependency must have a clear justification.

Before adding a dependency, ask:

- Does the standard library already solve this?
- Does this dependency improve Atlas?
- Is the dependency actively maintained?
- Can Atlas function without it?

Atlas should minimize unnecessary dependencies.

---

# Performance

Correctness is more important than optimization.

Optimize only after measuring.

Avoid premature optimization.

Engineering clarity takes priority.

---

# Security

Assume every external input is untrusted.

Validate all inputs.

Avoid exposing internal implementation details.

Protect engineering integrity before convenience.

---

# AI Development Guidelines

AI-generated code is a starting point, not a final product.

Every AI contribution must be:

- Reviewed
- Understood
- Tested
- Refactored when necessary

Do not accept generated code without engineering review.

AI assists engineering.

AI does not replace engineering judgment.

---

# Code Review Checklist

Before merging any change, verify:

- Architecture remains consistent.
- Atlas Principles are respected.
- Engineering Specifications are followed.
- Tests pass.
- Documentation is updated where required.
- No unnecessary complexity has been introduced.
- Public APIs remain coherent.
- Breaking changes are intentional and documented.

---

# Git Workflow

Every commit should represent one logical change.

Commit messages should be concise and descriptive.

Example:

```
feat(engine): implement AtlasID

feat(engine): add AtlasResource

test(engine): add AtlasResource unit tests

docs(eng): update Resource Relationships specification
```

Avoid mixing unrelated changes into a single commit.

---

# Engineering Specifications

Implementation must follow the Engineering Specifications.

If implementation reveals an issue in a specification:

1. Document the issue.
2. Discuss the architectural impact.
3. Update the specification.
4. Implement the agreed solution.

Specifications guide implementation.

Implementation may improve specifications.

---

# Decision Making

When faced with multiple solutions, prefer the one that:

1. Preserves architecture.
2. Maximizes clarity.
3. Reduces coupling.
4. Improves extensibility.
5. Simplifies future maintenance.

Short-term convenience must never compromise long-term architecture.

---

# Definition of Done

A task is complete only when:

- Implementation is complete.
- Tests pass.
- Documentation is updated.
- Code review is complete.
- Engineering Guidelines have been followed.
- Atlas Principles remain satisfied.

Working code alone is not considered complete.

---

# Closing Statement

Atlas is intended to become a long-lived engineering platform.

Every decision made today influences the maintainability, extensibility, and intelligence of the platform tomorrow.

Engineering excellence is achieved through consistent principles, disciplined implementation, and continuous improvement.

Build with intention.

Build with clarity.

Build for decades.
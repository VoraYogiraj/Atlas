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
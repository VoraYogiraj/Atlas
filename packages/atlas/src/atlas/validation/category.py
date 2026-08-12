"""
Atlas Validation Category

Defines validation categories used by the Atlas Validation Model.

Specification:
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model
"""

from __future__ import annotations

from enum import Enum


class AtlasValidationCategory(str, Enum):
    """
    Category of a validation rule or validation result.
    """

    IDENTITY = "identity"
    CLASSIFICATION = "classification"
    PROPERTY = "property"
    RELATIONSHIP = "relationship"
    SEMANTIC = "semantic"
    LIFECYCLE = "lifecycle"
    CUSTOM = "custom"

"""
Atlas Constraint Operators

ENG-027 — Property Constraints & Unit-Aware Evaluation
"""

from __future__ import annotations

from enum import Enum


class AtlasConstraintOperator(str, Enum):
    """
    Operators supported by ENG-027 constraints.
    """

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    MATCHES = "matches"
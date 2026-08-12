"""
Atlas Constraint Evaluation Result

ENG-027 — Property Constraints & Unit-Aware Evaluation
"""

from __future__ import annotations

from enum import Enum


class AtlasConstraintResult(str, Enum):
    """
    Logical result of evaluating a Constraint.
    """

    SATISFIED = "satisfied"
    VIOLATED = "violated"
    NOT_EVALUABLE = "not_evaluable"
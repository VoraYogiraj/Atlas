"""
Atlas Constraint Evaluator

ENG-027 — Property Constraints & Unit-Aware Evaluation
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from numbers import Real
from typing import Any

from atlas.constraints.constraint import AtlasConstraint
from atlas.constraints.operator import AtlasConstraintOperator
from atlas.constraints.result import AtlasConstraintResult
from atlas.properties.property import AtlasProperty


class AtlasConstraintEvaluator:
    """
    Evaluates AtlasProperty values against AtlasConstraint definitions.

    ENG-027 v0.1 supports:

        Length:
            mm
            cm
            m
            in
            ft

        Operators:
            EQUAL
            NOT_EQUAL
            GREATER_THAN
            GREATER_THAN_OR_EQUAL
            LESS_THAN
            LESS_THAN_OR_EQUAL
            IN
            NOT_IN
            MATCHES
    """

    _LENGTH_FACTORS: dict[str, Decimal] = {
        "mm": Decimal("1"),
        "cm": Decimal("10"),
        "m": Decimal("1000"),
        "in": Decimal("25.4"),
        "ft": Decimal("304.8"),
    }

    def evaluate(
        self,
        property: AtlasProperty,
        constraint: AtlasConstraint,
    ) -> AtlasConstraintResult:
        """
        Evaluate a Property against a Constraint.
        """
        if property.id != constraint.property_id:
            return AtlasConstraintResult.NOT_EVALUABLE

        value = property.value

        if value is None:
            return AtlasConstraintResult.NOT_EVALUABLE

        operator = constraint.operator

        if operator in {
            AtlasConstraintOperator.IN,
            AtlasConstraintOperator.NOT_IN,
        }:
            return self._evaluate_membership(
                property,
                constraint,
            )

        if operator == AtlasConstraintOperator.MATCHES:
            return self._evaluate_matches(
                property,
                constraint,
            )

        return self._evaluate_comparison(
            property,
            constraint,
        )

    # ------------------------------------------------------------------
    # Numeric / Measurement Evaluation
    # ------------------------------------------------------------------

    def _evaluate_comparison(
        self,
        property: AtlasProperty,
        constraint: AtlasConstraint,
    ) -> AtlasConstraintResult:
        if not self._is_numeric_value(
            property.value
        ):
            return AtlasConstraintResult.NOT_EVALUABLE

        if not self._is_numeric_value(
            constraint.expected_value
        ):
            return AtlasConstraintResult.NOT_EVALUABLE

        normalized = self._normalize_numeric_pair(
            property.value,
            property.unit,
            constraint.expected_value,
            constraint.expected_unit,
        )

        if normalized is None:
            return AtlasConstraintResult.NOT_EVALUABLE

        actual, expected = normalized

        operator = constraint.operator

        if operator == AtlasConstraintOperator.EQUAL:
            return self._result(
                actual == expected
            )

        if operator == AtlasConstraintOperator.NOT_EQUAL:
            return self._result(
                actual != expected
            )

        if operator == AtlasConstraintOperator.GREATER_THAN:
            return self._result(
                actual > expected
            )

        if operator == AtlasConstraintOperator.GREATER_THAN_OR_EQUAL:
            return self._result(
                actual >= expected
            )

        if operator == AtlasConstraintOperator.LESS_THAN:
            return self._result(
                actual < expected
            )

        if operator == AtlasConstraintOperator.LESS_THAN_OR_EQUAL:
            return self._result(
                actual <= expected
            )

        return AtlasConstraintResult.NOT_EVALUABLE

    # ------------------------------------------------------------------
    # Membership Evaluation
    # ------------------------------------------------------------------

    def _evaluate_membership(
        self,
        property: AtlasProperty,
        constraint: AtlasConstraint,
    ) -> AtlasConstraintResult:
        expected_values = constraint.expected_value

        if not isinstance(
            expected_values,
            (list, tuple, set, frozenset),
        ):
            return AtlasConstraintResult.NOT_EVALUABLE

        if property.value is None:
            return AtlasConstraintResult.NOT_EVALUABLE

        # Numeric membership with explicit compatible units.
        if (
            self._is_numeric_value(property.value)
            and all(
                self._is_numeric_value(item)
                for item in expected_values
            )
        ):
            if (
                constraint.expected_unit is not None
                or property.unit is not None
            ):
                if property.unit is None:
                    return AtlasConstraintResult.NOT_EVALUABLE

                if constraint.expected_unit is None:
                    return AtlasConstraintResult.NOT_EVALUABLE

                normalized_actual = self._convert_value(
                    property.value,
                    property.unit,
                    constraint.expected_unit,
                )

                if normalized_actual is None:
                    return AtlasConstraintResult.NOT_EVALUABLE

                expected_decimal_values = [
                    Decimal(str(item))
                    for item in expected_values
                ]

                is_member = (
                    normalized_actual in expected_decimal_values
                )
            else:
                is_member = property.value in expected_values

        else:
            is_member = property.value in expected_values

        if constraint.operator == AtlasConstraintOperator.IN:
            return self._result(is_member)

        if constraint.operator == AtlasConstraintOperator.NOT_IN:
            return self._result(not is_member)

        return AtlasConstraintResult.NOT_EVALUABLE

    # ------------------------------------------------------------------
    # Regex Evaluation
    # ------------------------------------------------------------------

    def _evaluate_matches(
        self,
        property: AtlasProperty,
        constraint: AtlasConstraint,
    ) -> AtlasConstraintResult:
        if not isinstance(
            property.value,
            str,
        ):
            return AtlasConstraintResult.NOT_EVALUABLE

        if not isinstance(
            constraint.expected_value,
            str,
        ):
            return AtlasConstraintResult.NOT_EVALUABLE

        try:
            matched = re.search(
                constraint.expected_value,
                property.value,
            )
        except re.error:
            return AtlasConstraintResult.NOT_EVALUABLE

        return self._result(
            matched is not None
        )

    # ------------------------------------------------------------------
    # Unit Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_numeric_pair(
        cls,
        actual_value: Real,
        actual_unit: str | None,
        expected_value: Real,
        expected_unit: str | None,
    ) -> tuple[Decimal, Decimal] | None:
        if actual_unit is None and expected_unit is None:
            return (
                Decimal(str(actual_value)),
                Decimal(str(expected_value)),
            )

        if actual_unit is None or expected_unit is None:
            return None

        converted = cls._convert_value(
            actual_value,
            actual_unit,
            expected_unit,
        )

        if converted is None:
            return None

        try:
            expected = Decimal(
                str(expected_value)
            )
        except (InvalidOperation, ValueError):
            return None

        return (
            converted,
            expected,
        )

    @classmethod
    def _convert_value(
        cls,
        value: Real,
        from_unit: str,
        to_unit: str,
    ) -> Decimal | None:
        source = cls._LENGTH_FACTORS.get(
            from_unit
        )

        target = cls._LENGTH_FACTORS.get(
            to_unit
        )

        if source is None or target is None:
            return None

        try:
            value_decimal = Decimal(
                str(value)
            )
        except (InvalidOperation, ValueError):
            return None

        # Convert to millimetres, then into the target unit.
        millimetres = value_decimal * source

        return millimetres / target

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_numeric_value(
        value: Any,
    ) -> bool:
        if isinstance(value, bool):
            return False

        return isinstance(
            value,
            Real,
        )

    @staticmethod
    def _result(
        condition: bool,
    ) -> AtlasConstraintResult:
        if condition:
            return AtlasConstraintResult.SATISFIED

        return AtlasConstraintResult.VIOLATED
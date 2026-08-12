"""
ENG-027 — Property Constraints & Unit-Aware Evaluation

Tests the runtime constraint model defined by ENG-027.

The constraint system consists of:

    AtlasConstraint
    AtlasConstraintOperator
    AtlasConstraintResult
    AtlasConstraintEvaluator
"""

from atlas.properties.property import AtlasProperty
from atlas.constraints.constraint import AtlasConstraint
from atlas.constraints.evaluator import AtlasConstraintEvaluator
from atlas.constraints.operator import AtlasConstraintOperator
from atlas.constraints.result import AtlasConstraintResult


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_numeric_property(
    *,
    value=3000,
    unit="mm",
    data_type="integer",
) -> AtlasProperty:
    return AtlasProperty(
        id="height",
        name="Height",
        value=value,
        data_type=data_type,
        unit=unit,
    )


def create_string_property(
    *,
    value="AAC Block",
) -> AtlasProperty:
    return AtlasProperty(
        id="material",
        name="Material",
        value=value,
        data_type="string",
        unit=None,
    )


def create_constraint(
    *,
    id="minimum-height",
    property_id="height",
    operator=AtlasConstraintOperator.GREATER_THAN_OR_EQUAL,
    expected_value=2400,
    expected_unit="mm",
    context=None,
    source=None,
) -> AtlasConstraint:
    return AtlasConstraint(
        id=id,
        property_id=property_id,
        operator=operator,
        expected_value=expected_value,
        expected_unit=expected_unit,
        context=context,
        source=source,
    )


# ----------------------------------------------------------------------
# Constraint Operators
# ----------------------------------------------------------------------


def test_constraint_operator_equal():
    assert AtlasConstraintOperator.EQUAL.value == "equal"


def test_constraint_operator_not_equal():
    assert (
        AtlasConstraintOperator.NOT_EQUAL.value
        == "not_equal"
    )


def test_constraint_operator_greater_than():
    assert (
        AtlasConstraintOperator.GREATER_THAN.value
        == "greater_than"
    )


def test_constraint_operator_greater_than_or_equal():
    assert (
        AtlasConstraintOperator.GREATER_THAN_OR_EQUAL.value
        == "greater_than_or_equal"
    )


def test_constraint_operator_less_than():
    assert (
        AtlasConstraintOperator.LESS_THAN.value
        == "less_than"
    )


def test_constraint_operator_less_than_or_equal():
    assert (
        AtlasConstraintOperator.LESS_THAN_OR_EQUAL.value
        == "less_than_or_equal"
    )


def test_constraint_operator_in():
    assert AtlasConstraintOperator.IN.value == "in"


def test_constraint_operator_not_in():
    assert AtlasConstraintOperator.NOT_IN.value == "not_in"


def test_constraint_operator_matches():
    assert AtlasConstraintOperator.MATCHES.value == "matches"


# ----------------------------------------------------------------------
# Constraint Identity
# ----------------------------------------------------------------------


def test_constraint_has_id():
    constraint = create_constraint()

    assert constraint.id == "minimum-height"


def test_constraint_has_property_id():
    constraint = create_constraint()

    assert constraint.property_id == "height"


def test_constraint_has_operator():
    constraint = create_constraint()

    assert (
        constraint.operator
        == AtlasConstraintOperator.GREATER_THAN_OR_EQUAL
    )


def test_constraint_has_expected_value():
    constraint = create_constraint()

    assert constraint.expected_value == 2400


def test_constraint_has_expected_unit():
    constraint = create_constraint()

    assert constraint.expected_unit == "mm"


def test_constraint_has_context():
    constraint = create_constraint(
        context={
            "project_type": "residential",
            "discipline": "architecture",
        }
    )

    assert constraint.context == {
        "project_type": "residential",
        "discipline": "architecture",
    }


def test_constraint_has_source():
    constraint = create_constraint(
        source="Project Standard"
    )

    assert constraint.source == "Project Standard"


def test_constraint_is_immutable():
    constraint = create_constraint()

    try:
        constraint.id = "different"
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError(
            "Constraint must be immutable"
        )


# ----------------------------------------------------------------------
# Constraint Result
# ----------------------------------------------------------------------


def test_constraint_result_satisfied():
    result = AtlasConstraintResult.SATISFIED

    assert result.value == "satisfied"


def test_constraint_result_violated():
    result = AtlasConstraintResult.VIOLATED

    assert result.value == "violated"


def test_constraint_result_not_evaluable():
    result = AtlasConstraintResult.NOT_EVALUABLE

    assert result.value == "not_evaluable"


def test_constraint_result_is_complete_enum():
    assert set(AtlasConstraintResult) == {
        AtlasConstraintResult.SATISFIED,
        AtlasConstraintResult.VIOLATED,
        AtlasConstraintResult.NOT_EVALUABLE,
    }


# ----------------------------------------------------------------------
# Numeric Constraint Evaluation
# ----------------------------------------------------------------------


def test_numeric_equal_is_satisfied():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.EQUAL,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_numeric_equal_is_violated():
    property = create_numeric_property(
        value=2500,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.EQUAL,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.VIOLATED
    )


def test_greater_than_is_satisfied():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.GREATER_THAN,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_greater_than_is_violated():
    property = create_numeric_property(
        value=2200,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.GREATER_THAN,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.VIOLATED
    )


def test_greater_than_or_equal_accepts_equal_value():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.GREATER_THAN_OR_EQUAL,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_less_than_is_satisfied():
    property = create_numeric_property(
        value=2200,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.LESS_THAN,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_less_than_is_violated():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.LESS_THAN,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.VIOLATED
    )


def test_less_than_or_equal_accepts_equal_value():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.LESS_THAN_OR_EQUAL,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_not_equal_is_satisfied_for_different_value():
    property = create_numeric_property(
        value=2500,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.NOT_EQUAL,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


# ----------------------------------------------------------------------
# Unit Conversion
# ----------------------------------------------------------------------


def test_mm_to_cm_comparison():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        expected_value=240,
        expected_unit="cm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_mm_to_m_comparison():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        expected_value=2.4,
        expected_unit="m",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_m_to_mm_comparison():
    property = create_numeric_property(
        value=2.4,
        unit="m",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_mm_to_inch_comparison():
    property = create_numeric_property(
        value=25.4,
        unit="mm",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=1,
        expected_unit="in",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_inch_to_mm_comparison():
    property = create_numeric_property(
        value=1,
        unit="in",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=25.4,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_ft_to_in_comparison():
    property = create_numeric_property(
        value=1,
        unit="ft",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=12,
        expected_unit="in",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_m_to_ft_comparison():
    property = create_numeric_property(
        value=0.3048,
        unit="m",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=1,
        expected_unit="ft",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_incompatible_units_are_not_evaluable():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        expected_value=50,
        expected_unit="kg",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )


# ----------------------------------------------------------------------
# Missing Values
# ----------------------------------------------------------------------


def test_missing_property_value_is_not_evaluable():
    property = create_numeric_property(
        value=None,
        unit="mm",
    )

    constraint = create_constraint()

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )


def test_missing_property_unit_for_measurement_is_not_evaluable():
    property = create_numeric_property(
        value=2400,
        unit=None,
    )

    constraint = create_constraint(
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )


# ----------------------------------------------------------------------
# Enumeration
# ----------------------------------------------------------------------


def test_in_operator_is_satisfied_for_member():
    property = create_string_property(
        value="AAC Block"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.IN,
        expected_value=[
            "AAC Block",
            "Brick",
            "Concrete",
        ],
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_in_operator_is_violated_for_non_member():
    property = create_string_property(
        value="Steel"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.IN,
        expected_value=[
            "AAC Block",
            "Brick",
            "Concrete",
        ],
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.VIOLATED
    )


def test_not_in_operator_is_satisfied_for_non_member():
    property = create_string_property(
        value="Steel"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.NOT_IN,
        expected_value=[
            "AAC Block",
            "Brick",
            "Concrete",
        ],
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


# ----------------------------------------------------------------------
# Regular Expressions
# ----------------------------------------------------------------------


def test_matches_operator_is_satisfied():
    property = create_string_property(
        value="AAC Block"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.MATCHES,
        expected_value=r"^AAC.*",
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


def test_matches_operator_is_violated():
    property = create_string_property(
        value="Brick"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.MATCHES,
        expected_value=r"^AAC.*",
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.VIOLATED
    )


def test_matches_on_numeric_property_is_not_evaluable():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.MATCHES,
        expected_value=r"^30",
        expected_unit=None,
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )


# ----------------------------------------------------------------------
# Property Type Compatibility
# ----------------------------------------------------------------------


def test_numeric_comparison_on_string_property_is_not_evaluable():
    property = create_string_property(
        value="3000"
    )

    constraint = create_constraint(
        property_id="material",
        operator=AtlasConstraintOperator.GREATER_THAN,
        expected_value=2400,
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )


def test_in_operator_with_numeric_property_can_use_numeric_values():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        operator=AtlasConstraintOperator.IN,
        expected_value=[
            2000,
            2500,
            3000,
        ],
        expected_unit="mm",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.SATISFIED
    )


# ----------------------------------------------------------------------
# Non-Mutating Evaluation
# ----------------------------------------------------------------------


def test_constraint_evaluation_does_not_modify_property_value():
    property = create_numeric_property(
        value=2.4,
        unit="m",
        data_type="float",
    )

    constraint = create_constraint(
        expected_value=2400,
        expected_unit="mm",
    )

    original_value = property.value
    original_unit = property.unit

    evaluator = AtlasConstraintEvaluator()

    evaluator.evaluate(
        property,
        constraint,
    )

    assert property.value == original_value
    assert property.unit == original_unit


def test_constraint_evaluation_does_not_modify_constraint_value():
    property = create_numeric_property(
        value=2400,
        unit="mm",
    )

    constraint = create_constraint(
        expected_value=2.4,
        expected_unit="m",
    )

    original_value = constraint.expected_value
    original_unit = constraint.expected_unit

    evaluator = AtlasConstraintEvaluator()

    evaluator.evaluate(
        property,
        constraint,
    )

    assert constraint.expected_value == original_value
    assert constraint.expected_unit == original_unit


# ----------------------------------------------------------------------
# Wrong Property Reference
# ----------------------------------------------------------------------


def test_constraint_for_different_property_is_not_evaluable():
    property = create_numeric_property(
        value=3000,
        unit="mm",
    )

    constraint = create_constraint(
        property_id="width",
    )

    evaluator = AtlasConstraintEvaluator()

    assert (
        evaluator.evaluate(
            property,
            constraint,
        )
        == AtlasConstraintResult.NOT_EVALUABLE
    )
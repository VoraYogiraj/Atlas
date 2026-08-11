"""
ENG-026 — Resource Validation

Tests the runtime validation model defined by ENG-026.

The validation system consists of:

    AtlasValidationCategory
    AtlasValidationSeverity
    AtlasValidationResult
    AtlasValidationRule
    AtlasValidationEngine
"""

from datetime import datetime, timezone

import pytest

from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.validation.category import AtlasValidationCategory
from atlas.validation.engine import AtlasValidationEngine
from atlas.validation.result import AtlasValidationResult
from atlas.validation.rule import AtlasValidationRule
from atlas.validation.severity import AtlasValidationSeverity


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_resource(
    *,
    name: str = "North Wall",
) -> AtlasResource:
    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )

    return AtlasResource(
        classification=classification,
        name=name,
    )


def create_result(
    *,
    resource: AtlasResource | None = None,
    result_id: str = "validation-001",
    category: AtlasValidationCategory = (
        AtlasValidationCategory.PROPERTY
    ),
    severity: AtlasValidationSeverity = (
        AtlasValidationSeverity.ERROR
    ),
    rule: str = "required-height",
    message: str = "Required property missing.",
    explanation: str = "Height is required for this Resource.",
    suggested_resolution: str = "Specify the Resource height.",
    timestamp: datetime | None = None,
) -> AtlasValidationResult:
    resource = resource or create_resource()

    return AtlasValidationResult(
        id=result_id,
        resource_id=resource.aid,
        category=category,
        severity=severity,
        rule=rule,
        message=message,
        explanation=explanation,
        suggested_resolution=suggested_resolution,
        timestamp=timestamp
        or datetime.now(timezone.utc),
    )


# ----------------------------------------------------------------------
# Validation Categories
# ----------------------------------------------------------------------


def test_validation_category_has_identity_category():
    assert AtlasValidationCategory.IDENTITY.value == "identity"


def test_validation_category_has_classification_category():
    assert (
        AtlasValidationCategory.CLASSIFICATION.value
        == "classification"
    )


def test_validation_category_has_property_category():
    assert AtlasValidationCategory.PROPERTY.value == "property"


def test_validation_category_has_relationship_category():
    assert (
        AtlasValidationCategory.RELATIONSHIP.value
        == "relationship"
    )


def test_validation_category_has_semantic_category():
    assert AtlasValidationCategory.SEMANTIC.value == "semantic"


def test_validation_category_has_lifecycle_category():
    assert (
        AtlasValidationCategory.LIFECYCLE.value
        == "lifecycle"
    )


def test_validation_category_has_custom_category():
    assert AtlasValidationCategory.CUSTOM.value == "custom"


def test_validation_category_is_an_enum():
    assert list(AtlasValidationCategory) == [
        AtlasValidationCategory.IDENTITY,
        AtlasValidationCategory.CLASSIFICATION,
        AtlasValidationCategory.PROPERTY,
        AtlasValidationCategory.RELATIONSHIP,
        AtlasValidationCategory.SEMANTIC,
        AtlasValidationCategory.LIFECYCLE,
        AtlasValidationCategory.CUSTOM,
    ]


# ----------------------------------------------------------------------
# Validation Severity
# ----------------------------------------------------------------------


def test_validation_severity_information():
    assert (
        AtlasValidationSeverity.INFORMATION.value
        == "information"
    )


def test_validation_severity_warning():
    assert (
        AtlasValidationSeverity.WARNING.value
        == "warning"
    )


def test_validation_severity_error():
    assert AtlasValidationSeverity.ERROR.value == "error"


def test_validation_severity_critical():
    assert (
        AtlasValidationSeverity.CRITICAL.value
        == "critical"
    )


def test_validation_severity_is_an_enum():
    assert list(AtlasValidationSeverity) == [
        AtlasValidationSeverity.INFORMATION,
        AtlasValidationSeverity.WARNING,
        AtlasValidationSeverity.ERROR,
        AtlasValidationSeverity.CRITICAL,
    ]


def test_validation_severity_is_ordered():
    assert (
        AtlasValidationSeverity.INFORMATION
        < AtlasValidationSeverity.WARNING
        < AtlasValidationSeverity.ERROR
        < AtlasValidationSeverity.CRITICAL
    )


# ----------------------------------------------------------------------
# Validation Result
# ----------------------------------------------------------------------


def test_validation_result_has_id():
    result = create_result()

    assert result.id == "validation-001"


def test_validation_result_has_resource_id():
    resource = create_resource()
    result = create_result(resource=resource)

    assert result.resource_id == resource.aid


def test_validation_result_has_category():
    result = create_result()

    assert result.category == AtlasValidationCategory.PROPERTY


def test_validation_result_has_severity():
    result = create_result()

    assert result.severity == AtlasValidationSeverity.ERROR


def test_validation_result_has_rule():
    result = create_result()

    assert result.rule == "required-height"


def test_validation_result_has_message():
    result = create_result()

    assert result.message == "Required property missing."


def test_validation_result_has_explanation():
    result = create_result()

    assert (
        result.explanation
        == "Height is required for this Resource."
    )


def test_validation_result_has_suggested_resolution():
    result = create_result()

    assert (
        result.suggested_resolution
        == "Specify the Resource height."
    )


def test_validation_result_has_timestamp():
    timestamp = datetime(
        2026,
        8,
        11,
        10,
        30,
        tzinfo=timezone.utc,
    )

    result = create_result(
        timestamp=timestamp
    )

    assert result.timestamp == timestamp


def test_validation_result_is_immutable():
    result = create_result()

    with pytest.raises((AttributeError, TypeError)):
        result.message = "Different message"


def test_validation_result_resource_identity_is_preserved():
    resource = create_resource()

    result = create_result(
        resource=resource
    )

    assert result.resource_id == resource.aid


# ----------------------------------------------------------------------
# Validation Rule
# ----------------------------------------------------------------------


def test_validation_rule_has_id():
    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    assert rule.id == "required-height"


def test_validation_rule_has_category():
    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    assert rule.category == AtlasValidationCategory.PROPERTY


def test_validation_rule_validates_resource():
    resource = create_resource()

    result = create_result(
        resource=resource
    )

    def validate(resource):
        return [result]

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    results = rule.validate(resource)

    assert results == [result]


def test_validation_rule_can_return_no_results():
    resource = create_resource()

    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="complete-resource",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    assert rule.validate(resource) == []


def test_validation_rule_is_immutable():
    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    with pytest.raises((AttributeError, TypeError)):
        rule.id = "different"


def test_validation_rule_category_is_immutable():
    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    with pytest.raises((AttributeError, TypeError)):
        rule.category = AtlasValidationCategory.IDENTITY


# ----------------------------------------------------------------------
# Validation Engine
# ----------------------------------------------------------------------


def test_validation_engine_starts_without_rules():
    engine = AtlasValidationEngine()

    assert engine.rules == []


def test_validation_engine_register_rule():
    engine = AtlasValidationEngine()

    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    result = engine.register_rule(rule)

    assert result is rule
    assert engine.rules == [rule]


def test_validation_engine_preserves_rule_order():
    engine = AtlasValidationEngine()

    def validate_first(resource):
        return []

    def validate_second(resource):
        return []

    first = AtlasValidationRule(
        id="first",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate_first,
    )

    second = AtlasValidationRule(
        id="second",
        category=AtlasValidationCategory.CLASSIFICATION,
        validate=validate_second,
    )

    engine.register_rule(first)
    engine.register_rule(second)

    assert engine.rules == [
        first,
        second,
    ]


def test_validation_engine_rejects_duplicate_rule_id():
    engine = AtlasValidationEngine()

    def validate(resource):
        return []

    first = AtlasValidationRule(
        id="same-rule",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    second = AtlasValidationRule(
        id="same-rule",
        category=AtlasValidationCategory.CUSTOM,
        validate=validate,
    )

    engine.register_rule(first)

    with pytest.raises(ValueError):
        engine.register_rule(second)


def test_validation_engine_get_rule():
    engine = AtlasValidationEngine()

    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    engine.register_rule(rule)

    assert engine.get_rule("required-height") is rule


def test_validation_engine_get_missing_rule_returns_none():
    engine = AtlasValidationEngine()

    assert engine.get_rule("missing-rule") is None


def test_validation_engine_unregister_rule():
    engine = AtlasValidationEngine()

    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    engine.register_rule(rule)

    removed = engine.unregister_rule(
        "required-height"
    )

    assert removed is rule
    assert engine.rules == []


def test_validation_engine_unregister_missing_rule_returns_none():
    engine = AtlasValidationEngine()

    assert (
        engine.unregister_rule("missing-rule")
        is None
    )


def test_validation_engine_rules_returns_copy():
    engine = AtlasValidationEngine()

    def validate(resource):
        return []

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    engine.register_rule(rule)

    rules = engine.rules
    rules.clear()

    assert engine.rules == [rule]


# ----------------------------------------------------------------------
# Validation Execution
# ----------------------------------------------------------------------


def test_validation_engine_without_rules_returns_empty_results():
    engine = AtlasValidationEngine()
    resource = create_resource()

    assert engine.validate(resource) == []


def test_validation_engine_executes_registered_rule():
    engine = AtlasValidationEngine()
    resource = create_resource()

    result = create_result(
        resource=resource
    )

    def validate(resource):
        return [result]

    rule = AtlasValidationRule(
        id="required-height",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate,
    )

    engine.register_rule(rule)

    results = engine.validate(resource)

    assert results == [result]


def test_validation_engine_executes_multiple_rules():
    engine = AtlasValidationEngine()
    resource = create_resource()

    first_result = create_result(
        resource=resource,
        result_id="first-result",
        rule="first-rule",
    )

    second_result = create_result(
        resource=resource,
        result_id="second-result",
        rule="second-rule",
    )

    def validate_first(resource):
        return [first_result]

    def validate_second(resource):
        return [second_result]

    first_rule = AtlasValidationRule(
        id="first-rule",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate_first,
    )

    second_rule = AtlasValidationRule(
        id="second-rule",
        category=AtlasValidationCategory.LIFECYCLE,
        validate=validate_second,
    )

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    results = engine.validate(resource)

    assert results == [
        first_result,
        second_result,
    ]


def test_validation_engine_preserves_rule_execution_order():
    engine = AtlasValidationEngine()
    resource = create_resource()

    execution_order = []

    first_result = create_result(
        resource=resource,
        result_id="first-result",
        rule="first-rule",
    )

    second_result = create_result(
        resource=resource,
        result_id="second-result",
        rule="second-rule",
    )

    def validate_first(resource):
        execution_order.append("first")
        return [first_result]

    def validate_second(resource):
        execution_order.append("second")
        return [second_result]

    first_rule = AtlasValidationRule(
        id="first-rule",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate_first,
    )

    second_rule = AtlasValidationRule(
        id="second-rule",
        category=AtlasValidationCategory.PROPERTY,
        validate=validate_second,
    )

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    results = engine.validate(resource)

    assert execution_order == [
        "first",
        "second",
    ]

    assert results == [
        first_result,
        second_result,
    ]


# ----------------------------------------------------------------------
# Non-Mutating Validation
# ----------------------------------------------------------------------


def test_validation_does_not_change_resource_name():
    engine = AtlasValidationEngine()
    resource = create_resource()

    original_name = resource.name

    def validate(resource):
        return []

    engine.register_rule(
        AtlasValidationRule(
            id="test-rule",
            category=AtlasValidationCategory.CUSTOM,
            validate=validate,
        )
    )

    engine.validate(resource)

    assert resource.name == original_name


def test_validation_does_not_change_resource_classification():
    engine = AtlasValidationEngine()
    resource = create_resource()

    original_classification = resource.classification

    def validate(resource):
        return []

    engine.register_rule(
        AtlasValidationRule(
            id="test-rule",
            category=AtlasValidationCategory.CLASSIFICATION,
            validate=validate,
        )
    )

    engine.validate(resource)

    assert (
        resource.classification
        is original_classification
    )


def test_validation_does_not_change_resource_categories():
    engine = AtlasValidationEngine()
    resource = create_resource()

    def validate(resource):
        return []

    engine.register_rule(
        AtlasValidationRule(
            id="test-rule",
            category=AtlasValidationCategory.CUSTOM,
            validate=validate,
        )
    )

    engine.validate(resource)

    assert resource.categories == []


def test_validation_does_not_change_resource_tags():
    engine = AtlasValidationEngine()
    resource = create_resource()

    def validate(resource):
        return []

    engine.register_rule(
        AtlasValidationRule(
            id="test-rule",
            category=AtlasValidationCategory.SEMANTIC,
            validate=validate,
        )
    )

    engine.validate(resource)

    assert resource.tags == []
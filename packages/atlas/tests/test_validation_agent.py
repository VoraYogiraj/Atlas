"""
ENG-034 — Validation Agent

Tests the Atlas Validation Agent contract.

The Validation Agent:

    - validates Resources through AtlasValidationEngine
    - lists validation rules
    - retrieves validation rules
    - registers validation rules
    - unregisters validation rules
    - preserves validation result integrity
    - preserves rule execution order
    - does not modify Resources
    - does not create a second Validation Engine
    - preserves Agent Request/Result traceability
"""

from datetime import datetime

import pytest

from atlas.agents.context import AtlasAgentContext
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.validation.category import AtlasValidationCategory
from atlas.validation.engine import AtlasValidationEngine
from atlas.validation.result import AtlasValidationResult
from atlas.validation.rule import AtlasValidationRule
from atlas.validation.severity import AtlasValidationSeverity
from atlas.validation_agent.validation_agent import AtlasValidationAgent


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def create_classification(
    *,
    id: str = "wall",
    name: str = "Wall",
) -> AtlasClassification:
    return AtlasClassification(
        id=id,
        name=name,
    )


def create_resource(
    *,
    name: str = "North Wall",
) -> AtlasResource:
    return AtlasResource(
        classification=create_classification(),
        name=name,
    )


def create_result(
    *,
    result_id: str = "result-001",
    resource: AtlasResource,
    category: AtlasValidationCategory = (
        AtlasValidationCategory.PROPERTY
    ),
    severity: AtlasValidationSeverity = (
        AtlasValidationSeverity.ERROR
    ),
    rule: str = "wall-height-required",
    message: str = "Height is required.",
    explanation: str = (
        "Wall height is required for this validation rule."
    ),
    suggested_resolution: str = (
        "Specify the wall height."
    ),
) -> AtlasValidationResult:
    return AtlasValidationResult(
        id=result_id,
        resource_id=resource.aid,
        category=category,
        severity=severity,
        rule=rule,
        message=message,
        explanation=explanation,
        suggested_resolution=suggested_resolution,
        timestamp=datetime.now(),
    )


def create_rule(
    *,
    rule_id: str = "rule-001",
    category: AtlasValidationCategory = (
        AtlasValidationCategory.PROPERTY
    ),
    results: list[AtlasValidationResult] | None = None,
    resource: AtlasResource | None = None,
) -> AtlasValidationRule:
    resource = resource or create_resource()

    fixed_results = list(
        results
        if results is not None
        else [
            create_result(
                resource=resource,
                result_id=f"{rule_id}-result",
                rule=rule_id,
            )
        ]
    )

    def validator(
        target: AtlasResource,
    ) -> list[AtlasValidationResult]:
        return list(fixed_results)

    return AtlasValidationRule(
        id=rule_id,
        category=category,
        validate=validator,
    )


def create_engine() -> AtlasValidationEngine:
    return AtlasValidationEngine()


def create_context(
    *,
    validation_engine: AtlasValidationEngine | None = None,
    metadata: dict | None = None,
) -> AtlasAgentContext:
    return AtlasAgentContext(
        validation_engine=validation_engine,
        metadata=dict(
            metadata or {}
        ),
    )


def create_request(
    *,
    request_id: str = "request-001",
    action: str = "validate_resource",
    validation_engine: AtlasValidationEngine | None = None,
    metadata: dict | None = None,
) -> AtlasAgentRequest:
    return AtlasAgentRequest(
        id=request_id,
        action=action,
        context=create_context(
            validation_engine=validation_engine,
            metadata=metadata,
        ),
    )


def create_agent() -> AtlasValidationAgent:
    return AtlasValidationAgent()


# ----------------------------------------------------------------------
# Identity
# ----------------------------------------------------------------------


def test_validation_agent_has_default_id():
    agent = create_agent()

    assert agent.id == "validation-agent"


def test_validation_agent_has_default_name():
    agent = create_agent()

    assert agent.name == "Validation Agent"


def test_validation_agent_starts_idle():
    agent = create_agent()

    assert agent.status is AtlasAgentStatus.IDLE


# ----------------------------------------------------------------------
# Context
# ----------------------------------------------------------------------


def test_validation_agent_requires_validation_engine():
    resource = create_resource()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=None,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_validation_agent_requires_resource_for_validation():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_validation_agent_rejects_invalid_resource():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": "not-a-resource",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------


def test_validation_agent_validates_resource():
    engine = create_engine()

    resource = create_resource()

    rule = create_rule(
        resource=resource,
    )

    engine.register_rule(
        rule
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert len(result.output) == 1
    assert result.output[0].rule == "rule-001"


def test_validation_agent_returns_empty_list_when_no_findings():
    engine = create_engine()

    resource = create_resource()

    def validator(
        target: AtlasResource,
    ) -> list[AtlasValidationResult]:
        return []

    engine.register_rule(
        AtlasValidationRule(
            id="clean-rule",
            category=AtlasValidationCategory.PROPERTY,
            validate=validator,
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == []


def test_validation_agent_preserves_rule_execution_order():
    engine = create_engine()

    resource = create_resource()

    first = create_result(
        result_id="first-result",
        resource=resource,
        rule="first-rule",
        message="First",
    )

    second = create_result(
        result_id="second-result",
        resource=resource,
        rule="second-rule",
        message="Second",
    )

    first_rule = create_rule(
        rule_id="first-rule",
        resource=resource,
        results=[first],
    )

    second_rule = create_rule(
        rule_id="second-rule",
        resource=resource,
        results=[second],
    )

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert [
        finding.rule
        for finding in result.output
    ] == [
        "first-rule",
        "second-rule",
    ]


def test_validation_agent_preserves_result_objects():
    engine = create_engine()

    resource = create_resource()

    finding = create_result(
        resource=resource,
        result_id="immutable-result",
    )

    engine.register_rule(
        create_rule(
            rule_id="rule-immutable",
            resource=resource,
            results=[finding],
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.output[0] is finding


def test_validation_agent_preserves_result_content():
    engine = create_engine()

    resource = create_resource()

    finding = create_result(
        resource=resource,
        result_id="finding-001",
        category=AtlasValidationCategory.CLASSIFICATION,
        severity=AtlasValidationSeverity.WARNING,
        rule="classification-rule",
        message="Classification should be reviewed.",
        explanation="The classification requires review.",
        suggested_resolution="Review classification.",
    )

    engine.register_rule(
        create_rule(
            rule_id="classification-rule",
            category=AtlasValidationCategory.CLASSIFICATION,
            resource=resource,
            results=[finding],
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    returned = result.output[0]

    assert returned.id == "finding-001"
    assert returned.resource_id == resource.aid
    assert returned.category is (
        AtlasValidationCategory.CLASSIFICATION
    )
    assert returned.severity is (
        AtlasValidationSeverity.WARNING
    )
    assert returned.rule == "classification-rule"
    assert returned.message == (
        "Classification should be reviewed."
    )
    assert returned.explanation == (
        "The classification requires review."
    )
    assert returned.suggested_resolution == (
        "Review classification."
    )


# ----------------------------------------------------------------------
# Validation Engine Failure
# ----------------------------------------------------------------------


def test_validation_agent_returns_failed_on_engine_exception():
    resource = create_resource()

    engine = create_engine()

    class BrokenRule:
        pass

    # Force an engine-side execution failure using a rule validator.
    def broken_validator(
        target: AtlasResource,
    ) -> list[AtlasValidationResult]:
        raise RuntimeError(
            "validation engine failure"
        )

    engine.register_rule(
        AtlasValidationRule(
            id="broken-rule",
            category=AtlasValidationCategory.CUSTOM,
            validate=broken_validator,
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert "validation engine failure" in (
        result.error
    )


# ----------------------------------------------------------------------
# Rule Listing
# ----------------------------------------------------------------------


def test_validation_agent_lists_rules():
    engine = create_engine()

    first = create_rule(
        rule_id="first-rule",
    )

    second = create_rule(
        rule_id="second-rule",
    )

    engine.register_rule(first)
    engine.register_rule(second)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output == [
        first,
        second,
    ]


def test_validation_agent_list_rules_preserves_registration_order():
    engine = create_engine()

    rules = [
        create_rule(rule_id="one"),
        create_rule(rule_id="two"),
        create_rule(rule_id="three"),
    ]

    for rule in rules:
        engine.register_rule(rule)

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert result.output == rules


def test_validation_agent_list_rules_returns_new_list():
    engine = create_engine()

    rule = create_rule()

    engine.register_rule(
        rule
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    result.output.clear()

    assert engine.rules == [
        rule
    ]


def test_validation_agent_list_rules_requires_engine():
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=None,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Rule Lookup
# ----------------------------------------------------------------------


def test_validation_agent_get_rule():
    engine = create_engine()

    rule = create_rule(
        rule_id="height-rule",
    )

    engine.register_rule(
        rule
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_rule",
            validation_engine=engine,
            metadata={
                "rule_id": "height-rule",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is rule


def test_validation_agent_get_missing_rule_returns_none():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_rule",
            validation_engine=engine,
            metadata={
                "rule_id": "missing-rule",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None
    assert result.error is None


def test_validation_agent_get_rule_requires_rule_id():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="get_rule",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Rule Registration
# ----------------------------------------------------------------------


def test_validation_agent_registers_rule():
    engine = create_engine()

    rule = create_rule(
        rule_id="registered-rule",
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="register_rule",
            validation_engine=engine,
            metadata={
                "rule": rule,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is rule
    assert engine.get_rule(
        "registered-rule"
    ) is rule


def test_validation_agent_register_rule_requires_rule():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="register_rule",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_validation_agent_register_rule_rejects_invalid_type():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="register_rule",
            validation_engine=engine,
            metadata={
                "rule": "not-a-rule",
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


def test_validation_agent_register_duplicate_rule_fails():
    engine = create_engine()

    rule = create_rule(
        rule_id="duplicate-rule",
    )

    engine.register_rule(
        rule
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="register_rule",
            validation_engine=engine,
            metadata={
                "rule": rule,
            },
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert engine.rules == [
        rule
    ]


# ----------------------------------------------------------------------
# Rule Removal
# ----------------------------------------------------------------------


def test_validation_agent_unregisters_rule():
    engine = create_engine()

    rule = create_rule(
        rule_id="remove-rule",
    )

    engine.register_rule(
        rule
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="unregister_rule",
            validation_engine=engine,
            metadata={
                "rule_id": "remove-rule",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is rule
    assert engine.get_rule(
        "remove-rule"
    ) is None


def test_validation_agent_unregister_missing_rule_returns_none():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="unregister_rule",
            validation_engine=engine,
            metadata={
                "rule_id": "missing-rule",
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
    assert result.output is None
    assert result.error is None


def test_validation_agent_unregister_requires_rule_id():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="unregister_rule",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Non-Mutation
# ----------------------------------------------------------------------


def test_validation_agent_does_not_modify_resource():
    engine = create_engine()

    resource = create_resource(
        name="Original Wall",
    )

    original_aid = resource.aid
    original_name = resource.name
    original_classification = (
        resource.classification
    )

    engine.register_rule(
        create_rule(
            resource=resource,
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED

    assert resource.aid == original_aid
    assert resource.name == original_name
    assert (
        resource.classification
        is original_classification
    )


def test_validation_agent_multiple_validations_do_not_modify_resource():
    engine = create_engine()

    resource = create_resource()

    engine.register_rule(
        create_rule(
            resource=resource,
        )
    )

    agent = create_agent()

    first = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    second = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert first.status is AtlasAgentStatus.COMPLETED
    assert second.status is AtlasAgentStatus.COMPLETED
    assert resource.name == "North Wall"


# ----------------------------------------------------------------------
# Shared Engine
# ----------------------------------------------------------------------


def test_validation_agent_uses_supplied_engine():
    engine = create_engine()

    rule = create_rule(
        rule_id="shared-rule",
    )

    engine.register_rule(
        rule
    )

    agent = create_agent()

    first = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    second = agent.execute(
        create_request(
            action="get_rule",
            validation_engine=engine,
            metadata={
                "rule_id": "shared-rule",
            },
        )
    )

    assert first.output == [
        rule
    ]

    assert second.output is rule


def test_validation_agent_does_not_create_new_engine_per_request():
    engine = create_engine()

    rule = create_rule(
        rule_id="persistent-rule",
    )

    agent = create_agent()

    register_result = agent.execute(
        create_request(
            action="register_rule",
            validation_engine=engine,
            metadata={
                "rule": rule,
            },
        )
    )

    list_result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert register_result.status is (
        AtlasAgentStatus.COMPLETED
    )

    assert list_result.output == [
        rule
    ]


# ----------------------------------------------------------------------
# Categories and Severity
# ----------------------------------------------------------------------


def test_validation_agent_preserves_validation_category():
    engine = create_engine()

    resource = create_resource()

    result_object = create_result(
        resource=resource,
        category=AtlasValidationCategory.SEMANTIC,
        severity=AtlasValidationSeverity.WARNING,
    )

    engine.register_rule(
        create_rule(
            rule_id="semantic-rule",
            category=AtlasValidationCategory.SEMANTIC,
            resource=resource,
            results=[result_object],
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.output[0].category is (
        AtlasValidationCategory.SEMANTIC
    )


def test_validation_agent_preserves_validation_severity():
    engine = create_engine()

    resource = create_resource()

    result_object = create_result(
        resource=resource,
        severity=AtlasValidationSeverity.CRITICAL,
    )

    engine.register_rule(
        create_rule(
            rule_id="critical-rule",
            resource=resource,
            results=[result_object],
        )
    )

    agent = create_agent()

    result = agent.execute(
        create_request(
            action="validate_resource",
            validation_engine=engine,
            metadata={
                "resource": resource,
            },
        )
    )

    assert result.output[0].severity is (
        AtlasValidationSeverity.CRITICAL
    )


# ----------------------------------------------------------------------
# Unsupported Actions
# ----------------------------------------------------------------------


def test_validation_agent_rejects_unknown_action():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="generate_validation_rules",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None
    assert result.error is not None


def test_validation_agent_rejects_ai_validation_action():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="predict_validation_failure",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.FAILED
    assert result.output is None


# ----------------------------------------------------------------------
# Traceability
# ----------------------------------------------------------------------


def test_validation_agent_preserves_request_id():
    engine = create_engine()

    agent = create_agent()

    result = agent.execute(
        create_request(
            request_id="validation-request-123",
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert result.request_id == (
        "validation-request-123"
    )


def test_validation_agent_result_contains_agent_id():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert result.agent_id == (
        "validation-agent"
    )


def test_validation_agent_result_is_agent_result():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert isinstance(
        result,
        AtlasAgentResult,
    )


# ----------------------------------------------------------------------
# Non-AI Implementation
# ----------------------------------------------------------------------


def test_validation_agent_does_not_require_ai_provider():
    engine = create_engine()
    agent = create_agent()

    result = agent.execute(
        create_request(
            action="list_rules",
            validation_engine=engine,
        )
    )

    assert result.status is AtlasAgentStatus.COMPLETED
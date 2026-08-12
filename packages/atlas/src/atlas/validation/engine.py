"""
Atlas Validation Engine

Executes registered validation rules against Atlas Resources.

Specification:
ENG-008 — Resource Validation
ENG-026 — Resource Validation Runtime Model
"""

from __future__ import annotations

from atlas.core.resource import AtlasResource
from atlas.validation.rule import AtlasValidationRule
from atlas.validation.result import AtlasValidationResult


class AtlasValidationEngine:
    """
    Executes registered validation rules against Resources.

    The engine observes Resources and never modifies them.
    """

    def __init__(self) -> None:
        self._rules: dict[str, AtlasValidationRule] = {}

    # ------------------------------------------------------------------
    # Rule Registration
    # ------------------------------------------------------------------

    def register_rule(
        self,
        rule: AtlasValidationRule,
    ) -> AtlasValidationRule:
        """
        Register a validation rule.

        Raises
        ------
        TypeError
            If rule is not an AtlasValidationRule.

        ValueError
            If a rule with the same ID already exists.
        """
        if not isinstance(
            rule,
            AtlasValidationRule,
        ):
            raise TypeError(
                "rule must be an AtlasValidationRule"
            )

        if rule.id in self._rules:
            raise ValueError(
                f"Validation rule already exists: {rule.id}"
            )

        self._rules[rule.id] = rule

        return rule

    # ------------------------------------------------------------------
    # Rule Lookup
    # ------------------------------------------------------------------

    def get_rule(
        self,
        rule_id: str,
    ) -> AtlasValidationRule | None:
        """
        Return a validation rule by ID.

        Returns None when the rule is not registered.
        """
        return self._rules.get(rule_id)

    # ------------------------------------------------------------------
    # Rule Removal
    # ------------------------------------------------------------------

    def unregister_rule(
        self,
        rule_id: str,
    ) -> AtlasValidationRule | None:
        """
        Remove and return a validation rule.

        Returns None when the rule is not registered.
        """
        return self._rules.pop(
            rule_id,
            None,
        )

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def rules(self) -> list[AtlasValidationRule]:
        """
        Return registered validation rules.

        Rules preserve registration order.
        """
        return list(
            self._rules.values()
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        resource: AtlasResource,
    ) -> list[AtlasValidationResult]:
        """
        Execute all registered validation rules against a Resource.

        Results preserve rule execution order.
        """
        results: list[AtlasValidationResult] = []

        for rule in self._rules.values():
            results.extend(
                rule.validate(resource)
            )

        return results

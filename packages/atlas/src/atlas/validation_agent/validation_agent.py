"""
Atlas Validation Agent

Specification:
ENG-034 — Validation Agent
"""

from __future__ import annotations

from typing import Any

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.core.resource import AtlasResource
from atlas.validation.engine import AtlasValidationEngine
from atlas.validation.rule import AtlasValidationRule


class AtlasValidationAgent(AtlasAgent):
    """
    Agent responsible for explicit Atlas validation operations.

    ENG-034 v0.1 is deterministic.

    The Agent delegates validation behavior to the existing
    AtlasValidationEngine and does not implement a second validation
    engine.
    """

    DEFAULT_ID = "validation-agent"
    DEFAULT_NAME = "Validation Agent"

    def __init__(self) -> None:
        super().__init__(
            id=self.DEFAULT_ID,
            name=self.DEFAULT_NAME,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """
        Execute a Validation Agent operation.

        Supported actions:

            validate_resource
            list_rules
            get_rule
            register_rule
            unregister_rule
        """
        try:
            engine = self._get_engine(request)

            handlers = {
                "validate_resource": self._validate_resource,
                "list_rules": self._list_rules,
                "get_rule": self._get_rule,
                "register_rule": self._register_rule,
                "unregister_rule": self._unregister_rule,
            }

            handler = handlers.get(
                request.action
            )

            if handler is None:
                return self._failure(
                    request,
                    (
                        "Unsupported Validation Agent "
                        f"action: {request.action}"
                    ),
                )

            return handler(
                request,
                engine,
            )

        except Exception as exc:
            return self._failure(
                request,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_resource(
        self,
        request: AtlasAgentRequest,
        engine: AtlasValidationEngine,
    ) -> AtlasAgentResult:
        resource = request.context.metadata.get(
            "resource"
        )

        if not isinstance(
            resource,
            AtlasResource,
        ):
            return self._failure(
                request,
                (
                    "resource metadata must be "
                    "an AtlasResource"
                ),
            )

        results = engine.validate(
            resource
        )

        return self._success(
            request,
            list(results),
        )

    # ------------------------------------------------------------------
    # Rule Listing
    # ------------------------------------------------------------------

    def _list_rules(
        self,
        request: AtlasAgentRequest,
        engine: AtlasValidationEngine,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            list(engine.rules),
        )

    # ------------------------------------------------------------------
    # Rule Lookup
    # ------------------------------------------------------------------

    def _get_rule(
        self,
        request: AtlasAgentRequest,
        engine: AtlasValidationEngine,
    ) -> AtlasAgentResult:
        rule_id = request.context.metadata.get(
            "rule_id"
        )

        if rule_id is None:
            return self._failure(
                request,
                "rule_id metadata is required",
            )

        if not isinstance(
            rule_id,
            str,
        ):
            return self._failure(
                request,
                "rule_id must be a string",
            )

        if not rule_id.strip():
            return self._failure(
                request,
                "rule_id cannot be empty",
            )

        return self._success(
            request,
            engine.get_rule(
                rule_id
            ),
        )

    # ------------------------------------------------------------------
    # Rule Registration
    # ------------------------------------------------------------------

    def _register_rule(
        self,
        request: AtlasAgentRequest,
        engine: AtlasValidationEngine,
    ) -> AtlasAgentResult:
        rule = request.context.metadata.get(
            "rule"
        )

        if not isinstance(
            rule,
            AtlasValidationRule,
        ):
            return self._failure(
                request,
                (
                    "rule metadata must be "
                    "an AtlasValidationRule"
                ),
            )

        registered = engine.register_rule(
            rule
        )

        return self._success(
            request,
            registered,
        )

    # ------------------------------------------------------------------
    # Rule Removal
    # ------------------------------------------------------------------

    def _unregister_rule(
        self,
        request: AtlasAgentRequest,
        engine: AtlasValidationEngine,
    ) -> AtlasAgentResult:
        rule_id = request.context.metadata.get(
            "rule_id"
        )

        if rule_id is None:
            return self._failure(
                request,
                "rule_id metadata is required",
            )

        if not isinstance(
            rule_id,
            str,
        ):
            return self._failure(
                request,
                "rule_id must be a string",
            )

        if not rule_id.strip():
            return self._failure(
                request,
                "rule_id cannot be empty",
            )

        return self._success(
            request,
            engine.unregister_rule(
                rule_id
            ),
        )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    @staticmethod
    def _get_engine(
        request: AtlasAgentRequest,
    ) -> AtlasValidationEngine:
        engine = request.context.validation_engine

        if not isinstance(
            engine,
            AtlasValidationEngine,
        ):
            raise ValueError(
                "AtlasValidationEngine is required "
                "in Agent context"
            )

        return engine

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _success(
        self,
        request: AtlasAgentRequest,
        output: Any,
    ) -> AtlasAgentResult:
        self._set_status(
            AtlasAgentStatus.COMPLETED
        )

        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.COMPLETED,
            output=output,
            error=None,
        )

    def _failure(
        self,
        request: AtlasAgentRequest,
        error: str,
    ) -> AtlasAgentResult:
        self._set_status(
            AtlasAgentStatus.FAILED
        )

        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.FAILED,
            output=None,
            error=error,
        )
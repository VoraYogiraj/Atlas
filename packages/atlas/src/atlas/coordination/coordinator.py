"""
Atlas Agent Coordinator

Specification:
ENG-035 — Multi-Agent Coordination
"""

from __future__ import annotations

from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.runtime import AtlasAgentRuntime
from atlas.agents.status import AtlasAgentStatus
from atlas.orchestrator.orchestrator import AtlasOrchestrator


class AtlasAgentCoordinator:
    """
    Coordinates explicit Agent-to-Agent delegation through the
    AtlasOrchestrator.

    ENG-035 v0.1 is deterministic and sequential.
    """

    DEFAULT_MAX_DELEGATION_DEPTH = 8

    def __init__(
        self,
        *,
        orchestrator: AtlasOrchestrator,
        max_delegation_depth: int = (
            DEFAULT_MAX_DELEGATION_DEPTH
        ),
    ) -> None:
        if not isinstance(
            max_delegation_depth,
            int,
        ):
            raise TypeError(
                "max_delegation_depth must be an integer"
            )

        if max_delegation_depth < 0:
            raise ValueError(
                "max_delegation_depth must be greater than or equal to 0"
            )

        self._orchestrator = orchestrator
        self._max_delegation_depth = (
            max_delegation_depth
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @property
    def orchestrator(self) -> AtlasOrchestrator:
        """Return the Orchestrator used for delegation."""
        return self._orchestrator

    @property
    def runtime(self) -> AtlasAgentRuntime:
        """Return the Orchestrator's underlying Agent Runtime."""
        return self._orchestrator.runtime

    @property
    def max_delegation_depth(self) -> int:
        """Return the maximum supported delegation depth."""
        return self._max_delegation_depth

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    def delegate(
        self,
        *,
        target_agent_id: str,
        request: AtlasAgentRequest,
        delegated_by: str,
        coordination_id: str | None = None,
    ) -> AtlasAgentResult:
        """
        Delegate a request to another Agent through the Orchestrator.

        The original request remains immutable.

        A derived request is created with coordination metadata.
        """
        if not isinstance(
            target_agent_id,
            str,
        ) or not target_agent_id.strip():
            return self._failure(
                request,
                "target_agent_id is required",
            )

        if not isinstance(
            delegated_by,
            str,
        ) or not delegated_by.strip():
            return self._failure(
                request,
                "delegated_by is required",
            )

        current_depth = request.context.metadata.get(
            "delegation_depth",
            0,
        )

        if not isinstance(
            current_depth,
            int,
        ):
            return self._failure(
                request,
                "delegation_depth must be an integer",
            )

        if current_depth < 0:
            return self._failure(
                request,
                "delegation_depth cannot be negative",
            )

        if (
            current_depth
            >= self._max_delegation_depth
        ):
            return self._failure(
                request,
                (
                    "Maximum delegation depth exceeded: "
                    f"{current_depth} >= "
                    f"{self._max_delegation_depth}"
                ),
            )

        if coordination_id is not None:
            if not isinstance(
                coordination_id,
                str,
            ) or not coordination_id.strip():
                return self._failure(
                    request,
                    "coordination_id cannot be empty",
                )

        existing_coordination_id = (
            request.context.metadata.get(
                "coordination_id"
            )
        )

        if coordination_id is None:
            coordination_id = (
                existing_coordination_id
            )

        if coordination_id is not None:
            if not isinstance(
                coordination_id,
                str,
            ) or not coordination_id.strip():
                return self._failure(
                    request,
                    "coordination_id cannot be empty",
                )

        # --------------------------------------------------------------
        # Build derived coordination metadata.
        #
        # A request entering this delegation already has a depth.
        # The delegated request moves one level deeper.
        # --------------------------------------------------------------

        delegated_depth = (
            current_depth + 1
        )

        metadata = dict(
            request.context.metadata
        )

        metadata["parent_request_id"] = (
            request.id
        )

        metadata["delegated_by"] = (
            delegated_by
        )

        metadata["delegation_depth"] = (
            delegated_depth
        )

        if coordination_id is not None:
            metadata["coordination_id"] = (
                coordination_id
            )

        # --------------------------------------------------------------
        # Create a new immutable request context.
        # --------------------------------------------------------------

        delegated_context = type(
            request.context
        )(
            project=request.context.project,
            resource_registry=(
                request.context.resource_registry
            ),
            resource_graph=(
                request.context.resource_graph
            ),
            classification_registry=(
                request.context.classification_registry
            ),
            classification_hierarchy=(
                request.context.classification_hierarchy
            ),
            validation_engine=(
                request.context.validation_engine
            ),
            metadata=metadata,
        )

        delegated_request = AtlasAgentRequest(
            id=request.id,
            action=request.action,
            context=delegated_context,
        )

        # --------------------------------------------------------------
        # Confirm target Agent exists before dispatch.
        # --------------------------------------------------------------

        target_agent = self.runtime.get_agent(
            target_agent_id
        )

        if target_agent is None:
            return self._failure(
                request,
                f"Agent not found: {target_agent_id}",
            )

        # --------------------------------------------------------------
        # Delegate exclusively through the Orchestrator.
        # --------------------------------------------------------------

        return self._orchestrator.dispatch(
            target_agent_id,
            delegated_request,
        )

    # ------------------------------------------------------------------
    # Result Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _failure(
        request: AtlasAgentRequest,
        error: str,
    ) -> AtlasAgentResult:
        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id="coordination",
            status=AtlasAgentStatus.FAILED,
            output=None,
            error=error,
        )
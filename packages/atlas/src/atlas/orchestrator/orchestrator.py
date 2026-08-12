"""
Atlas Orchestrator Agent

Specification:
ENG-029 — Orchestrator Agent
"""

from __future__ import annotations

from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.runtime import AtlasAgentRuntime


class AtlasOrchestrator:
    """
    Top-level coordination component for the Atlas Agent Runtime.

    The Orchestrator routes Agent Requests to registered Agents through
    an existing AtlasAgentRuntime.

    It does not implement domain-specific Resource, Registry, Semantic,
    Relationship, or Validation logic.
    """

    DEFAULT_ID = "orchestrator-agent"
    DEFAULT_NAME = "Orchestrator Agent"

    def __init__(
        self,
        *,
        runtime: AtlasAgentRuntime,
    ) -> None:
        self._runtime = runtime

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Return the stable Orchestrator ID."""
        return self.DEFAULT_ID

    @property
    def name(self) -> str:
        """Return the human-readable Orchestrator name."""
        return self.DEFAULT_NAME

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    @property
    def runtime(self) -> AtlasAgentRuntime:
        """
        Return the existing Agent Runtime used by the Orchestrator.
        """
        return self._runtime

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch(
        self,
        target_agent_id: str,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """
        Dispatch an Agent Request to a registered target Agent.

        The Request is passed to the existing Runtime unchanged.

        Unknown Agents raise KeyError.

        Agent execution failures are returned by the Runtime as
        FAILED AtlasAgentResult objects.
        """
        return self._runtime.execute(
            target_agent_id,
            request,
        )
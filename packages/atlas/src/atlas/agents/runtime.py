"""
Atlas Agent Runtime

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus


class AtlasAgentRuntime:
    """
    Runtime responsible for registering and executing Atlas Agents.

    The Runtime does not implement domain-specific Agent behavior.
    """

    def __init__(self) -> None:
        self._agents: dict[str, AtlasAgent] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_agent(
        self,
        agent: AtlasAgent,
    ) -> AtlasAgent:
        """
        Register an Agent.

        Raises
        ------
        TypeError
            If agent is not an AtlasAgent.

        ValueError
            If the Agent ID is already registered.
        """
        if not isinstance(
            agent,
            AtlasAgent,
        ):
            raise TypeError(
                "agent must be an AtlasAgent"
            )

        if agent.id in self._agents:
            raise ValueError(
                f"Agent already registered: {agent.id}"
            )

        self._agents[agent.id] = agent

        return agent

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_agent(
        self,
        agent_id: str,
    ) -> AtlasAgent | None:
        """
        Return an Agent by ID.

        Returns None when the Agent is not registered.
        """
        return self._agents.get(
            agent_id
        )

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def unregister_agent(
        self,
        agent_id: str,
    ) -> AtlasAgent | None:
        """
        Remove and return an Agent.

        Returns None when the Agent is not registered.
        """
        return self._agents.pop(
            agent_id,
            None,
        )

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    @property
    def agents(self) -> list[AtlasAgent]:
        """
        Return registered Agents in registration order.

        A copy is returned so the internal registry cannot be modified
        by callers.
        """
        return list(
            self._agents.values()
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        agent_id: str,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """
        Execute a Request through a registered Agent.

        Unknown Agents raise KeyError.

        Agent exceptions are converted into FAILED results and do not
        unregister the Agent.
        """
        agent = self._agents.get(
            agent_id
        )

        if agent is None:
            raise KeyError(
                f"Agent not found: {agent_id}"
            )

        agent._set_status(
            AtlasAgentStatus.RUNNING
        )

        try:
            result = agent.execute(
                request
            )
        except Exception as exc:
            agent._set_status(
                AtlasAgentStatus.FAILED
            )

            return AtlasAgentResult(
                id=f"result-{request.id}",
                request_id=request.id,
                agent_id=agent.id,
                status=AtlasAgentStatus.FAILED,
                output=None,
                error=str(exc),
            )

        # Keep the Agent status synchronized with the execution result.
        if result.status is AtlasAgentStatus.COMPLETED:
            agent._set_status(
                AtlasAgentStatus.COMPLETED
            )
        elif result.status is AtlasAgentStatus.FAILED:
            agent._set_status(
                AtlasAgentStatus.FAILED
            )

        return result
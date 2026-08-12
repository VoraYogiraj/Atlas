"""
Atlas Agent

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus


class AtlasAgent(ABC):
    """
    Base class for Atlas Agents.

    Specialized Agents implement execute().
    """

    def __init__(
        self,
        *,
        id: str,
        name: str,
    ) -> None:
        self._id = id
        self._name = name
        self._status = AtlasAgentStatus.IDLE

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Return the stable Agent ID."""
        return self._id

    @property
    def name(self) -> str:
        """Return the human-readable Agent name."""
        return self._name

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def status(self) -> AtlasAgentStatus:
        """Return the current Agent status."""
        return self._status

    def _set_status(
        self,
        status: AtlasAgentStatus,
    ) -> None:
        self._status = status

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """
        Execute an Agent Request.

        Specialized Agents must implement this method.
        """
        raise NotImplementedError
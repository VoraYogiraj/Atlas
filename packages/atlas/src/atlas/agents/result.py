"""
Atlas Agent Result

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.agents.status import AtlasAgentStatus


@dataclass(frozen=True, slots=True)
class AtlasAgentResult:
    """
    Immutable result produced by an Atlas Agent execution.
    """

    id: str
    request_id: str
    agent_id: str
    status: AtlasAgentStatus
    output: Any = None
    error: str | None = None
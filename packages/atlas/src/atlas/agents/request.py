"""
Atlas Agent Request

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.agents.context import AtlasAgentContext


@dataclass(frozen=True, slots=True)
class AtlasAgentRequest:
    """
    Immutable request sent to an Atlas Agent.
    """

    id: str
    action: str
    context: AtlasAgentContext
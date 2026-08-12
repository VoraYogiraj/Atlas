"""
Atlas Agent Status

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from enum import Enum


class AtlasAgentStatus(str, Enum):
    """
    Runtime status of an Atlas Agent.
    """

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
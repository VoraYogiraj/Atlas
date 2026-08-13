"""
Atlas Application Commands

ENG-039 — Atlas UI Architecture

Commands represent user or system intent that may change engineering state.
They do not contain Atlas domain rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AtlasCommand:
    """
    Explicit application operation request.

    Commands describe intent. They do not implement engineering rules.
    """

    name: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dictionary")
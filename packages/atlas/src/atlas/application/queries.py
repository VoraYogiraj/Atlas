"""
Atlas Application Queries

ENG-039 — Atlas UI Architecture

Queries represent read-only application requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AtlasQuery:
    """
    Explicit application read request.
    """

    name: str
    parameters: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if not isinstance(self.parameters, dict):
            raise TypeError("parameters must be a dictionary")
"""
Atlas Agent Context

ENG-028 — Agent Runtime Core
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AtlasAgentContext:
    """
    Execution context available to an Atlas Agent.

    The context does not transfer ownership of any Atlas domain object.
    """

    project: Any = None
    resource_registry: Any = None
    resource_graph: Any = None
    classification_registry: Any = None
    classification_hierarchy: Any = None
    validation_engine: Any = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )
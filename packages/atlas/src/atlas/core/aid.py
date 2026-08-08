"""
AtlasID (AID)

Defines the globally unique identity used by every Atlas Resource.

Specification:
    ENG-002 — Resource Identity
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class AtlasID:
    """
    Immutable identifier for an Atlas Resource.

    Every Atlas Resource owns exactly one AtlasID.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "AtlasID":
        """
        Generate a new AtlasID.
        """
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "AtlasID":
        """
        Create an AtlasID from a string.
        """
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"AtlasID('{self.value}')"

    def to_dict(self) -> dict[str, str]:
        """
        Serialize the AtlasID.
        """
        return {
            "aid": str(self.value)
        }
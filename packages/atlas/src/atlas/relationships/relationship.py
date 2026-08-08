"""
Atlas Relationship

Defines an engineering relationship between two Atlas Resources.

Specification:
    ENG-005 — Resource Relationships
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atlas.core.resource import AtlasResource


@dataclass(slots=True)
class AtlasRelationship:
    """
    Represents a directed engineering relationship between two Resources.

    Example:
        Wall --contains--> Door
    """

    id: str
    relationship_type: str

    source: "AtlasResource"
    target: "AtlasResource"

    description: str = ""

    @property
    def is_self_reference(self) -> bool:
        """
        Returns True if the relationship connects a Resource to itself.
        """
        return self.source.aid == self.target.aid

    def involves(self, resource: "AtlasResource") -> bool:
        """
        Returns True if the supplied Resource participates
        in this relationship.
        """
        return (
            resource.aid == self.source.aid
            or resource.aid == self.target.aid
        )

    def __repr__(self) -> str:
        return (
            f"AtlasRelationship("
            f"type='{self.relationship_type}', "
            f"source={self.source.aid}, "
            f"target={self.target.aid})"
        )
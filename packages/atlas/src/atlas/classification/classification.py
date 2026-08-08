"""
Atlas Classification

Defines the engineering classification of Atlas Resources.

Specification:
    ENG-003 — Resource Classification
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class AtlasClassification:
    """
    Represents an engineering classification.

    A classification defines *what* a Resource is.

    Classifications are immutable and reusable across
    many Atlas Resources.
    """

    id: str
    name: str
    description: str = ""
    parent: Optional["AtlasClassification"] = None

    @property
    def path(self) -> tuple[str, ...]:
        """
        Returns the complete classification hierarchy.

        Example
        -------
        (
            "Physical Resource",
            "Building Element",
            "Wall",
        )
        """
        if self.parent is None:
            return (self.name,)

        return (*self.parent.path, self.name)

    @property
    def depth(self) -> int:
        """
        Returns the hierarchy depth.

        Root classifications have depth 0.
        """
        return len(self.path) - 1

    @property
    def is_root(self) -> bool:
        """
        Returns True if this classification has no parent.
        """
        return self.parent is None

    def is_descendant_of(
        self,
        other: "AtlasClassification",
    ) -> bool:
        """
        Returns True if this classification is a descendant
        of another classification.
        """
        current = self.parent

        while current is not None:
            if current == other:
                return True

            current = current.parent

        return False

    def is_ancestor_of(
        self,
        other: "AtlasClassification",
    ) -> bool:
        """
        Returns True if this classification is an ancestor
        of another classification.
        """
        return other.is_descendant_of(self)

    def __str__(self) -> str:
        return " > ".join(self.path)

    def __repr__(self) -> str:
        return (
            f"AtlasClassification("
            f"id='{self.id}', "
            f"name='{self.name}')"
        )
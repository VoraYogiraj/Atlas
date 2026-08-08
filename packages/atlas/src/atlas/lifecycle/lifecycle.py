"""
Atlas Lifecycle

Defines the lifecycle state of an Atlas Resource.

Specification:
    ENG-007 — Resource Lifecycle
"""

from __future__ import annotations

from enum import Enum


class AtlasLifecycle(str, Enum):
    """
    Represents the lifecycle state of an Atlas Resource.

    Lifecycle states describe the current state of a Resource,
    not the history of changes made to it.
    """

    CREATED = "created"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """Return True when the Resource is active."""
        return self is AtlasLifecycle.ACTIVE

    def is_terminal(self) -> bool:
        """
        Return True when the lifecycle state represents
        a terminal state.
        """
        return self in {
            AtlasLifecycle.ARCHIVED,
            AtlasLifecycle.DELETED,
        }

    def can_transition_to(self, target: "AtlasLifecycle") -> bool:
        """
        Determine whether a lifecycle transition is allowed.

        Current v0.1 transition model:

            CREATED  -> ACTIVE
            CREATED  -> ARCHIVED
            ACTIVE   -> ARCHIVED
            ACTIVE   -> DELETED
            ARCHIVED -> DELETED

        Terminal states cannot transition to themselves or
        to another state.
        """
        transitions: dict[AtlasLifecycle, set[AtlasLifecycle]] = {
            AtlasLifecycle.CREATED: {
                AtlasLifecycle.ACTIVE,
                AtlasLifecycle.ARCHIVED,
            },
            AtlasLifecycle.ACTIVE: {
                AtlasLifecycle.ARCHIVED,
                AtlasLifecycle.DELETED,
            },
            AtlasLifecycle.ARCHIVED: {
                AtlasLifecycle.DELETED,
            },
            AtlasLifecycle.DELETED: set(),
        }

        return target in transitions[self]

    def __str__(self) -> str:
        return self.value
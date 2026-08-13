"""
Atlas Application Views

ENG-039 — Atlas UI Architecture

Presentation boundaries for future UI views.
"""

from __future__ import annotations


class Atlas3DView:
    """
    Future 3D presentation boundary.

    This object intentionally owns no AtlasProject, Resource Registry,
    Resource Graph, or canonical engineering state.
    """

    __slots__ = ()

    def __init__(self) -> None:
        pass
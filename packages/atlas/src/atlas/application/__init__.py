"""
Atlas Application

ENG-039 — Atlas UI Architecture
ENG-040 — Atlas UI Application Shell
"""

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.application.panel import AtlasPanel
from atlas.application.panel_registry import AtlasPanelRegistry
from atlas.application.presentation import (
    AtlasResourcePresentation,
)
from atlas.application.queries import AtlasQuery
from atlas.application.selection import AtlasResourceSelection
from atlas.application.ui_state import AtlasUIState
from atlas.application.view import AtlasView
from atlas.application.view_registry import AtlasViewRegistry
from atlas.application.views import Atlas3DView
from atlas.application.workspace import AtlasWorkspace

__all__ = [
    "AtlasApplication",
    "AtlasCommand",
    "AtlasQuery",
    "AtlasResourceSelection",
    "AtlasUIState",
    "AtlasResourcePresentation",
    "Atlas3DView",
    "AtlasWorkspace",
    "AtlasPanel",
    "AtlasPanelRegistry",
    "AtlasView",
    "AtlasViewRegistry",
]
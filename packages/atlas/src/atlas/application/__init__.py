"""
Atlas Application

ENG-039 — Atlas UI Architecture
ENG-040 — Atlas UI Application Shell
ENG-041 — Atlas Dashboard
ENG-042 — Atlas Explorer
ENG-043 — Atlas Inspector
ENG-044 — Atlas Toolbar
ENG-046 — Atlas Scene
ENG-047 — Atlas Camera
ENG-048 — Atlas Navigation
"""

from atlas.application.application import AtlasApplication
from atlas.application.camera import AtlasCamera
from atlas.application.commands import AtlasCommand
from atlas.application.dashboard import (
    AtlasAgentSummary,
    AtlasClassificationSummary,
    AtlasDashboard,
    AtlasDashboardPresentation,
    AtlasDashboardSelectionTarget,
    AtlasRelationshipSummary,
    AtlasResourceSummary,
    AtlasValidationSummary,
)
from atlas.application.explorer import (
    AtlasExplorer,
    AtlasExplorerNode,
    AtlasExplorerPresentation,
)
from atlas.application.inspector import (
    AtlasInspector,
    AtlasInspectorClassification,
    AtlasInspectorPresentation,
    AtlasInspectorRelationship,
)
from atlas.application.navigation import AtlasNavigation
from atlas.application.panel import AtlasPanel
from atlas.application.panel_registry import AtlasPanelRegistry
from atlas.application.presentation import AtlasResourcePresentation
from atlas.application.queries import AtlasQuery
from atlas.application.scene import AtlasScene, AtlasSceneNode
from atlas.application.selection import AtlasResourceSelection
from atlas.application.toolbar import (
    AtlasToolbar,
    AtlasToolbarItem,
    AtlasToolbarPresentation,
)
from atlas.application.ui_state import AtlasUIState
from atlas.application.view import AtlasView
from atlas.application.view_registry import AtlasViewRegistry
from atlas.application.views import Atlas3DView
from atlas.application.workspace import AtlasWorkspace


__all__ = [
    # ENG-039 — Application Boundary
    "AtlasApplication",
    "AtlasCommand",
    "AtlasQuery",
    "AtlasResourceSelection",
    "AtlasUIState",
    "AtlasResourcePresentation",
    "Atlas3DView",

    # ENG-040 — UI Application Shell
    "AtlasWorkspace",
    "AtlasPanel",
    "AtlasPanelRegistry",
    "AtlasView",
    "AtlasViewRegistry",

    # ENG-046 — Scene
    "AtlasScene",
    "AtlasSceneNode",

    # ENG-047 — Camera
    "AtlasCamera",

    # ENG-048 — Navigation
    "AtlasNavigation",

    # ENG-041 — Dashboard
    "AtlasDashboard",
    "AtlasDashboardPresentation",
    "AtlasDashboardSelectionTarget",
    "AtlasResourceSummary",
    "AtlasClassificationSummary",
    "AtlasRelationshipSummary",
    "AtlasValidationSummary",
    "AtlasAgentSummary",

    # ENG-042 — Explorer
    "AtlasExplorer",
    "AtlasExplorerNode",
    "AtlasExplorerPresentation",

    # ENG-043 — Inspector
    "AtlasInspector",
    "AtlasInspectorPresentation",
    "AtlasInspectorRelationship",
    "AtlasInspectorClassification",

    # ENG-044 — Toolbar
    "AtlasToolbar",
    "AtlasToolbarItem",
    "AtlasToolbarPresentation",
]
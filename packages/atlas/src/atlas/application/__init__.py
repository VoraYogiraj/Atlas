"""
Atlas Application

ENG-039 — Atlas UI Architecture
ENG-040 — Atlas UI Application Shell
ENG-041 — Atlas Dashboard
ENG-042 — Atlas Explorer
ENG-043 — Atlas Inspector
ENG-044 — Atlas Toolbar
ENG-045 — Atlas Panels
ENG-046 — Atlas Scene
ENG-047 — Atlas Camera
ENG-048 — Atlas Navigation
ENG-049 — Atlas Selection
ENG-050 — Atlas Gizmo
ENG-051 — Atlas Basic Editing
ENG-052 — Atlas Resource Create
ENG-053 — Atlas Resource Move
"""

from atlas.application.application import AtlasApplication
from atlas.application.basic_editing import AtlasBasicEditing
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

from atlas.application.gizmo import AtlasGizmo

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

from atlas.application.scene import (
    AtlasScene,
    AtlasSceneNode,
)

from atlas.application.selection import (
    AtlasResourceSelection,
    AtlasSelectionState,
)

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
    # Core application boundary
    "AtlasApplication",
    "AtlasCommand",
    "AtlasQuery",

    # Resource editing
    "AtlasBasicEditing",

    # Selection / UI state
    "AtlasResourceSelection",
    "AtlasSelectionState",
    "AtlasUIState",

    # Presentation
    "AtlasResourcePresentation",

    # Views / workspace
    "Atlas3DView",
    "AtlasWorkspace",
    "AtlasView",
    "AtlasViewRegistry",

    # Panels
    "AtlasPanel",
    "AtlasPanelRegistry",

    # Scene / 3D workspace
    "AtlasScene",
    "AtlasSceneNode",
    "AtlasCamera",
    "AtlasNavigation",
    "AtlasGizmo",

    # Dashboard
    "AtlasDashboard",
    "AtlasDashboardPresentation",
    "AtlasDashboardSelectionTarget",
    "AtlasResourceSummary",
    "AtlasClassificationSummary",
    "AtlasRelationshipSummary",
    "AtlasValidationSummary",
    "AtlasAgentSummary",

    # Explorer
    "AtlasExplorer",
    "AtlasExplorerNode",
    "AtlasExplorerPresentation",

    # Inspector
    "AtlasInspector",
    "AtlasInspectorRelationship",
    "AtlasInspectorClassification",
    "AtlasInspectorPresentation",

    # Toolbar
    "AtlasToolbar",
    "AtlasToolbarItem",
    "AtlasToolbarPresentation",
]
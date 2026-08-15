"""
Atlas UI Application Workspace

ENG-040 — Atlas UI Application Shell
ENG-045 — Atlas Panels
ENG-046 — Atlas Scene
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.application.panel import AtlasPanel
from atlas.application.panel_registry import AtlasPanelRegistry
from atlas.application.queries import AtlasQuery
from atlas.application.scene import AtlasScene
from atlas.application.view import AtlasView
from atlas.application.view_registry import AtlasViewRegistry
from atlas.core.aid import AtlasID


class AtlasWorkspace:
    """
    Structural UI workspace above the ENG-039 application boundary.

    The Workspace owns only presentation/application state.
    It does not own Atlas Resource registries, graphs, agents,
    persistence, or exchange state.
    """

    def __init__(
        self,
        *,
        application: AtlasApplication | None = None,
    ) -> None:
        if application is not None and not isinstance(
            application,
            AtlasApplication,
        ):
            raise TypeError(
                "application must be an AtlasApplication or None"
            )

        self._workspace_id: UUID = uuid4()
        self._application = application

        self._panel_registry = AtlasPanelRegistry()
        self._view_registry = AtlasViewRegistry()

        self._active_panel_id: str | None = None
        self._active_view_id: str | None = None
        self._selected_resource_id: AtlasID | None = None
        self._scene: AtlasScene | None = None

        self._lifecycle = "created"

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def workspace_id(self) -> UUID:
        """Return the stable UI workspace identity."""
        return self._workspace_id

    @property
    def application(self) -> AtlasApplication | None:
        """Return the ENG-039 application boundary, when configured."""
        return self._application

    @property
    def panel_registry(self) -> AtlasPanelRegistry:
        """Return the UI Panel Registry."""
        return self._panel_registry

    @property
    def view_registry(self) -> AtlasViewRegistry:
        """Return the UI View Registry."""
        return self._view_registry

    @property
    def active_panel_id(self) -> str | None:
        """Return the active panel identity."""
        return self._active_panel_id

    @property
    def active_view_id(self) -> str | None:
        """Return the active view identity."""
        return self._active_view_id

    @property
    def selected_resource_id(self) -> AtlasID | None:
        """Return the selected Resource identity."""
        return self._selected_resource_id

    @property
    def scene(self) -> AtlasScene | None:
        """Return the hosted 3D Workspace Scene, when configured."""
        return self._scene

    @property
    def lifecycle(self) -> str:
        """Return the current workspace lifecycle state."""
        return self._lifecycle

    # ------------------------------------------------------------------
    # Panel operations
    # ------------------------------------------------------------------

    @property
    def panels(self) -> tuple[AtlasPanel, ...]:
        """
        Return registered Panels in deterministic presentation order.
        """
        panels = tuple(
            self._panel_registry.get(panel_id)
            for panel_id in self._panel_registry.ids()
        )

        return tuple(
            sorted(
                panels,
                key=lambda panel: (
                    panel.order,
                    panel.panel_id,
                ),
            )
        )

    def register_panel(
        self,
        panel: AtlasPanel,
    ) -> None:
        """Register a presentation Panel."""
        self._panel_registry.register(
            panel,
        )

    def set_active_panel(
        self,
        panel_id: str | None,
    ) -> None:
        """
        Activate a registered Panel or clear the active Panel.

        Active state is kept synchronized with Panel presentation state.
        """
        if panel_id is None:
            if self._active_panel_id is not None:
                previous = self._panel_registry.get(
                    self._active_panel_id,
                )
                previous.set_active(False)

            self._active_panel_id = None
            return

        panel = self._panel_registry.get(
            panel_id,
        )

        if self._active_panel_id == panel_id:
            panel.set_active(True)
            return

        if self._active_panel_id is not None:
            previous = self._panel_registry.get(
                self._active_panel_id,
            )
            previous.set_active(False)

        panel.set_active(True)
        self._active_panel_id = panel_id

    # ------------------------------------------------------------------
    # View operations
    # ------------------------------------------------------------------

    def register_view(
        self,
        view: AtlasView,
    ) -> None:
        """Register a main workspace View."""
        self._view_registry.register(
            view,
        )

    def set_active_view(
        self,
        view_id: str | None,
    ) -> None:
        """Activate a registered View or clear the active View."""
        if view_id is None:
            self._active_view_id = None
            return

        self._view_registry.get(
            view_id,
        )
        self._active_view_id = view_id

    # ------------------------------------------------------------------
    # Scene hosting
    # ------------------------------------------------------------------

    def set_scene(
        self,
        scene: AtlasScene | None,
    ) -> None:
        """Host a framework-independent ENG-046 Scene or clear it."""
        if scene is not None and not isinstance(
            scene,
            AtlasScene,
        ):
            raise TypeError(
                "scene must be an AtlasScene or None"
            )

        self._scene = scene

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def set_selected_resource(
        self,
        resource_id: AtlasID | None,
    ) -> None:
        """
        Set selection using canonical Atlas identity.

        The Workspace never stores the Resource object itself.
        """
        if resource_id is not None and not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID or None"
            )

        self._selected_resource_id = resource_id

    # ------------------------------------------------------------------
    # Application boundary
    # ------------------------------------------------------------------

    def execute(
        self,
        command: AtlasCommand,
    ) -> Any:
        """
        Dispatch a Command through ENG-039.
        """
        if self._application is None:
            raise RuntimeError(
                "Workspace has no AtlasApplication"
            )

        return self._application.execute(
            command,
        )

    def query(
        self,
        query: AtlasQuery,
    ) -> Any:
        """
        Dispatch a Query through ENG-039.
        """
        if self._application is None:
            raise RuntimeError(
                "Workspace has no AtlasApplication"
            )

        return self._application.query(
            query,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Initialize the Workspace."""
        if self._lifecycle != "created":
            raise RuntimeError(
                f"Cannot initialize Workspace from "
                f"state '{self._lifecycle}'"
            )

        self._lifecycle = "initialized"

    def activate(self) -> None:
        """Activate an initialized Workspace."""
        if self._lifecycle != "initialized":
            raise RuntimeError(
                "Workspace must be initialized before activation"
            )

        self._lifecycle = "active"

    def deactivate(self) -> None:
        """Deactivate an active Workspace."""
        if self._lifecycle != "active":
            raise RuntimeError(
                f"Cannot deactivate Workspace from "
                f"state '{self._lifecycle}'"
            )

        self._lifecycle = "inactive"

    def dispose(self) -> None:
        """
        Dispose UI-owned state.

        This does not touch the Atlas Project.
        """
        if self._lifecycle == "disposed":
            return

        if self._lifecycle not in {
            "inactive",
            "initialized",
            "created",
        }:
            raise RuntimeError(
                f"Cannot dispose Workspace from "
                f"state '{self._lifecycle}'"
            )

        for panel_id in self._panel_registry.ids():
            panel = self._panel_registry.get(
                panel_id,
            )
            panel.set_active(False)

        self._active_panel_id = None
        self._active_view_id = None
        self._selected_resource_id = None
        self._scene = None

        self._lifecycle = "disposed"
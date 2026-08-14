"""
Atlas UI Panel

ENG-040 — Atlas UI Application Shell
ENG-045 — Atlas Panels
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AtlasPanel:
    """
    Presentation panel hosted by an AtlasWorkspace.

    Panels are UI/application objects. They do not own canonical
    Atlas engineering state.
    """

    panel_id: str
    name: str
    description: str = ""
    visible: bool = True
    enabled: bool = True
    active: bool = False
    order: int = 0
    lifecycle: str = "created"
    is_loading: bool = False
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.panel_id, str):
            raise TypeError("panel_id must be a string")

        if not self.panel_id.strip():
            raise ValueError("panel_id cannot be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not isinstance(self.visible, bool):
            raise TypeError("visible must be a boolean")

        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a boolean")

        if not isinstance(self.active, bool):
            raise TypeError("active must be a boolean")

        if not isinstance(self.order, int):
            raise TypeError("order must be an integer")

        if not isinstance(self.lifecycle, str):
            raise TypeError("lifecycle must be a string")

        if not self.lifecycle.strip():
            raise ValueError("lifecycle cannot be empty")

        if not isinstance(self.is_loading, bool):
            raise TypeError("is_loading must be a boolean")

        if self.error is not None and not isinstance(
            self.error,
            str,
        ):
            raise TypeError("error must be a string or None")

        if (
            isinstance(self.error, str)
            and not self.error.strip()
        ):
            raise ValueError("error cannot be empty")

    # ------------------------------------------------------------------
    # Visibility
    # ------------------------------------------------------------------

    def set_visible(
        self,
        visible: bool,
    ) -> None:
        """Set presentation visibility."""
        if not isinstance(
            visible,
            bool,
        ):
            raise TypeError(
                "visible must be a boolean"
            )

        self.visible = visible

    # ------------------------------------------------------------------
    # Enabled state
    # ------------------------------------------------------------------

    def set_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Set presentation enabled state."""
        if not isinstance(
            enabled,
            bool,
        ):
            raise TypeError(
                "enabled must be a boolean"
            )

        self.enabled = enabled

    # ------------------------------------------------------------------
    # Active state
    # ------------------------------------------------------------------

    def set_active(
        self,
        active: bool,
    ) -> None:
        """Set transient active state."""
        if not isinstance(
            active,
            bool,
        ):
            raise TypeError(
                "active must be a boolean"
            )

        self.active = active

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------

    def set_order(
        self,
        order: int,
    ) -> None:
        """Set deterministic presentation order."""
        if not isinstance(
            order,
            int,
        ):
            raise TypeError(
                "order must be an integer"
            )

        self.order = order

    # ------------------------------------------------------------------
    # Loading state
    # ------------------------------------------------------------------

    def set_loading(
        self,
        loading: bool,
    ) -> None:
        """Set transient presentation loading state."""
        if not isinstance(
            loading,
            bool,
        ):
            raise TypeError(
                "loading must be a boolean"
            )

        self.is_loading = loading

    # ------------------------------------------------------------------
    # Error state
    # ------------------------------------------------------------------

    def set_error(
        self,
        message: str | None,
    ) -> None:
        """Set or clear transient presentation error state."""
        if message is not None and not isinstance(
            message,
            str,
        ):
            raise TypeError(
                "message must be a string or None"
            )

        if (
            isinstance(message, str)
            and not message.strip()
        ):
            raise ValueError(
                "message cannot be empty"
            )

        self.error = message
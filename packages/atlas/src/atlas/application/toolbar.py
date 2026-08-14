"""
Atlas Toolbar

ENG-044 — Atlas Toolbar

Framework-independent command presentation surface for the Atlas UI.

The Toolbar presents existing AtlasCommand instances and delegates command
execution through AtlasApplication. It does not implement a second command
engine and does not own engineering state.
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.application.application import AtlasApplication
from atlas.application.commands import AtlasCommand
from atlas.core.aid import AtlasID


# ---------------------------------------------------------------------------
# Toolbar Item
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasToolbarItem:
    """
    Presentation representation of an Atlas application command.

    The underlying AtlasCommand remains the canonical command identity.
    """

    command: AtlasCommand
    label: str
    group: str = ""
    order: int = 0
    enabled: bool = True
    visible: bool = True
    tooltip: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.command,
            AtlasCommand,
        ):
            raise TypeError(
                "command must be an AtlasCommand"
            )

        if not isinstance(
            self.label,
            str,
        ):
            raise TypeError(
                "label must be a string"
            )

        if not self.label.strip():
            raise ValueError(
                "label cannot be empty"
            )

        if not isinstance(
            self.group,
            str,
        ):
            raise TypeError(
                "group must be a string"
            )

        if not isinstance(
            self.order,
            int,
        ):
            raise TypeError(
                "order must be an integer"
            )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise TypeError(
                "enabled must be a boolean"
            )

        if not isinstance(
            self.visible,
            bool,
        ):
            raise TypeError(
                "visible must be a boolean"
            )

        if self.tooltip is not None:
            if not isinstance(
                self.tooltip,
                str,
            ):
                raise TypeError(
                    "tooltip must be a string or None"
                )

    @property
    def command_name(self) -> str:
        """Return the underlying application command name."""
        return self.command.name


# ---------------------------------------------------------------------------
# Toolbar Presentation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasToolbarPresentation:
    """
    Derived presentation state for the Toolbar.
    """

    items: tuple[AtlasToolbarItem, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.items,
            tuple,
        ):
            raise TypeError(
                "items must be a tuple"
            )

        for item in self.items:
            if not isinstance(
                item,
                AtlasToolbarItem,
            ):
                raise TypeError(
                    "items must contain AtlasToolbarItem values"
                )


# ---------------------------------------------------------------------------
# Toolbar
# ---------------------------------------------------------------------------


class AtlasToolbar:
    """
    Atlas command presentation surface.

    ENG-044 intentionally keeps command semantics outside the Toolbar.
    """

    toolbar_id = "toolbar"

    def __init__(
        self,
        *,
        application: AtlasApplication,
    ) -> None:
        if not isinstance(
            application,
            AtlasApplication,
        ):
            raise TypeError(
                "application must be an AtlasApplication"
            )

        self._application = application

        self._items: list[AtlasToolbarItem] = []

        self._selected_resource_id: AtlasID | None = None

        self._is_loading = False
        self._error: str | None = None

    # ------------------------------------------------------------------
    # Application Boundary
    # ------------------------------------------------------------------

    @property
    def application(self) -> AtlasApplication:
        """
        Return the canonical AtlasApplication boundary.
        """
        return self._application

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    @property
    def selected_resource_id(self) -> AtlasID | None:
        """
        Return the currently selected Resource identity.
        """
        return self._selected_resource_id

    def set_selection(
        self,
        resource_id: AtlasID | None,
    ) -> None:
        """
        Update transient Toolbar selection context.
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
    # Command Registration
    # ------------------------------------------------------------------

    def register_command(
        self,
        command: AtlasCommand,
        *,
        label: str,
        group: str = "",
        order: int = 0,
        enabled: bool = True,
        visible: bool = True,
        tooltip: str | None = None,
    ) -> AtlasToolbarItem:
        """
        Register an existing AtlasCommand as a Toolbar presentation item.

        The Toolbar stores presentation information only. The command itself
        remains owned by the application command boundary.
        """

        item = AtlasToolbarItem(
            command=command,
            label=label,
            group=group,
            order=order,
            enabled=enabled,
            visible=visible,
            tooltip=tooltip,
        )

        self._items.append(
            item,
        )

        return item

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    def refresh(self) -> AtlasToolbarPresentation:
        """
        Produce a deterministic Toolbar presentation.

        The Toolbar does not mutate Atlas engineering state.
        """

        ordered_items = tuple(
            sorted(
                self._items,
                key=lambda item: (
                    item.order,
                    item.group,
                    item.command.name,
                    item.label,
                ),
            )
        )

        return AtlasToolbarPresentation(
            items=ordered_items,
        )

    # ------------------------------------------------------------------
    # Command Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        command: AtlasCommand,
    ) -> object:
        """
        Delegate an AtlasCommand to AtlasApplication.

        The Toolbar does not implement command semantics.
        """

        if not isinstance(
            command,
            AtlasCommand,
        ):
            raise TypeError(
                "command must be an AtlasCommand"
            )

        return self._application.execute(
            command,
        )

    # ------------------------------------------------------------------
    # Loading State
    # ------------------------------------------------------------------

    @property
    def is_loading(self) -> bool:
        """Return whether the Toolbar is currently loading."""
        return self._is_loading

    def set_loading(
        self,
        loading: bool,
    ) -> None:
        """Set transient Toolbar loading state."""

        if not isinstance(
            loading,
            bool,
        ):
            raise TypeError(
                "loading must be a boolean"
            )

        self._is_loading = loading

    # ------------------------------------------------------------------
    # Error State
    # ------------------------------------------------------------------

    @property
    def error(self) -> str | None:
        """Return the current Toolbar error state."""
        return self._error

    def set_error(
        self,
        message: str | None,
    ) -> None:
        """Set transient Toolbar error state."""

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

        self._error = message
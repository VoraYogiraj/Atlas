"""
Atlas Gizmo

ENG-050 — Atlas 3D Workspace Gizmo

The Gizmo is renderer-independent manipulation state.

It stores:
- manipulation mode,
- constrained axis,
- target scene-node identity,
- manipulation lifecycle.

It does not mutate SceneNodes, Resources, Relationships, or Projects.
"""

from __future__ import annotations


class AtlasGizmo:
    """
    Renderer-independent manipulation state for the Atlas 3D workspace.

    The Gizmo references a scene node only by its viewport identity
    (`node_id`). It does not own or resolve an AtlasSceneNode.

    ENG-050 deliberately does not perform:
    - scene-node transformation
    - selection
    - picking
    - raycasting
    - highlighting
    - rendering
    - input handling
    - engineering-model mutation
    """

    _VALID_MODES = frozenset({"translate", "rotate", "scale"})
    _VALID_AXES = frozenset({"x", "y", "z"})

    __slots__ = (
        "_mode",
        "_active_axis",
        "_node_id",
        "_is_active",
    )

    def __init__(self) -> None:
        self._mode = "translate"
        self._active_axis: str | None = None
        self._node_id: str | None = None
        self._is_active = False

    @property
    def mode(self) -> str:
        """Return the current manipulation mode."""
        return self._mode

    @property
    def active_axis(self) -> str | None:
        """Return the current axis constraint."""
        return self._active_axis

    @property
    def node_id(self) -> str | None:
        """Return the currently attached scene-node identity."""
        return self._node_id

    @property
    def is_active(self) -> bool:
        """Return whether a manipulation session is active."""
        return self._is_active

    def set_mode(self, *, mode: str) -> None:
        """
        Set the manipulation mode.

        Valid modes:
        - translate
        - rotate
        - scale

        Changing the mode does not activate the Gizmo.
        """
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")

        if mode not in self._VALID_MODES:
            raise ValueError(
                "mode must be one of: translate, rotate, scale"
            )

        self._mode = mode

    def set_axis(self, *, axis: str | None) -> None:
        """
        Set the manipulation axis constraint.

        Valid values:
        - None
        - x
        - y
        - z
        """
        if axis is not None and not isinstance(axis, str):
            raise TypeError("axis must be a string or None")

        if axis is not None and axis not in self._VALID_AXES:
            raise ValueError("axis must be one of: x, y, z, or None")

        self._active_axis = axis

    def attach(self, *, node_id: str) -> None:
        """
        Attach the Gizmo to a scene-node identity.

        The Gizmo stores only the node identifier. It does not resolve
        or own the corresponding AtlasSceneNode.
        """
        if not isinstance(node_id, str):
            raise TypeError("node_id must be a string")

        if not node_id.strip():
            raise ValueError("node_id must not be empty or whitespace")

        if self._is_active:
            raise RuntimeError("cannot attach while gizmo is active")

        if self._node_id is not None:
            raise RuntimeError(
                "gizmo is already attached; detach before attaching another node"
            )

        self._node_id = node_id

    def detach(self) -> None:
        """
        Detach the current scene-node identity.

        Detaching an already detached inactive Gizmo is idempotent.
        """
        if self._is_active:
            raise RuntimeError("cannot detach while gizmo is active")

        self._node_id = None

    def begin(self) -> None:
        """
        Begin a manipulation session.

        A target node must be attached and the Gizmo must not already
        be active.
        """
        if self._node_id is None:
            raise RuntimeError("cannot begin without an attached node")

        if self._is_active:
            raise RuntimeError("gizmo is already active")

        self._is_active = True

    def end(self) -> None:
        """
        End the active manipulation session.
        """
        if not self._is_active:
            raise RuntimeError("cannot end an inactive gizmo")

        self._is_active = False

    def cancel(self) -> None:
        """
        Cancel the active manipulation session.

        ENG-050 does not mutate SceneNode transformations, so cancellation
        only ends the transient manipulation state.
        """
        if not self._is_active:
            raise RuntimeError("cannot cancel an inactive gizmo")

        self._is_active = False


__all__ = [
    "AtlasGizmo",
]
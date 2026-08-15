"""
Atlas Scene

ENG-046 — Atlas Scene

Defines framework-independent presentation state for the 3D Workspace. A
Scene references Atlas Resources solely by their canonical AtlasID; it never
owns Resources, engineering relationships, classifications, or registries.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias

from atlas.core.aid import AtlasID


Vector3: TypeAlias = tuple[float, float, float]


def _require_non_empty_string(
    value: object,
    *,
    name: str,
) -> str:
    """Validate an explicit machine- or human-readable identity."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")

    if not value:
        raise ValueError(f"{name} cannot be empty")

    return value


def _vector3(
    value: object,
    *,
    name: str,
) -> Vector3:
    """Return a numeric three-component presentation vector."""
    if isinstance(value, str) or not isinstance(
        value,
        Iterable,
    ):
        raise TypeError(
            f"{name} must be a three-component vector"
        )

    components = tuple(value)

    if len(components) != 3:
        raise ValueError(
            f"{name} must contain exactly three components"
        )

    if any(
        not isinstance(component, (int, float))
        or isinstance(component, bool)
        for component in components
    ):
        raise TypeError(
            f"{name} components must be numeric"
        )

    return (
        float(components[0]),
        float(components[1]),
        float(components[2]),
    )


class AtlasSceneNode:
    """
    A spatial presentation node for exactly one Atlas Resource.

    ``node_id`` identifies the presentation node. ``resource_id`` retains
    the reference to canonical engineering identity without retaining or
    duplicating the Resource itself.
    """

    def __init__(
        self,
        *,
        node_id: str,
        resource_id: AtlasID,
    ) -> None:
        self._node_id = _require_non_empty_string(
            node_id,
            name="node_id",
        )

        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        self._resource_id = resource_id
        self._parent_id: str | None = None

        self._position: Vector3 = (
            0.0,
            0.0,
            0.0,
        )
        self._rotation: Vector3 = (
            0.0,
            0.0,
            0.0,
        )
        self._scale: Vector3 = (
            1.0,
            1.0,
            1.0,
        )
        self._visible = True

    # ------------------------------------------------------------------
    # Identity and hierarchy
    # ------------------------------------------------------------------

    @property
    def node_id(self) -> str:
        """Return the stable presentation identity for this node."""
        return self._node_id

    @property
    def resource_id(self) -> AtlasID:
        """Return the canonical Atlas Resource identity being presented."""
        return self._resource_id

    @property
    def parent_id(self) -> str | None:
        """Return the parent node identity, or None for a root node."""
        return self._parent_id

    def _set_parent(
        self,
        parent_id: str | None,
    ) -> None:
        """Set hierarchy ownership after validation by AtlasScene."""
        self._parent_id = parent_id

    # ------------------------------------------------------------------
    # Spatial presentation
    # ------------------------------------------------------------------

    @property
    def position(self) -> Vector3:
        """Return the local position in Scene coordinates."""
        return self._position

    @property
    def rotation(self) -> Vector3:
        """Return the local rotation in Scene coordinates."""
        return self._rotation

    @property
    def scale(self) -> Vector3:
        """Return the local scale in Scene coordinates."""
        return self._scale

    def set_position(
        self,
        position: Vector3,
    ) -> None:
        """Set the local position."""
        self._position = _vector3(
            position,
            name="position",
        )

    def set_rotation(
        self,
        rotation: Vector3,
    ) -> None:
        """Set the local rotation."""
        self._rotation = _vector3(
            rotation,
            name="rotation",
        )

    def set_scale(
        self,
        scale: Vector3,
    ) -> None:
        """Set the local scale."""
        self._scale = _vector3(
            scale,
            name="scale",
        )

    @property
    def visible(self) -> bool:
        """Return whether this node is visible in the presentation."""
        return self._visible

    def set_visible(
        self,
        visible: bool,
    ) -> None:
        """Set transient node visibility."""
        if not isinstance(visible, bool):
            raise TypeError("visible must be a bool")

        self._visible = visible


class AtlasScene:
    """
    A framework-independent spatial presentation of Atlas Resources.

    The Scene owns nodes and their visual hierarchy only. Engineering truth
    remains in AtlasProject and the Resource/Relationship/Classification
    model beneath the ENG-039 application boundary.
    """

    def __init__(
        self,
        *,
        scene_id: str,
        name: str,
    ) -> None:
        self._scene_id = _require_non_empty_string(
            scene_id,
            name="scene_id",
        )
        self._name = _require_non_empty_string(
            name,
            name="name",
        )

        self._nodes: dict[str, AtlasSceneNode] = {}

        self._selected_node_id: str | None = None
        self._visible = True
        self._is_loading = False
        self._error: str | None = None
        self._lifecycle = "created"

    # ------------------------------------------------------------------
    # Identity and state
    # ------------------------------------------------------------------

    @property
    def scene_id(self) -> str:
        """Return the stable presentation identity for this Scene."""
        return self._scene_id

    @property
    def name(self) -> str:
        """Return the human-readable Scene name."""
        return self._name

    @property
    def lifecycle(self) -> str:
        """Return the Scene presentation lifecycle state."""
        return self._lifecycle

    @property
    def visible(self) -> bool:
        """Return whether the Scene is visible."""
        return self._visible

    def set_visible(
        self,
        visible: bool,
    ) -> None:
        """Set transient Scene visibility."""
        if not isinstance(visible, bool):
            raise TypeError("visible must be a bool")

        self._visible = visible

    @property
    def is_loading(self) -> bool:
        """Return the transient Scene loading state."""
        return self._is_loading

    def set_loading(
        self,
        is_loading: bool,
    ) -> None:
        """Set the transient Scene loading state."""
        if not isinstance(is_loading, bool):
            raise TypeError(
                "is_loading must be a bool"
            )

        self._is_loading = is_loading

    @property
    def error(self) -> str | None:
        """Return the transient Scene presentation error, if any."""
        return self._error

    def set_error(
        self,
        error: str | None,
    ) -> None:
        """Set or clear a transient Scene presentation error."""
        if error is not None and not isinstance(
            error,
            str,
        ):
            raise TypeError(
                "error must be a string or None"
            )

        self._error = error

    # ------------------------------------------------------------------
    # Node registration and lookup
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> tuple[AtlasSceneNode, ...]:
        """Return all Scene nodes in deterministic identity order."""
        return tuple(
            self._nodes[node_id]
            for node_id in sorted(self._nodes)
        )

    @property
    def is_empty(self) -> bool:
        """Return True if this Scene contains no nodes."""
        return not self._nodes

    def add_node(
        self,
        node: AtlasSceneNode,
    ) -> None:
        """Register a node."""
        if not isinstance(node, AtlasSceneNode):
            raise TypeError(
                "node must be an AtlasSceneNode"
            )

        if node.node_id in self._nodes:
            raise ValueError(
                f"Scene node already exists: {node.node_id}"
            )

        if node.parent_id is not None:
            raise ValueError(
                "A node must be unparented when added to a Scene"
            )

        self._nodes[node.node_id] = node

    def get_node(
        self,
        node_id: str,
    ) -> AtlasSceneNode:
        """Return a node by presentation identity."""
        _require_non_empty_string(
            node_id,
            name="node_id",
        )
        return self._nodes[node_id]

    def remove_node(
        self,
        node_id: str,
    ) -> AtlasSceneNode:
        """Remove an unparented leaf node and return it."""
        node = self.get_node(node_id)

        if self.children_of(node_id):
            raise ValueError(
                "Cannot remove a Scene node with children"
            )

        del self._nodes[node_id]

        if self._selected_node_id == node_id:
            self._selected_node_id = None

        return node

    # ------------------------------------------------------------------
    # Hierarchy
    # ------------------------------------------------------------------

    @property
    def root_nodes(self) -> tuple[AtlasSceneNode, ...]:
        """Return root nodes in deterministic identity order."""
        return tuple(
            node
            for node in self.nodes
            if node.parent_id is None
        )

    def children_of(
        self,
        node_id: str,
    ) -> tuple[AtlasSceneNode, ...]:
        """Return direct children of a registered node in stable order."""
        self.get_node(node_id)

        return tuple(
            node
            for node in self.nodes
            if node.parent_id == node_id
        )

    def set_parent(
        self,
        node_id: str,
        parent_id: str | None,
    ) -> None:
        """Set or clear a node parent after validating the resulting tree."""
        node = self.get_node(node_id)

        if parent_id is None:
            node._set_parent(None)
            return

        _require_non_empty_string(
            parent_id,
            name="parent_id",
        )
        self.get_node(parent_id)

        if node_id == parent_id:
            raise ValueError(
                "A Scene node cannot be its own parent"
            )

        ancestor_id: str | None = parent_id

        while ancestor_id is not None:
            if ancestor_id == node_id:
                raise ValueError(
                    "Scene node hierarchy cannot contain cycles"
                )

            ancestor_id = self._nodes[
                ancestor_id
            ].parent_id

        node._set_parent(parent_id)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    @property
    def selected_node_id(self) -> str | None:
        """Return the selected Scene node identity, if any."""
        return self._selected_node_id

    def set_selected_node(
        self,
        node_id: str | None,
    ) -> None:
        """Select a registered node or clear presentation selection."""
        if node_id is None:
            self._selected_node_id = None
            return

        self.get_node(node_id)
        self._selected_node_id = node_id

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Initialize the Scene presentation."""
        if self._lifecycle != "created":
            raise RuntimeError(
                "Cannot initialize Scene from "
                f"state '{self._lifecycle}'"
            )

        self._lifecycle = "initialized"

    def activate(self) -> None:
        """Activate an initialized Scene."""
        if self._lifecycle != "initialized":
            raise RuntimeError(
                "Scene must be initialized before activation"
            )

        self._lifecycle = "active"

    def deactivate(self) -> None:
        """Deactivate an active Scene."""
        if self._lifecycle != "active":
            raise RuntimeError(
                "Cannot deactivate Scene from "
                f"state '{self._lifecycle}'"
            )

        self._lifecycle = "inactive"

    def dispose(self) -> None:
        """Dispose only UI-owned Scene state."""
        if self._lifecycle == "disposed":
            return

        if self._lifecycle not in {
            "created",
            "initialized",
            "inactive",
        }:
            raise RuntimeError(
                "Cannot dispose Scene from "
                f"state '{self._lifecycle}'"
            )

        self._selected_node_id = None
        self._is_loading = False
        self._lifecycle = "disposed"
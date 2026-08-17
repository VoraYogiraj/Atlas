"""ENG-046 — Atlas Scene."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias

from atlas.core.aid import AtlasID

Vector3: TypeAlias = tuple[float, float, float]


def _text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty or whitespace")
    return value


def _vector(value: object, name: str) -> Vector3:
    if isinstance(value, str) or not isinstance(value, Iterable):
        raise TypeError(f"{name} must be a three-component vector")

    parts = tuple(value)

    if len(parts) != 3:
        raise ValueError(f"{name} must contain exactly three components")

    if any(
        not isinstance(item, (int, float)) or isinstance(item, bool)
        for item in parts
    ):
        raise TypeError(f"{name} components must be numeric")

    return (
        float(parts[0]),
        float(parts[1]),
        float(parts[2]),
    )


class AtlasSceneNode:
    """A spatial presentation object, separate from AtlasResource."""

    def __init__(
        self,
        *,
        node_id: str,
        name: str,
        resource_id: AtlasID | None = None,
        parent_node_id: str | None = None,
        position: Vector3 = (0.0, 0.0, 0.0),
        rotation: Vector3 = (0.0, 0.0, 0.0),
        scale: Vector3 = (1.0, 1.0, 1.0),
        visible: bool = True,
        order: int = 0,
    ) -> None:
        self._node_id = _text(node_id, "node_id")
        self._name = _text(name, "name")

        if resource_id is not None and not isinstance(resource_id, AtlasID):
            raise TypeError("resource_id must be an AtlasID or None")

        if parent_node_id is not None:
            self._parent_node_id = _text(
                parent_node_id,
                "parent_node_id",
            )
        else:
            self._parent_node_id = None

        if not isinstance(visible, bool):
            raise TypeError("visible must be a bool")

        if not isinstance(order, int) or isinstance(order, bool):
            raise TypeError("order must be an int")

        self._resource_id = resource_id

        self._position = _vector(
            position,
            "position",
        )

        self._rotation = _vector(
            rotation,
            "rotation",
        )

        self._scale = _vector(
            scale,
            "scale",
        )

        self._visible = visible
        self._order = order

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def resource_id(self) -> AtlasID | None:
        return self._resource_id

    @property
    def parent_node_id(self) -> str | None:
        return self._parent_node_id

    @property
    def position(self) -> Vector3:
        return self._position

    @property
    def rotation(self) -> Vector3:
        return self._rotation

    @property
    def scale(self) -> Vector3:
        return self._scale

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def order(self) -> int:
        return self._order

    def set_visible(self, visible: bool) -> None:
        if not isinstance(visible, bool):
            raise TypeError("visible must be a bool")

        self._visible = visible

    def set_order(self, order: int) -> None:
        if not isinstance(order, int) or isinstance(order, bool):
            raise TypeError("order must be an int")

        self._order = order

    def _set_parent(self, parent_node_id: str | None) -> None:
        self._parent_node_id = parent_node_id

    def _set_position(self, position: Vector3) -> None:
        """Internal transformation mutation used by ENG-051 Basic Editing."""
        self._position = _vector(position, "position")

    def _set_rotation(self, rotation: Vector3) -> None:
        """Internal transformation mutation used by ENG-051 Basic Editing."""
        self._rotation = _vector(rotation, "rotation")

    def _set_scale(self, scale: Vector3) -> None:
        """Internal transformation mutation used by ENG-051 Basic Editing."""
        self._scale = _vector(scale, "scale")


class AtlasScene:
    """Framework-independent 3D Workspace presentation state."""

    def __init__(
        self,
        *,
        scene_id: str,
        name: str,
    ) -> None:
        self._scene_id = _text(
            scene_id,
            "scene_id",
        )

        self._name = _text(
            name,
            "name",
        )

        self._nodes: dict[str, AtlasSceneNode] = {}
        self._selected_node_id: str | None = None
        self._is_loading = False
        self._error: str | None = None
        self._lifecycle = "created"

    @property
    def scene_id(self) -> str:
        return self._scene_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def lifecycle(self) -> str:
        return self._lifecycle

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def selected_node_id(self) -> str | None:
        return self._selected_node_id

    @property
    def nodes(self) -> tuple[AtlasSceneNode, ...]:
        return tuple(
            sorted(
                self._nodes.values(),
                key=lambda node: (
                    node.order,
                    node.node_id,
                ),
            )
        )

    @property
    def root_nodes(self) -> tuple[AtlasSceneNode, ...]:
        return tuple(
            node
            for node in self.nodes
            if node.parent_node_id is None
        )

    def add_node(self, node: AtlasSceneNode) -> None:
        if not isinstance(node, AtlasSceneNode):
            raise TypeError("node must be an AtlasSceneNode")

        if node.node_id in self._nodes:
            raise ValueError(
                f"Scene node already exists: {node.node_id}"
            )

        if (
            node.parent_node_id is not None
            and node.parent_node_id not in self._nodes
        ):
            raise ValueError(
                "A node parent must already exist in the Scene"
            )

        self._nodes[node.node_id] = node

    def get_node(self, node_id: str) -> AtlasSceneNode:
        _text(
            node_id,
            "node_id",
        )

        return self._nodes[node_id]

    def remove_node(self, node_id: str) -> AtlasSceneNode:
        node = self.get_node(node_id)

        if any(
            child.parent_node_id == node_id
            for child in self._nodes.values()
        ):
            raise ValueError(
                "Cannot remove a Scene node with children"
            )

        del self._nodes[node_id]

        if self._selected_node_id == node_id:
            self._selected_node_id = None

        return node

    def set_parent(
        self,
        node_id: str,
        parent_node_id: str | None,
    ) -> None:
        node = self.get_node(node_id)

        if parent_node_id is None:
            node._set_parent(None)
            return

        _text(
            parent_node_id,
            "parent_node_id",
        )

        self.get_node(parent_node_id)

        if node_id == parent_node_id:
            raise ValueError(
                "A Scene node cannot be its own parent"
            )

        ancestor_id: str | None = parent_node_id

        while ancestor_id is not None:
            if ancestor_id == node_id:
                raise ValueError(
                    "Scene node hierarchy cannot contain cycles"
                )

            ancestor_id = self._nodes[
                ancestor_id
            ].parent_node_id

        node._set_parent(parent_node_id)

    def set_selected_node(
        self,
        node_id: str | None,
    ) -> None:
        if node_id is None:
            self._selected_node_id = None
            return

        self.get_node(node_id)

        self._selected_node_id = node_id

    def set_loading(
        self,
        is_loading: bool,
    ) -> None:
        if not isinstance(is_loading, bool):
            raise TypeError("is_loading must be a bool")

        self._is_loading = is_loading

    def set_error(
        self,
        error: str | None,
    ) -> None:
        if error is not None:
            self._error = _text(
                error,
                "error",
            )
            return

        self._error = None

    def initialize(self) -> None:
        if self._lifecycle != "created":
            raise RuntimeError(
                f"Cannot initialize Scene from state "
                f"'{self._lifecycle}'"
            )

        self._lifecycle = "initialized"

    def activate(self) -> None:
        if self._lifecycle not in {
            "initialized",
            "inactive",
        }:
            raise RuntimeError(
                "Scene must be initialized or inactive "
                "before activation"
            )

        self._lifecycle = "active"

    def deactivate(self) -> None:
        if self._lifecycle != "active":
            raise RuntimeError(
                f"Cannot deactivate Scene from state "
                f"'{self._lifecycle}'"
            )

        self._lifecycle = "inactive"

    def dispose(self) -> None:
        if self._lifecycle == "disposed":
            return

        if self._lifecycle not in {
            "created",
            "initialized",
            "inactive",
        }:
            raise RuntimeError(
                f"Cannot dispose Scene from state "
                f"'{self._lifecycle}'"
            )

        self._selected_node_id = None
        self._is_loading = False
        self._lifecycle = "disposed"
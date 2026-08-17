"""
ENG-051 — Atlas Basic Editing.

Provides deterministic, renderer-independent transformation editing
for Atlas scene nodes.

Basic Editing owns transformation mutation of Scene presentation state.
It does not own selection, gizmos, rendering, engineering resources,
relationships, persistence, history, or undo/redo.
"""

from __future__ import annotations

from typing import Any

from atlas.application.scene import AtlasScene


class AtlasBasicEditing:
    """Deterministic transformation editing for Atlas scene nodes."""

    _VALID_AXES = frozenset({"x", "y", "z"})

    def __eq__(self, other: object) -> bool:
        """Basic editing has no mutable instance state."""
        return isinstance(other, AtlasBasicEditing)

    def __hash__(self) -> int:
        """Keep equality/hash behavior consistent."""
        return hash(type(self))

    @classmethod
    def _validate_axis(cls, axis: Any) -> str:
        """Validate and return a canonical axis."""
        if not isinstance(axis, str):
            raise TypeError("axis must be one of: 'x', 'y', 'z'")

        if axis not in cls._VALID_AXES:
            raise ValueError("axis must be one of: 'x', 'y', 'z'")

        return axis

    @staticmethod
    def _validate_value(value: Any) -> float:
        """Validate a transform value without coercing invalid input."""
        if isinstance(value, bool):
            raise TypeError("transform value must be numeric")

        if not isinstance(value, (int, float)):
            raise TypeError("transform value must be numeric")

        return float(value)

    @staticmethod
    def _get_node(scene: AtlasScene, node_id: str) -> Any:
        """Return the target node or raise KeyError."""
        return scene.get_node(node_id)

    @staticmethod
    def _replace_axis(
        vector: tuple[float, float, float],
        axis: str,
        value: float,
    ) -> tuple[float, float, float]:
        """Return a new vector with exactly one axis replaced."""
        index = {"x": 0, "y": 1, "z": 2}[axis]
        values = list(vector)
        values[index] = value
        return tuple(values)

    def translate(
        self,
        scene: AtlasScene,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        """Set one translation axis on a scene node."""
        axis = self._validate_axis(axis)
        value = self._validate_value(value)
        node = self._get_node(scene, node_id)

        new_position = self._replace_axis(
            node.position,
            axis,
            value,
        )

        node._set_position(new_position)

    def rotate(
        self,
        scene: AtlasScene,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        """Set one rotation axis on a scene node."""
        axis = self._validate_axis(axis)
        value = self._validate_value(value)
        node = self._get_node(scene, node_id)

        new_rotation = self._replace_axis(
            node.rotation,
            axis,
            value,
        )

        node._set_rotation(new_rotation)

    def scale(
        self,
        scene: AtlasScene,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        """Set one scale axis on a scene node."""
        axis = self._validate_axis(axis)
        value = self._validate_value(value)
        node = self._get_node(scene, node_id)

        new_scale = self._replace_axis(
            node.scale,
            axis,
            value,
        )

        node._set_scale(new_scale)
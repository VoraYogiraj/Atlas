"""ENG-051 — Atlas Basic Editing."""

from __future__ import annotations

from typing import Any

from .scene import AtlasScene


class AtlasBasicEditing:
    """Deterministic presentation-state transformation editing.

    ENG-051 owns basic SceneNode transformation editing.

    This layer:
    - operates only on AtlasScene presentation state,
    - does not mutate AtlasResource or AtlasProject state,
    - does not own selection,
    - does not own gizmos,
    - does not perform rendering or input handling,
    - performs single-axis translation, rotation, and scale edits.

    The supplied value is the resulting value of the selected axis.
    """

    _VALID_AXES = frozenset({"x", "y", "z"})

    def __eq__(self, other: object) -> bool:
        """Basic editing has no instance-specific state."""
        return isinstance(other, AtlasBasicEditing)

    def _validate_axis(self, axis: Any) -> str:
        if not isinstance(axis, str):
            raise TypeError("axis must be a string")

        if axis not in self._VALID_AXES:
            raise ValueError("axis must be one of: x, y, z")

        return axis

    def _validate_value(self, value: Any) -> float:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("value must be numeric")

        return float(value)

    def _get_node(self, scene: AtlasScene, node_id: str):
        if not isinstance(scene, AtlasScene):
            raise TypeError("scene must be an AtlasScene")

        return scene.get_node(node_id)

    @staticmethod
    def _replace_axis(
        vector: tuple[float, float, float],
        axis: str,
        value: float,
    ) -> tuple[float, float, float]:
        values = list(vector)
        index = {"x": 0, "y": 1, "z": 2}[axis]
        values[index] = value
        return (values[0], values[1], values[2])

    def translate(
        self,
        scene: AtlasScene,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        """Set one translation axis on a SceneNode."""
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
        """Set one rotation axis on a SceneNode."""
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
        """Set one scale axis on a SceneNode."""
        axis = self._validate_axis(axis)
        value = self._validate_value(value)
        node = self._get_node(scene, node_id)

        new_scale = self._replace_axis(
            node.scale,
            axis,
            value,
        )

        node._set_scale(new_scale)


__all__ = ["AtlasBasicEditing"]
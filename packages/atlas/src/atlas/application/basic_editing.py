"""ENG-051 — Atlas Basic Editing API skeleton."""

from __future__ import annotations

from typing import Any


class AtlasBasicEditing:
    """Minimal ENG-051 API skeleton.

    RED phase only.
    Transformation behavior is intentionally not implemented.
    """

    def translate(
        self,
        scene: Any,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        raise NotImplementedError("ENG-051 RED: translate not implemented")

    def rotate(
        self,
        scene: Any,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        raise NotImplementedError("ENG-051 RED: rotate not implemented")

    def scale(
        self,
        scene: Any,
        node_id: str,
        axis: str,
        value: Any,
    ) -> None:
        raise NotImplementedError("ENG-051 RED: scale not implemented")
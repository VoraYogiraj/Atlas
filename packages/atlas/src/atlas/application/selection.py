"""
Atlas Resource Selection

ENG-039 — Atlas UI Architecture
ENG-049 — Atlas 3D Workspace Selection

Selection is identity-based and never owns a Resource copy.

AtlasResourceSelection is the existing identity-only resource selection
value object and its constructor/validation contract is intentionally
preserved.

AtlasSelectionState is the workspace-level mutable selection state used by
the 3D workspace. It supports an empty state while keeping resource and
scene-node identities distinct.
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.core.aid import AtlasID


@dataclass(slots=True)
class AtlasResourceSelection:
    """
    UI selection represented only by canonical AtlasID.

    ENG-039 contract:
    - resource_id is required
    - resource_id must be an AtlasID
    - no Resource object is owned
    """

    resource_id: AtlasID

    def __post_init__(self) -> None:
        if not isinstance(self.resource_id, AtlasID):
            raise TypeError("resource_id must be an AtlasID")


class AtlasSelectionState:
    """
    Mutable single-selection state for the Atlas 3D workspace.

    The state deliberately separates two identities:

    - resource_id: canonical engineering identity represented by AtlasID
    - node_id: viewport/scene-node identity represented by str

    The state may be empty. At most one selection is active at any time.

    This class does not:
    - own or resolve an AtlasScene
    - own AtlasResource objects
    - own relationships or graphs
    - depend on a renderer
    - perform picking or raycasting
    - perform highlighting
    - manage input events
    - perform engineering edits
    """

    __slots__ = ("_resource_id", "_node_id")

    def __init__(self) -> None:
        self._resource_id: AtlasID | None = None
        self._node_id: str | None = None

    @property
    def resource_id(self) -> AtlasID | None:
        """Return the currently selected engineering resource identity."""
        return self._resource_id

    @property
    def node_id(self) -> str | None:
        """Return the currently selected viewport scene-node identity."""
        return self._node_id

    @property
    def is_selected(self) -> bool:
        """Return True when either a resource or node is selected."""
        return self._resource_id is not None or self._node_id is not None

    def select_resource(self, *, resource_id: AtlasID) -> None:
        """
        Select an engineering resource by its canonical AtlasID.

        Selecting a resource clears any existing scene-node selection.
        Validation occurs before state mutation.
        """
        if not isinstance(resource_id, AtlasID):
            raise TypeError("resource_id must be an AtlasID")

        self._resource_id = resource_id
        self._node_id = None

    def select_node(
        self,
        *,
        node_id: str,
        resource_id: AtlasID | None = None,
    ) -> None:
        """
        Select a scene node.

        ``node_id`` is the viewport identity and must be a non-empty,
        non-whitespace string.

        ``resource_id`` is optional because a scene node does not have to
        reference an engineering resource.

        Selecting a node clears any existing resource selection.
        Validation occurs before state mutation.
        """
        if not isinstance(node_id, str):
            raise TypeError("node_id must be a string")

        if not node_id.strip():
            raise ValueError("node_id must not be empty or whitespace")

        if resource_id is not None and not isinstance(resource_id, AtlasID):
            raise TypeError("resource_id must be an AtlasID or None")

        self._resource_id = resource_id
        self._node_id = node_id

    def clear(self) -> None:
        """Clear the current selection."""
        self._resource_id = None
        self._node_id = None


__all__ = [
    "AtlasResourceSelection",
    "AtlasSelectionState",
]
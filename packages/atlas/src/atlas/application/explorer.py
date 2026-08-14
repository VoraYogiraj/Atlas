"""
Atlas Explorer

ENG-042 — Atlas Explorer

Read-oriented navigation and discovery capability for Atlas Projects.

The Explorer presents canonical Atlas information through the ENG-039
Application Boundary and remains independent from the Resource Registry,
Classification Hierarchy, Resource Graph, persistence, exchange, Agents,
and frontend technology.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from atlas.application.application import AtlasApplication
from atlas.application.selection import AtlasResourceSelection
from atlas.core.aid import AtlasID


# ---------------------------------------------------------------------------
# Explorer Node
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasExplorerNode:
    """
    Lightweight presentation node for the Explorer.

    The node may represent a Project, Classification, Resource, or
    Relationship Group.

    It never owns the canonical Atlas object.
    """

    node_id: str
    node_type: str
    label: str
    resource_id: AtlasID | None = None
    classification_id: str | None = None
    parent_id: str | None = None
    children: tuple["AtlasExplorerNode", ...] = ()
    expandable: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str):
            raise TypeError("node_id must be a string")

        if not self.node_id.strip():
            raise ValueError("node_id cannot be empty")

        if not isinstance(self.node_type, str):
            raise TypeError("node_type must be a string")

        if not self.node_type.strip():
            raise ValueError("node_type cannot be empty")

        if not isinstance(self.label, str):
            raise TypeError("label must be a string")

        if not isinstance(self.resource_id, (AtlasID, type(None))):
            raise TypeError(
                "resource_id must be an AtlasID or None"
            )

        if not isinstance(
            self.classification_id,
            (str, type(None)),
        ):
            raise TypeError(
                "classification_id must be a string or None"
            )

        if not isinstance(
            self.parent_id,
            (str, type(None)),
        ):
            raise TypeError(
                "parent_id must be a string or None"
            )

        if not isinstance(self.children, tuple):
            raise TypeError("children must be a tuple")

        if not isinstance(self.expandable, bool):
            raise TypeError("expandable must be a boolean")


# ---------------------------------------------------------------------------
# Explorer Presentation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasExplorerPresentation:
    """
    Derived Explorer presentation model.

    This object contains presentation data only and never embeds
    AtlasProject or canonical Resource objects.
    """

    project_id: str
    project_name: str
    root: AtlasExplorerNode
    nodes: tuple[AtlasExplorerNode, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.project_id, str):
            raise TypeError("project_id must be a string")

        if not self.project_id.strip():
            raise ValueError("project_id cannot be empty")

        if not isinstance(self.project_name, str):
            raise TypeError("project_name must be a string")

        if not isinstance(self.root, AtlasExplorerNode):
            raise TypeError(
                "root must be an AtlasExplorerNode"
            )

        if not isinstance(self.nodes, tuple):
            raise TypeError("nodes must be a tuple")


# ---------------------------------------------------------------------------
# Explorer
# ---------------------------------------------------------------------------


class AtlasExplorer:
    """
    Project navigation and discovery surface.

    The Explorer is deliberately read-oriented. It derives presentation
    nodes from the canonical AtlasProject exposed through AtlasApplication.

    It owns only transient UI state:

    - expansion state
    - selection identity
    - loading state
    - error state
    """

    explorer_id = "explorer"

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
        self._expanded_nodes: set[str] = set()
        self._selected_resource_id: AtlasID | None = None
        self._is_loading = False
        self._error: str | None = None

    # ------------------------------------------------------------------
    # Application boundary
    # ------------------------------------------------------------------

    @property
    def application(self) -> AtlasApplication:
        """Return the ENG-039 application boundary."""
        return self._application

    # ------------------------------------------------------------------
    # UI state
    # ------------------------------------------------------------------

    @property
    def selected_resource_id(self) -> AtlasID | None:
        return self._selected_resource_id

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @property
    def error(self) -> str | None:
        return self._error

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(
        self,
        *,
        group_by: str | None = None,
    ) -> AtlasExplorerPresentation:
        """
        Build a fresh Explorer presentation from canonical Atlas state.
        """

        project = self._application.project

        self._error = None
        self._is_loading = False

        root = AtlasExplorerNode(
            node_id=f"project:{project.aid}",
            node_type="project",
            label=project.name,
            parent_id=None,
            expandable=project.resource_count > 0,
        )

        nodes: list[AtlasExplorerNode] = [root]

        resources = list(project.resources)

        if group_by is None:
            nodes.extend(
                self._resource_nodes(
                    resources,
                    parent_id=root.node_id,
                )
            )

        elif group_by == "classification":
            nodes.extend(
                self._classification_grouped_nodes(
                    resources,
                    parent_id=root.node_id,
                )
            )

        else:
            raise ValueError(
                f"Unsupported Explorer grouping: {group_by}"
            )

        return AtlasExplorerPresentation(
            project_id=str(project.aid),
            project_name=project.name,
            root=root,
            nodes=tuple(nodes),
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
    ) -> tuple[AtlasExplorerNode, ...]:
        """
        Search canonical project Resources and Classifications.

        Search is read-only.
        """

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        normalized = query.strip().lower()

        if not normalized:
            return ()

        project = self._application.project

        results: list[AtlasExplorerNode] = []

        for resource in project.resources:
            name = resource.name or ""
            resource_id = str(resource.aid)
            classification = resource.classification.name

            haystack = (
                f"{name} "
                f"{resource_id} "
                f"{classification}"
            ).lower()

            if normalized in haystack:
                results.append(
                    self._resource_node(
                        resource,
                        parent_id=None,
                    )
                )

        return tuple(results)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter(
        self,
        *,
        classification: str | None = None,
        lifecycle: str | None = None,
    ) -> tuple[AtlasExplorerNode, ...]:
        """
        Filter canonical Resources.

        Filtering is read-only and returns presentation nodes.
        """

        if classification is not None:
            if not isinstance(classification, str):
                raise TypeError(
                    "classification must be a string or None"
                )

            classification = classification.strip().lower()

        if lifecycle is not None:
            if not isinstance(lifecycle, str):
                raise TypeError(
                    "lifecycle must be a string or None"
                )

            lifecycle = lifecycle.strip().lower()

        project = self._application.project
        results: list[AtlasExplorerNode] = []

        for resource in project.resources:
            if classification is not None:
                resource_classification = (
                    resource.classification.name.lower()
                )

                if (
                    resource_classification != classification
                    and resource.classification.id.lower()
                    != classification
                ):
                    continue

            if lifecycle is not None:
                resource_lifecycle = getattr(
                    resource.lifecycle,
                    "name",
                    str(resource.lifecycle),
                ).lower()

                if resource_lifecycle != lifecycle:
                    continue

            results.append(
                self._resource_node(
                    resource,
                    parent_id=None,
                )
            )

        return tuple(results)

    # ------------------------------------------------------------------
    # Expansion
    # ------------------------------------------------------------------

    def set_expanded(
        self,
        node_id: str,
        expanded: bool,
    ) -> None:
        """Set transient UI expansion state for a node."""
        if not isinstance(node_id, str):
            raise TypeError("node_id must be a string")

        if not node_id.strip():
            raise ValueError("node_id cannot be empty")

        if not isinstance(expanded, bool):
            raise TypeError(
                "expanded must be a boolean"
            )

        if expanded:
            self._expanded_nodes.add(node_id)
        else:
            self._expanded_nodes.discard(node_id)

    def is_expanded(
        self,
        node_id: str,
    ) -> bool:
        """Return transient UI expansion state."""
        if not isinstance(node_id, str):
            raise TypeError("node_id must be a string")

        return node_id in self._expanded_nodes

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_resource(
        self,
        resource_id: AtlasID | None,
    ) -> None:
        """
        Set the transient selected Resource identity.

        Selection uses AtlasID only.
        """

        if resource_id is not None and not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID or None"
            )

        self._selected_resource_id = resource_id

    def to_selection(
        self,
    ) -> AtlasResourceSelection | None:
        """
        Convert current Explorer selection into the ENG-039 selection model.
        """

        if self._selected_resource_id is None:
            return None

        return AtlasResourceSelection(
            resource_id=self._selected_resource_id,
        )

    # ------------------------------------------------------------------
    # Loading / error
    # ------------------------------------------------------------------

    def set_loading(
        self,
        loading: bool,
    ) -> None:
        """Set transient loading UI state."""
        if not isinstance(loading, bool):
            raise TypeError(
                "loading must be a boolean"
            )

        self._is_loading = loading

    def set_error(
        self,
        message: str | None,
    ) -> None:
        """Set or clear transient Explorer error state."""
        if message is not None and not isinstance(
            message,
            str,
        ):
            raise TypeError(
                "message must be a string or None"
            )

        if isinstance(message, str) and not message.strip():
            raise ValueError(
                "message cannot be empty"
            )

        self._error = message

    # ------------------------------------------------------------------
    # Internal presentation builders
    # ------------------------------------------------------------------

    @classmethod
    def _resource_node(
        cls,
        resource,
        *,
        parent_id: str | None,
    ) -> AtlasExplorerNode:
        """Convert one canonical Resource into a presentation node."""

        classification = resource.classification

        return AtlasExplorerNode(
            node_id=f"resource:{resource.aid}",
            node_type="resource",
            label=resource.name or str(resource.aid),
            resource_id=resource.aid,
            classification_id=classification.id,
            parent_id=parent_id,
            expandable=bool(
                resource.relationships
            ),
        )

    @classmethod
    def _resource_nodes(
        cls,
        resources,
        *,
        parent_id: str | None,
    ) -> list[AtlasExplorerNode]:
        """Build Resource nodes preserving Registry iteration order."""

        return [
            cls._resource_node(
                resource,
                parent_id=parent_id,
            )
            for resource in resources
        ]

    @classmethod
    def _classification_grouped_nodes(
        cls,
        resources,
        *,
        parent_id: str | None,
    ) -> list[AtlasExplorerNode]:
        """
        Build Classification presentation groups while deriving everything
        from canonical Resource Classification objects.
        """

        groups: dict[str, list] = {}

        for resource in resources:
            classification = resource.classification
            groups.setdefault(
                classification.id,
                [],
            ).append(resource)

        nodes: list[AtlasExplorerNode] = []

        for classification_id, grouped_resources in groups.items():
            classification = grouped_resources[0].classification

            group_node = AtlasExplorerNode(
                node_id=f"classification:{classification.id}",
                node_type="classification",
                label=classification.name,
                classification_id=classification.id,
                parent_id=parent_id,
                expandable=bool(grouped_resources),
            )

            nodes.append(group_node)

            for resource in grouped_resources:
                nodes.append(
                    cls._resource_node(
                        resource,
                        parent_id=group_node.node_id,
                    )
                )

        return nodes
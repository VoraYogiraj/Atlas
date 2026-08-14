"""
Atlas Inspector

ENG-043 — Atlas Inspector

Read-oriented Resource-level detail presentation capability.

The Inspector consumes an AtlasID selection, resolves the canonical
AtlasResource through AtlasApplication/AtlasProject, and produces a
dedicated presentation model.

The Inspector does not own engineering state, registries, graphs,
persistence, exchange, Agents, or mutation logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from atlas.application.application import AtlasApplication
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource


# ---------------------------------------------------------------------------
# Presentation support models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasInspectorClassification:
    """Presentation representation of a Resource Classification."""

    id: str
    name: str
    path: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("id must be a string")

        if not self.id.strip():
            raise ValueError("id cannot be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not isinstance(self.path, tuple):
            raise TypeError("path must be a tuple")


@dataclass(frozen=True, slots=True)
class AtlasInspectorRelationship:
    """Presentation representation of an AtlasRelationship."""

    relationship_id: str
    relationship_type: str
    source_id: AtlasID
    target_id: AtlasID
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.relationship_id, str):
            raise TypeError("relationship_id must be a string")

        if not self.relationship_id.strip():
            raise ValueError(
                "relationship_id cannot be empty"
            )

        if not isinstance(self.relationship_type, str):
            raise TypeError(
                "relationship_type must be a string"
            )

        if not self.relationship_type.strip():
            raise ValueError(
                "relationship_type cannot be empty"
            )

        if not isinstance(self.source_id, AtlasID):
            raise TypeError(
                "source_id must be an AtlasID"
            )

        if not isinstance(self.target_id, AtlasID):
            raise TypeError(
                "target_id must be an AtlasID"
            )

        if not isinstance(self.description, str):
            raise TypeError(
                "description must be a string"
            )


# ---------------------------------------------------------------------------
# Inspector presentation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasInspectorPresentation:
    """
    Derived Resource detail presentation.

    This object contains presentation data only.
    """

    resource_id: AtlasID
    name: str | None

    classification: AtlasInspectorClassification | None = None
    classification_path: tuple[str, ...] = ()
    lifecycle: object | None = None

    properties: dict[str, object] = field(
        default_factory=dict,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    tags: tuple[object, ...] = ()

    categories: tuple[object, ...] = ()

    relationships: tuple[
        AtlasInspectorRelationship,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        if not isinstance(
            self.name,
            (str, type(None)),
        ):
            raise TypeError(
                "name must be a string or None"
            )

        if not isinstance(
            self.classification,
            (
                AtlasInspectorClassification,
                type(None),
            ),
        ):
            raise TypeError(
                "classification must be an AtlasInspectorClassification or None"
            )

        if not isinstance(
            self.classification_path,
            tuple,
        ):
            raise TypeError(
                "classification_path must be a tuple"
            )

        if not isinstance(
            self.properties,
            dict,
        ):
            raise TypeError(
                "properties must be a dict"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dict"
            )

        if not isinstance(
            self.tags,
            tuple,
        ):
            raise TypeError(
                "tags must be a tuple"
            )

        if not isinstance(
            self.categories,
            tuple,
        ):
            raise TypeError(
                "categories must be a tuple"
            )

        if not isinstance(
            self.relationships,
            tuple,
        ):
            raise TypeError(
                "relationships must be a tuple"
            )


# ---------------------------------------------------------------------------
# Inspector
# ---------------------------------------------------------------------------


class AtlasInspector:
    """
    Resource-level detail presentation surface.

    The Inspector is intentionally read-only for ENG-043.
    """

    inspector_id = "inspector"

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
    # Selection state
    # ------------------------------------------------------------------

    @property
    def selected_resource_id(self) -> AtlasID | None:
        return self._selected_resource_id

    def set_selection(
        self,
        resource_id: AtlasID | None,
    ) -> None:
        """
        Set the currently inspected Resource identity.
        """

        if resource_id is not None and not isinstance(
            resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID or None"
            )

        self._selected_resource_id = resource_id
        self._error = None

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    def refresh(
        self,
    ) -> AtlasInspectorPresentation | None:
        """
        Build a fresh Inspector presentation.

        Returns None when no Resource is selected.

        Raises KeyError when a selected AtlasID cannot be resolved.
        """

        resource_id = self._selected_resource_id

        if resource_id is None:
            return None

        self._error = None

        project = self._application.project

        resource = project.require_resource(
            resource_id,
        )

        return self._build_presentation(
            resource,
        )

    # ------------------------------------------------------------------
    # Loading / errors
    # ------------------------------------------------------------------

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    def set_loading(
        self,
        loading: bool,
    ) -> None:
        if not isinstance(
            loading,
            bool,
        ):
            raise TypeError(
                "loading must be a boolean"
            )

        self._is_loading = loading

    @property
    def error(self) -> str | None:
        return self._error

    def set_error(
        self,
        message: str | None,
    ) -> None:
        if message is not None and not isinstance(
            message,
            str,
        ):
            raise TypeError(
                "message must be a string or None"
            )

        if isinstance(
            message,
            str,
        ) and not message.strip():
            raise ValueError(
                "message cannot be empty"
            )

        self._error = message

    # ------------------------------------------------------------------
    # Internal builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_presentation(
        resource: AtlasResource,
    ) -> AtlasInspectorPresentation:
        """Convert canonical Resource state to presentation state."""

        classification = resource.classification

        classification_presentation = (
            AtlasInspectorClassification(
                id=classification.id,
                name=classification.name,
                path=classification.path,
            )
        )

        relationship_presentations = tuple(
            AtlasInspectorRelationship(
                relationship_id=relationship.id,
                relationship_type=relationship.relationship_type,
                source_id=relationship.source.aid,
                target_id=relationship.target.aid,
                description=relationship.description,
            )
            for relationship in resource.relationships
        )

        return AtlasInspectorPresentation(
            resource_id=resource.aid,
            name=resource.name,
            classification=classification_presentation,
            classification_path=classification.path,
            lifecycle=resource.lifecycle,
            properties=dict(resource.properties),
            metadata=dict(resource.metadata),
            tags=tuple(resource.tags),
            categories=tuple(resource.categories),
            relationships=relationship_presentations,
        )
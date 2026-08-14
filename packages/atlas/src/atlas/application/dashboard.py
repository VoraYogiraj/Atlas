"""
Atlas Dashboard

ENG-041 — Atlas Dashboard

Read-oriented project-level presentation capability.

The Dashboard derives presentation state from the canonical AtlasProject
through the ENG-039 AtlasApplication boundary.

It does not own engineering state, registries, graphs, validation engines,
agents, persistence, or exchange layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from atlas.application.application import AtlasApplication
from atlas.core.aid import AtlasID


# ---------------------------------------------------------------------------
# Summary models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasResourceSummary:
    """Derived Resource counts for Dashboard presentation."""

    total: int = 0
    active: int = 0
    archived: int = 0
    deleted: int = 0
    by_classification: dict[str, int] = field(
        default_factory=dict,
    )


@dataclass(frozen=True, slots=True)
class AtlasClassificationSummary:
    """Derived classification counts."""

    counts: dict[str, int] = field(
        default_factory=dict,
    )


@dataclass(frozen=True, slots=True)
class AtlasRelationshipSummary:
    """Derived relationship counts."""

    total: int = 0
    by_type: dict[str, int] = field(
        default_factory=dict,
    )


@dataclass(frozen=True, slots=True)
class AtlasValidationSummary:
    """High-level validation presentation data."""

    status: str = "No findings"
    errors: int = 0
    warnings: int = 0
    passed: int = 0


@dataclass(frozen=True, slots=True)
class AtlasAgentSummary:
    """High-level Agent/activity presentation data."""

    active: int = 0
    completed: int = 0
    failed: int = 0
    recent_activity: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AtlasDashboardSelectionTarget:
    """
    Identity-based Dashboard navigation target.

    The target stores only AtlasID, never a Resource object.
    """

    resource_id: AtlasID

    def __post_init__(self) -> None:
        if not isinstance(
            self.resource_id,
            AtlasID,
        ):
            raise TypeError(
                "resource_id must be an AtlasID"
            )


# ---------------------------------------------------------------------------
# Dashboard presentation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasDashboardPresentation:
    """
    Derived Dashboard presentation model.

    This is not an AtlasProject and does not contain the canonical project.
    """

    project_id: str
    project_name: str
    resource_summary: AtlasResourceSummary = field(
        default_factory=AtlasResourceSummary,
    )
    classification_summary: AtlasClassificationSummary = field(
        default_factory=AtlasClassificationSummary,
    )
    relationship_summary: AtlasRelationshipSummary = field(
        default_factory=AtlasRelationshipSummary,
    )
    validation_summary: AtlasValidationSummary = field(
        default_factory=AtlasValidationSummary,
    )
    agent_summary: AtlasAgentSummary = field(
        default_factory=AtlasAgentSummary,
    )
    project_status: str = "Ready"

    def __post_init__(self) -> None:
        if not isinstance(
            self.project_id,
            str,
        ):
            raise TypeError(
                "project_id must be a string"
            )

        if not self.project_id.strip():
            raise ValueError(
                "project_id cannot be empty"
            )

        if not isinstance(
            self.project_name,
            str,
        ):
            raise TypeError(
                "project_name must be a string"
            )

        if not isinstance(
            self.project_status,
            str,
        ):
            raise TypeError(
                "project_status must be a string"
            )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class AtlasDashboard:
    """
    Project-level, read-oriented Dashboard.

    The Dashboard is bound to ENG-039 AtlasApplication and derives its
    presentation data from the canonical project.

    It deliberately owns no Project, Registry, Graph, Validation Engine,
    Agent Runtime, Persistence, or Exchange component.
    """

    dashboard_id = "dashboard"

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

    @property
    def application(self) -> AtlasApplication:
        """Return the ENG-039 application boundary."""
        return self._application

    def refresh(self) -> AtlasDashboardPresentation:
        """
        Derive a fresh Dashboard presentation from canonical Atlas state.
        """
        project = self._application.project

        resource_summary = self._build_resource_summary(
            project.resources,
        )

        classification_summary = (
            self._build_classification_summary(
                project.resources,
            )
        )

        relationship_summary = (
            self._build_relationship_summary(
                project.relationships,
            )
        )

        validation_summary = (
            self._build_validation_summary()
        )

        agent_summary = self._build_agent_summary()

        return AtlasDashboardPresentation(
            project_id=str(project.aid),
            project_name=project.name,
            resource_summary=resource_summary,
            classification_summary=classification_summary,
            relationship_summary=relationship_summary,
            validation_summary=validation_summary,
            agent_summary=agent_summary,
            project_status="Ready",
        )

    # ------------------------------------------------------------------
    # Derived summaries
    # ------------------------------------------------------------------

    @staticmethod
    def _build_resource_summary(
        resources: Any,
    ) -> AtlasResourceSummary:
        """
        Build Resource counts from the canonical Resource collection.
        """
        items = tuple(resources)

        active = 0
        archived = 0
        deleted = 0
        by_classification: dict[str, int] = {}

        for resource in items:
            lifecycle = str(resource.lifecycle).lower()

            if lifecycle.endswith("active"):
                active += 1
            elif lifecycle.endswith("archived"):
                archived += 1
            elif lifecycle.endswith("deleted"):
                deleted += 1

            classification = str(
                resource.classification
            )

            by_classification[classification] = (
                by_classification.get(
                    classification,
                    0,
                )
                + 1
            )

        return AtlasResourceSummary(
            total=len(items),
            active=active,
            archived=archived,
            deleted=deleted,
            by_classification=by_classification,
        )

    @staticmethod
    def _build_classification_summary(
        resources: Any,
    ) -> AtlasClassificationSummary:
        """
        Build Resource distribution by classification.

        Classification truth remains in Atlas Core.
        """
        counts: dict[str, int] = {}

        for resource in tuple(resources):
            classification = str(
                resource.classification
            )

            counts[classification] = (
                counts.get(
                    classification,
                    0,
                )
                + 1
            )

        return AtlasClassificationSummary(
            counts=counts,
        )

    @staticmethod
    def _build_relationship_summary(
        relationships: Any,
    ) -> AtlasRelationshipSummary:
        """
        Build relationship counts from the canonical Project Graph.
        """
        counts: dict[str, int] = {}

        items = tuple(relationships)

        for relationship in items:
            relationship_type = (
                relationship.relationship_type
            )

            counts[relationship_type] = (
                counts.get(
                    relationship_type,
                    0,
                )
                + 1
            )

        return AtlasRelationshipSummary(
            total=len(items),
            by_type=counts,
        )

    def _build_validation_summary(
        self,
    ) -> AtlasValidationSummary:
        """
        Provide the current high-level validation summary.

        ENG-041 does not reimplement validation. Until the application layer
        exposes a dedicated dashboard validation query, an empty valid summary
        is returned.
        """
        return AtlasValidationSummary(
            status="No findings",
            errors=0,
            warnings=0,
            passed=0,
        )

    def _build_agent_summary(
        self,
    ) -> AtlasAgentSummary:
        """
        Provide the current high-level Agent summary.

        Agent execution remains owned by the existing Agent Runtime. The
        Dashboard deliberately does not create or own an Agent Runtime.
        """
        return AtlasAgentSummary(
            active=0,
            completed=0,
            failed=0,
            recent_activity=(),
        )
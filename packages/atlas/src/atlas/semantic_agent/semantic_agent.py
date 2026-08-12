"""
Atlas Semantic Agent

Specification:
ENG-032 — Semantic Agent
"""

from __future__ import annotations

from typing import Any

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.categories.category import AtlasCategory
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.semantic_tags.tag import AtlasSemanticTag


class AtlasSemanticAgent(AtlasAgent):
    """
    Agent responsible for explicit Resource semantic operations.

    ENG-032 v0.1 is deterministic.

    It exposes existing:

        - Resource Classification
        - Semantic Tags
        - Categories

    It does not infer semantic meaning.
    """

    DEFAULT_ID = "semantic-agent"
    DEFAULT_NAME = "Semantic Agent"

    def __init__(self) -> None:
        super().__init__(
            id=self.DEFAULT_ID,
            name=self.DEFAULT_NAME,
        )

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """Execute a Semantic operation."""
        try:
            project = self._get_project(request)
            resource = self._get_resource(request, project)
            action = request.action

            handlers = {
                "get_classification": self._get_classification,
                "get_classification_path": self._get_classification_path,
                "list_semantic_tags": self._list_semantic_tags,
                "get_semantic_tag": self._get_semantic_tag,
                "has_semantic_tag": self._has_semantic_tag,
                "add_semantic_tag": self._add_semantic_tag,
                "remove_semantic_tag": self._remove_semantic_tag,
                "list_categories": self._list_categories,
                "get_category": self._get_category,
                "has_category": self._has_category,
                "add_category": self._add_category,
                "remove_category": self._remove_category,
                "get_semantic_context": self._get_semantic_context,
            }

            handler = handlers.get(action)

            if handler is None:
                return self._failure(
                    request,
                    f"Unsupported Semantic Agent action: {action}",
                )

            return handler(
                request,
                resource,
            )

        except Exception as exc:
            return self._failure(
                request,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def _get_classification(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            resource.classification,
        )

    def _get_classification_path(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            resource.classification.path,
        )

    # ------------------------------------------------------------------
    # Semantic Tags
    # ------------------------------------------------------------------

    def _list_semantic_tags(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            list(resource.tags),
        )

    def _get_semantic_tag(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        tag_id = self._required_metadata(
            request,
            "tag_id",
        )

        if tag_id is None:
            return self._failure(
                request,
                "tag_id metadata is required",
            )

        return self._success(
            request,
            resource.get_tag(tag_id),
        )

    def _has_semantic_tag(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        tag_id = self._required_metadata(
            request,
            "tag_id",
        )

        if tag_id is None:
            return self._failure(
                request,
                "tag_id metadata is required",
            )

        return self._success(
            request,
            resource.has_tag(tag_id),
        )

    def _add_semantic_tag(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        tag = self._required_metadata(
            request,
            "tag",
        )

        if not isinstance(
            tag,
            AtlasSemanticTag,
        ):
            return self._failure(
                request,
                "tag metadata must be an AtlasSemanticTag",
            )

        return self._success(
            request,
            resource.add_tag(tag),
        )

    def _remove_semantic_tag(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        tag_id = self._required_metadata(
            request,
            "tag_id",
        )

        if tag_id is None:
            return self._failure(
                request,
                "tag_id metadata is required",
            )

        return self._success(
            request,
            resource.remove_tag(tag_id),
        )

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def _list_categories(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            list(resource.categories),
        )

    def _get_category(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        category_id = self._required_metadata(
            request,
            "category_id",
        )

        if category_id is None:
            return self._failure(
                request,
                "category_id metadata is required",
            )

        return self._success(
            request,
            resource.get_category(category_id),
        )

    def _has_category(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        category_id = self._required_metadata(
            request,
            "category_id",
        )

        if category_id is None:
            return self._failure(
                request,
                "category_id metadata is required",
            )

        return self._success(
            request,
            resource.has_category(category_id),
        )

    def _add_category(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        category = self._required_metadata(
            request,
            "category",
        )

        if not isinstance(
            category,
            AtlasCategory,
        ):
            return self._failure(
                request,
                "category metadata must be an AtlasCategory",
            )

        return self._success(
            request,
            resource.add_category(category),
        )

    def _remove_category(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        category_id = self._required_metadata(
            request,
            "category_id",
        )

        if category_id is None:
            return self._failure(
                request,
                "category_id metadata is required",
            )

        return self._success(
            request,
            resource.remove_category(category_id),
        )

    # ------------------------------------------------------------------
    # Semantic Context
    # ------------------------------------------------------------------

    def _get_semantic_context(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            {
                "classification": resource.classification,
                "classification_path": resource.classification.path,
                "semantic_tags": list(resource.tags),
                "categories": list(resource.categories),
            },
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _get_project(
        request: AtlasAgentRequest,
    ) -> AtlasProject:
        project = request.context.project

        if not isinstance(project, AtlasProject):
            raise ValueError(
                "AtlasProject is required in Agent context"
            )

        return project

    @staticmethod
    def _get_resource(
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasResource:
        resource = request.context.metadata.get("resource")

        if not isinstance(resource, AtlasResource):
            raise ValueError(
                "resource metadata must be an AtlasResource"
            )

        registered = project.get_resource(resource.aid)

        if registered is None:
            raise ValueError(
                f"Resource is not registered with Project: {resource.aid}"
            )

        return registered

    @staticmethod
    def _required_metadata(
        request: AtlasAgentRequest,
        key: str,
    ) -> Any:
        return request.context.metadata.get(key)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _success(
        self,
        request: AtlasAgentRequest,
        output: Any,
    ) -> AtlasAgentResult:
        self._set_status(
            AtlasAgentStatus.COMPLETED
        )

        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.COMPLETED,
            output=output,
            error=None,
        )

    def _failure(
        self,
        request: AtlasAgentRequest,
        error: str,
    ) -> AtlasAgentResult:
        self._set_status(
            AtlasAgentStatus.FAILED
        )

        return AtlasAgentResult(
            id=f"result-{request.id}",
            request_id=request.id,
            agent_id=self.id,
            status=AtlasAgentStatus.FAILED,
            output=None,
            error=error,
        )
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

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        request: AtlasAgentRequest,
    ) -> AtlasAgentResult:
        """
        Execute a Semantic operation.

        Supported actions:

            get_classification
            get_classification_path
            list_semantic_tags
            get_semantic_tag
            has_semantic_tag
            add_semantic_tag
            remove_semantic_tag
            list_categories
            get_category
            has_category
            add_category
            remove_category
            get_semantic_context
        """
        try:
            project = self._get_project(request)
            resource = self._get_resource(
                request,
                project,
            )

            action = request.action

            if action == "get_classification":
                return self._get_classification(
                    request,
                    resource,
                )

            if action == "get_classification_path":
                return self._get_classification_path(
                    request,
                    resource,
                )

            if action == "list_semantic_tags":
                return self._list_semantic_tags(
                    request,
                    resource,
                )

            if action == "get_semantic_tag":
                return self._get_semantic_tag(
                    request,
                    resource,
                )

            if action == "has_semantic_tag":
                return self._has_semantic_tag(
                    request,
                    resource,
                )

            if action == "add_semantic_tag":
                return self._add_semantic_tag(
                    request,
                    resource,
                )

            if action == "remove_semantic_tag":
                return self._remove_semantic_tag(
                    request,
                    resource,
                )

            if action == "list_categories":
                return self._list_categories(
                    request,
                    resource,
                )

            if action == "get_category":
                return self._get_category(
                    request,
                    resource,
                )

            if action == "has_category":
                return self._has_category(
                    request,
                    resource,
                )

            if action == "add_category":
                return self._add_category(
                    request,
                    resource,
                )

            if action == "remove_category":
                return self._remove_category(
                    request,
                    resource,
                )

            if action == "get_semantic_context":
                return self._get_semantic_context(
                    request,
                    resource,
                )

            return self._failure(
                request,
                f"Unsupported Semantic Agent action: {action}",
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

        tag = resource.get_semantic_tag(
            tag_id
        )

        return self._success(
            request,
            tag,
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
            resource.has_semantic_tag(
                tag_id
            ),
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

        added = resource.add_semantic_tag(
            tag
        )

        return self._success(
            request,
            added,
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

        removed = resource.remove_semantic_tag(
            tag_id
        )

        return self._success(
            request,
            removed,
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

        category = resource.get_category(
            category_id
        )

        return self._success(
            request,
            category,
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
            resource.has_category(
                category_id
            ),
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

        added = resource.add_category(
            category
        )

        return self._success(
            request,
            added,
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

        removed = resource.remove_category(
            category_id
        )

        return self._success(
            request,
            removed,
        )

    # ------------------------------------------------------------------
    # Semantic Context
    # ------------------------------------------------------------------

    def _get_semantic_context(
        self,
        request: AtlasAgentRequest,
        resource: AtlasResource,
    ) -> AtlasAgentResult:
        context = {
            "classification": resource.classification,
            "classification_path": (
                resource.classification.path
            ),
            "semantic_tags": list(
                resource.tags
            ),
            "categories": list(
                resource.categories
            ),
        }

        return self._success(
            request,
            context,
        )

    # ------------------------------------------------------------------
    # Context Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _get_project(
        request: AtlasAgentRequest,
    ) -> AtlasProject:
        project = request.context.project

        if not isinstance(
            project,
            AtlasProject,
        ):
            raise ValueError(
                "AtlasProject is required in Agent context"
            )

        return project

    @staticmethod
    def _get_resource(
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasResource:
        resource = request.context.metadata.get(
            "resource"
        )

        if not isinstance(
            resource,
            AtlasResource,
        ):
            raise ValueError(
                "resource metadata must be an AtlasResource"
            )

        registered = project.get_resource(
            resource.aid
        )

        if registered is None:
            raise ValueError(
                "Resource is not registered with Project: "
                f"{resource.aid}"
            )

        return registered

    @staticmethod
    def _required_metadata(
        request: AtlasAgentRequest,
        key: str,
    ) -> Any:
        return request.context.metadata.get(
            key
        )

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
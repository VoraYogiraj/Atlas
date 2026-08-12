"""
Atlas Registry Agent

Specification:
ENG-031 — Registry Agent
"""

from __future__ import annotations

from typing import Any

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.project.project import AtlasProject


class AtlasRegistryAgent(AtlasAgent):
    """
    Agent responsible for Resource Registry query operations.

    The Registry Agent is read-oriented and delegates registry access
    through AtlasProject.
    """

    DEFAULT_ID = "registry-agent"
    DEFAULT_NAME = "Registry Agent"

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
        Execute a Registry query.

        Supported actions:

            get_resource
            require_resource
            contains_resource
            resources_for_classification
            resource_count
            list_resources
        """
        try:
            project = self._get_project(request)

            action = request.action

            if action == "get_resource":
                return self._get_resource(
                    request,
                    project,
                )

            if action == "require_resource":
                return self._require_resource(
                    request,
                    project,
                )

            if action == "contains_resource":
                return self._contains_resource(
                    request,
                    project,
                )

            if action == "resources_for_classification":
                return self._resources_for_classification(
                    request,
                    project,
                )

            if action == "resource_count":
                return self._resource_count(
                    request,
                    project,
                )

            if action == "list_resources":
                return self._list_resources(
                    request,
                    project,
                )

            return self._failure(
                request,
                f"Unsupported Registry Agent action: {action}",
            )

        except Exception as exc:
            return self._failure(
                request,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Get Resource
    # ------------------------------------------------------------------

    def _get_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource_id = request.context.metadata.get(
            "resource_id"
        )

        if resource_id is None:
            return self._failure(
                request,
                "resource_id metadata is required",
            )

        resource = project.get_resource(
            resource_id
        )

        return self._success(
            request,
            resource,
        )

    # ------------------------------------------------------------------
    # Require Resource
    # ------------------------------------------------------------------

    def _require_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource_id = request.context.metadata.get(
            "resource_id"
        )

        if resource_id is None:
            return self._failure(
                request,
                "resource_id metadata is required",
            )

        resource = project.require_resource(
            resource_id
        )

        return self._success(
            request,
            resource,
        )

    # ------------------------------------------------------------------
    # Contains Resource
    # ------------------------------------------------------------------

    def _contains_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource_id = request.context.metadata.get(
            "resource_id"
        )

        if resource_id is None:
            return self._failure(
                request,
                "resource_id metadata is required",
            )

        result = project.resources.contains(
            resource_id
        )

        return self._success(
            request,
            result,
        )

    # ------------------------------------------------------------------
    # Classification Query
    # ------------------------------------------------------------------

    def _resources_for_classification(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        classification_id = (
            request.context.metadata.get(
                "classification_id"
            )
        )

        if classification_id is None:
            return self._failure(
                request,
                "classification_id metadata is required",
            )

        resources = (
            project.resources_for_classification(
                classification_id
            )
        )

        return self._success(
            request,
            resources,
        )

    # ------------------------------------------------------------------
    # Resource Count
    # ------------------------------------------------------------------

    def _resource_count(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            project.resource_count,
        )

    # ------------------------------------------------------------------
    # List Resources
    # ------------------------------------------------------------------

    def _list_resources(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resources = list(
            project.resources
        )

        return self._success(
            request,
            resources,
        )

    # ------------------------------------------------------------------
    # Context
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
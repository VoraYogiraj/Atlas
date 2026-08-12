"""
Atlas Resource Agent

Specification:
ENG-030 — Resource Agent
"""

from __future__ import annotations

from typing import Any

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject


class AtlasResourceAgent(AtlasAgent):
    """
    Agent responsible for Resource-domain operations.

    The Resource Agent delegates all Resource integrity rules to
    AtlasProject rather than directly modifying the Project's internal
    registries.
    """

    DEFAULT_ID = "resource-agent"
    DEFAULT_NAME = "Resource Agent"

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
        Execute a Resource operation.

        Supported actions:

            create_resource
            get_resource
            require_resource
            update_resource
            delete_resource
        """
        try:
            project = self._get_project(request)

            action = request.action

            if action == "create_resource":
                return self._create_resource(
                    request,
                    project,
                )

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

            if action == "update_resource":
                return self._update_resource(
                    request,
                    project,
                )

            if action == "delete_resource":
                return self._delete_resource(
                    request,
                    project,
                )

            return self._failure(
                request,
                f"Unsupported Resource Agent action: {action}",
            )

        except Exception as exc:
            return self._failure(
                request,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def _create_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._metadata_value(
            request,
            "resource",
        )

        if not isinstance(
            resource,
            AtlasResource,
        ):
            return self._failure(
                request,
                "resource metadata must be an AtlasResource",
            )

        created = project.add_resource(
            resource
        )

        return self._success(
            request,
            created,
        )

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def _get_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource_id = self._metadata_value(
            request,
            "resource_id",
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
    # Require
    # ------------------------------------------------------------------

    def _require_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource_id = self._metadata_value(
            request,
            "resource_id",
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
    # Update
    # ------------------------------------------------------------------

    def _update_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._metadata_value(
            request,
            "resource",
        )

        if not isinstance(
            resource,
            AtlasResource,
        ):
            return self._failure(
                request,
                "resource metadata must be an AtlasResource",
            )

        registered = project.get_resource(
            resource.aid
        )

        if registered is None:
            return self._failure(
                request,
                f"Resource is not registered with Project: "
                f"{resource.aid}",
            )

        if "name" not in request.context.metadata:
            return self._failure(
                request,
                "name metadata is required",
            )

        name = request.context.metadata["name"]

        if not isinstance(
            name,
            str,
        ):
            return self._failure(
                request,
                "name metadata must be a string",
            )

        resource.name = name

        return self._success(
            request,
            resource,
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _delete_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._metadata_value(
            request,
            "resource",
        )

        if not isinstance(
            resource,
            AtlasResource,
        ):
            return self._failure(
                request,
                "resource metadata must be an AtlasResource",
            )

        removed = project.remove_resource(
            resource
        )

        return self._success(
            request,
            removed,
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

    @staticmethod
    def _metadata_value(
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
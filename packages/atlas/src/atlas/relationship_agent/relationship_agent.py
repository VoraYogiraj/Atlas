"""
Atlas Relationship Agent

Specification:
ENG-033 — Relationship Agent
"""

from __future__ import annotations

from typing import Any

from atlas.agents.agent import AtlasAgent
from atlas.agents.request import AtlasAgentRequest
from atlas.agents.result import AtlasAgentResult
from atlas.agents.status import AtlasAgentStatus
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.relationships.relationship import AtlasRelationship


class AtlasRelationshipAgent(AtlasAgent):
    """
    Agent responsible for explicit Atlas Relationship and Graph operations.

    ENG-033 v0.1 is deterministic.

    The Agent delegates graph behavior to AtlasProject and
    AtlasResourceGraph. It does not maintain a second graph.
    """

    DEFAULT_ID = "relationship-agent"
    DEFAULT_NAME = "Relationship Agent"

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
        Execute a Relationship / Graph operation.
        """
        try:
            project = self._get_project(request)

            handlers = {
                "add_relationship": self._add_relationship,
                "get_relationships_between": (
                    self._get_relationships_between
                ),
                "relationships_for_resource": (
                    self._relationships_for_resource
                ),
                "outgoing_relationships": (
                    self._outgoing_relationships
                ),
                "incoming_relationships": (
                    self._incoming_relationships
                ),
                "relationships_by_type": (
                    self._relationships_by_type
                ),
                "neighbors": self._neighbors,
                "connected": self._connected,
                "traverse": self._traverse,
                "reachable": self._reachable,
                "remove_relationship": (
                    self._remove_relationship
                ),
                "relationship_count": (
                    self._relationship_count
                ),
            }

            handler = handlers.get(
                request.action
            )

            if handler is None:
                return self._failure(
                    request,
                    (
                        "Unsupported Relationship Agent "
                        f"action: {request.action}"
                    ),
                )

            return handler(
                request,
                project,
            )

        except Exception as exc:
            return self._failure(
                request,
                str(exc),
            )

    # ------------------------------------------------------------------
    # Add
    # ------------------------------------------------------------------

    def _add_relationship(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        relationship = self._metadata(
            request,
            "relationship",
        )

        if not isinstance(
            relationship,
            AtlasRelationship,
        ):
            return self._failure(
                request,
                (
                    "relationship metadata must be "
                    "an AtlasRelationship"
                ),
            )

        added = project.add_relationship(
            relationship
        )

        return self._success(
            request,
            added,
        )

    # ------------------------------------------------------------------
    # Relationship Queries
    # ------------------------------------------------------------------

    def _get_relationships_between(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        first = self._required_resource(
            request,
            "first_resource",
        )

        if first is None:
            return self._failure(
                request,
                "first_resource metadata is required",
            )

        second = self._required_resource(
            request,
            "second_resource",
        )

        if second is None:
            return self._failure(
                request,
                "second_resource metadata is required",
            )

        # The existing project API does not expose get_between(),
        # so use the project graph's authoritative implementation.
        result = project.graph.get_between(
            first,
            second,
        )

        return self._success(
            request,
            result,
        )

    def _relationships_for_resource(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._required_resource(
            request,
            "resource",
        )

        if resource is None:
            return self._failure(
                request,
                "resource metadata is required",
            )

        result = project.relationships_for_resource(
            resource
        )

        return self._success(
            request,
            list(result),
        )

    def _outgoing_relationships(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._required_resource(
            request,
            "resource",
        )

        if resource is None:
            return self._failure(
                request,
                "resource metadata is required",
            )

        result = project.outgoing_relationships(
            resource
        )

        return self._success(
            request,
            list(result),
        )

    def _incoming_relationships(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._required_resource(
            request,
            "resource",
        )

        if resource is None:
            return self._failure(
                request,
                "resource metadata is required",
            )

        result = project.incoming_relationships(
            resource
        )

        return self._success(
            request,
            list(result),
        )

    def _relationships_by_type(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        relationship_type = request.context.metadata.get(
            "relationship_type"
        )

        if relationship_type is None:
            return self._failure(
                request,
                "relationship_type metadata is required",
            )

        if not isinstance(
            relationship_type,
            str,
        ):
            return self._failure(
                request,
                "relationship_type must be a string",
            )

        if not relationship_type.strip():
            return self._failure(
                request,
                "relationship_type cannot be empty",
            )

        result = project.relationships_by_type(
            relationship_type
        )

        return self._success(
            request,
            list(result),
        )

    # ------------------------------------------------------------------
    # Graph Operations
    # ------------------------------------------------------------------

    def _neighbors(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._required_resource(
            request,
            "resource",
        )

        if resource is None:
            return self._failure(
                request,
                "resource metadata is required",
            )

        result = project.graph.neighbors(
            resource
        )

        return self._success(
            request,
            list(result),
        )

    def _connected(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        first = self._required_resource(
            request,
            "first_resource",
        )

        if first is None:
            return self._failure(
                request,
                "first_resource metadata is required",
            )

        second = self._required_resource(
            request,
            "second_resource",
        )

        if second is None:
            return self._failure(
                request,
                "second_resource metadata is required",
            )

        result = project.graph.connected(
            first,
            second,
        )

        return self._success(
            request,
            result,
        )

    def _traverse(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        resource = self._required_resource(
            request,
            "resource",
        )

        if resource is None:
            return self._failure(
                request,
                "resource metadata is required",
            )

        max_depth = request.context.metadata.get(
            "max_depth"
        )

        if (
            max_depth is not None
            and not isinstance(max_depth, int)
        ):
            return self._failure(
                request,
                "max_depth must be an integer or None",
            )

        if (
            max_depth is not None
            and max_depth < 0
        ):
            return self._failure(
                request,
                "max_depth must be greater than or equal to 0",
            )

        result = project.graph.traverse(
            resource,
            max_depth=max_depth,
        )

        return self._success(
            request,
            list(result),
        )

    def _reachable(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        first = self._required_resource(
            request,
            "first_resource",
        )

        if first is None:
            return self._failure(
                request,
                "first_resource metadata is required",
            )

        second = self._required_resource(
            request,
            "second_resource",
        )

        if second is None:
            return self._failure(
                request,
                "second_resource metadata is required",
            )

        result = project.graph.reachable(
            first,
            second,
        )

        return self._success(
            request,
            result,
        )

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def _remove_relationship(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        relationship = self._metadata(
            request,
            "relationship",
        )

        if not isinstance(
            relationship,
            AtlasRelationship,
        ):
            return self._failure(
                request,
                (
                    "relationship metadata must be "
                    "an AtlasRelationship"
                ),
            )

        removed = project.remove_relationship(
            relationship
        )

        return self._success(
            request,
            removed,
        )

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def _relationship_count(
        self,
        request: AtlasAgentRequest,
        project: AtlasProject,
    ) -> AtlasAgentResult:
        return self._success(
            request,
            project.relationship_count,
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
    def _metadata(
        request: AtlasAgentRequest,
        key: str,
    ) -> Any:
        return request.context.metadata.get(
            key
        )

    @staticmethod
    def _required_resource(
        request: AtlasAgentRequest,
        key: str,
    ) -> AtlasResource | None:
        resource = request.context.metadata.get(
            key
        )

        if resource is None:
            return None

        if not isinstance(
            resource,
            AtlasResource,
        ):
            raise ValueError(
                f"{key} metadata must be an AtlasResource"
            )

        return resource

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
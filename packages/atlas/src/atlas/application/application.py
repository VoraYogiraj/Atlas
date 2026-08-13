"""
Atlas Application Boundary

ENG-039 — Atlas UI Architecture

Thin application boundary between UI interactions and the canonical
Atlas domain model.
"""

from __future__ import annotations

from typing import Any

from atlas.application.commands import AtlasCommand
from atlas.application.presentation import AtlasResourcePresentation
from atlas.application.queries import AtlasQuery
from atlas.project.project import AtlasProject


class AtlasApplication:
    """
    Application boundary over an AtlasProject.

    This class intentionally remains thin. It does not replace AtlasProject
    or implement a second engineering model.
    """

    def __init__(self, project: AtlasProject) -> None:
        if not isinstance(project, AtlasProject):
            raise TypeError("project must be an AtlasProject")

        self._project = project

    @property
    def project(self) -> AtlasProject:
        """Return the canonical Atlas project."""
        return self._project

    def execute(self, command: AtlasCommand) -> Any:
        """
        Execute an application command.

        ENG-039 intentionally starts with a minimal command boundary.
        Domain-specific command handlers will be introduced by later
        implementation milestones.
        """
        if not isinstance(command, AtlasCommand):
            raise TypeError("command must be an AtlasCommand")

        if command.name == "noop":
            return None

        raise NotImplementedError(
            f"Command '{command.name}' is not implemented"
        )

    def query(self, query: AtlasQuery) -> Any:
        """
        Execute an application query.

        The initial query boundary exposes only project retrieval and
        deliberately avoids duplicating domain behavior.
        """
        if not isinstance(query, AtlasQuery):
            raise TypeError("query must be an AtlasQuery")

        if query.name == "get_project":
            return self._project

        raise NotImplementedError(
            f"Query '{query.name}' is not implemented"
        )

    def present_resource(
        self,
        resource_id: object,
    ) -> AtlasResourcePresentation:
        """
        Build a presentation representation for a Resource.

        This is intentionally small in ENG-039. Resource lookup remains
        owned by the canonical Resource Registry.
        """
        from atlas.core.aid import AtlasID

        if not isinstance(resource_id, AtlasID):
            raise TypeError(
                "resource_id must be an AtlasID"
            )

        resource = self._project.require_resource(
            resource_id
        )

        return AtlasResourcePresentation(
            resource_id=resource.aid,
            name=resource.name,
            classification=resource.classification,
            properties=dict(resource.properties),
            metadata=dict(resource.metadata),
            lifecycle=str(resource.lifecycle),
        )
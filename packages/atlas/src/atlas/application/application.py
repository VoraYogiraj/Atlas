"""
Atlas Application Boundary

ENG-039 — Atlas UI Architecture
ENG-053 — Atlas Resource Move

Thin application boundary between UI interactions and the canonical
Atlas domain model.
"""

from __future__ import annotations

from typing import Any

from atlas.application.commands import AtlasCommand
from atlas.application.presentation import AtlasResourcePresentation
from atlas.application.queries import AtlasQuery
from atlas.core.aid import AtlasID
from atlas.core.spatial import AtlasSpatialPosition
from atlas.project.project import AtlasProject


class AtlasApplication:
    """
    Application boundary over an AtlasProject.

    This class intentionally remains thin. It does not replace
    AtlasProject or implement a second engineering model.
    """

    def __init__(self, project: AtlasProject) -> None:
        if not isinstance(
            project,
            AtlasProject,
        ):
            raise TypeError(
                "project must be an AtlasProject"
            )

        self._project = project

    @property
    def project(self) -> AtlasProject:
        """Return the canonical Atlas project."""
        return self._project

    def execute(
        self,
        command: AtlasCommand,
    ) -> Any:
        """
        Execute an application command.

        Commands represent application intent. Domain state is mutated
        through the canonical Project-owned domain structures.
        """
        if not isinstance(
            command,
            AtlasCommand,
        ):
            raise TypeError(
                "command must be an AtlasCommand"
            )

        if command.name == "noop":
            return None

        if command.name == "create_resource":
            classification = command.payload["classification"]
            name = command.payload.get(
                "name"
            )

            from atlas.classification.classification import (
                AtlasClassification,
            )
            from atlas.core.resource import AtlasResource

            if not isinstance(
                classification,
                AtlasClassification,
            ):
                raise TypeError(
                    "classification must be an AtlasClassification"
                )

            resource = AtlasResource(
                classification=classification,
                name=name,
            )

            # Project is the ownership boundary.
            # This also initializes the Resource's canonical spatial state.
            self._project.add_resource(
                resource
            )

            return resource

        if command.name == "move_resource":
            resource_id = command.payload.get(
                "resource_id"
            )

            if not isinstance(
                resource_id,
                AtlasID,
            ):
                raise TypeError(
                    "resource_id must be an AtlasID"
                )

            # Resolve the canonical Resource first.
            self._project.require_resource(
                resource_id
            )

            position = command.payload.get(
                "position"
            )

            if not isinstance(
                position,
                dict,
            ):
                raise TypeError(
                    "position must be a dictionary"
                )

            if set(position.keys()) != {
                "x",
                "y",
                "z",
            }:
                raise ValueError(
                    "position must contain exactly x, y, and z"
                )

            spatial_position = AtlasSpatialPosition(
                x=position["x"],
                y=position["y"],
                z=position["z"],
            )

            self._project.spatial_states.set_position(
                resource_id,
                spatial_position,
            )

            return spatial_position.as_mapping()

        raise NotImplementedError(
            f"Command '{command.name}' is not implemented"
        )

    def query(
        self,
        query: AtlasQuery,
    ) -> Any:
        """
        Execute an application query.

        The application boundary remains thin and delegates canonical
        state lookup to AtlasProject-owned structures.
        """
        if not isinstance(
            query,
            AtlasQuery,
        ):
            raise TypeError(
                "query must be an AtlasQuery"
            )

        if query.name == "get_project":
            return self._project

        if query.name == "get_resource_position":
            resource_id = query.parameters.get(
                "resource_id"
            )

            if not isinstance(
                resource_id,
                AtlasID,
            ):
                raise TypeError(
                    "resource_id must be an AtlasID"
                )

            # The Resource itself must exist.
            self._project.require_resource(
                resource_id
            )

            position = self._project.spatial_states.require_position(
                resource_id
            )

            return position.as_mapping()

        raise NotImplementedError(
            f"Query '{query.name}' is not implemented"
        )

    def present_resource(
        self,
        resource_id: object,
    ) -> AtlasResourcePresentation:
        """
        Build a presentation representation for a Resource.

        Resource lookup remains owned by the canonical Resource Registry.
        """
        if not isinstance(
            resource_id,
            AtlasID,
        ):
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
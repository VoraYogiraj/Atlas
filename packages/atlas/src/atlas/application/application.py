"""
Atlas Application Boundary

ENG-039 — Atlas UI Architecture
ENG-052 — Atlas Resource Create
ENG-053 — Atlas Resource Move
ENG-054 — Atlas Resource Rotate
ENG-055 — Atlas Resource Scale

Thin application boundary between UI interactions and the canonical
Atlas domain model.
"""

from __future__ import annotations

from typing import Any

from atlas.application.commands import AtlasCommand
from atlas.application.presentation import AtlasResourcePresentation
from atlas.application.queries import AtlasQuery
from atlas.core.aid import AtlasID
from atlas.core.spatial import (
    AtlasSpatialPosition,
    AtlasSpatialRotation,
    AtlasSpatialScale,
)
from atlas.project.project import AtlasProject


class AtlasApplication:
    """
    Application boundary over an AtlasProject.

    This class intentionally remains thin. It does not replace
    AtlasProject or implement a second engineering model.
    """

    def __init__(
        self,
        project: AtlasProject,
    ) -> None:
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

    # ------------------------------------------------------------------
    # Command Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        command: AtlasCommand,
    ) -> Any:
        """
        Execute an application command.

        Commands express intent. Canonical state remains owned by
        AtlasProject and its domain structures.
        """
        if not isinstance(
            command,
            AtlasCommand,
        ):
            raise TypeError(
                "command must be an AtlasCommand"
            )

        # --------------------------------------------------------------
        # ENG-039 — No-op
        # --------------------------------------------------------------

        if command.name == "noop":
            return None

        # --------------------------------------------------------------
        # ENG-052 — Resource Create
        # --------------------------------------------------------------

        if command.name == "create_resource":
            classification = command.payload.get(
                "classification"
            )

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

            # Preserve the completed ENG-052 creation contract.
            #
            # Resource Create registers directly in the canonical
            # Resource Registry and does not require the supplied
            # Classification to be pre-registered with the Project.
            self._project.resources.register(
                resource
            )

            # ENG-053 spatial initialization.
            self._project.spatial_states.set_position(
                resource.aid,
                AtlasSpatialPosition(
                    x=0.0,
                    y=0.0,
                    z=0.0,
                ),
            )

            # ENG-054 spatial initialization.
            self._project.spatial_states.set_rotation(
                resource.aid,
                AtlasSpatialRotation(
                    x=0.0,
                    y=0.0,
                    z=0.0,
                ),
            )

            # ENG-055 spatial initialization.
            #
            # Scale is dimensionless and neutral at Resource creation.
            self._project.spatial_states.set_scale(
                resource.aid,
                AtlasSpatialScale(
                    x=1.0,
                    y=1.0,
                    z=1.0,
                ),
            )

            return resource

        # --------------------------------------------------------------
        # ENG-053 — Resource Move
        # --------------------------------------------------------------

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

            # Validation is complete before mutation.
            self._project.spatial_states.set_position(
                resource_id,
                spatial_position,
            )

            return spatial_position.as_mapping()

        # --------------------------------------------------------------
        # ENG-054 — Resource Rotate
        # --------------------------------------------------------------

        if command.name == "rotate_resource":
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

            self._project.require_resource(
                resource_id
            )

            rotation = command.payload.get(
                "rotation"
            )

            if not isinstance(
                rotation,
                dict,
            ):
                raise TypeError(
                    "rotation must be a dictionary"
                )

            if set(rotation.keys()) != {
                "x",
                "y",
                "z",
            }:
                raise ValueError(
                    "rotation must contain exactly x, y, and z"
                )

            spatial_rotation = AtlasSpatialRotation(
                x=rotation["x"],
                y=rotation["y"],
                z=rotation["z"],
            )

            # Validation is complete before mutation.
            self._project.spatial_states.set_rotation(
                resource_id,
                spatial_rotation,
            )

            return spatial_rotation.as_mapping()

        # --------------------------------------------------------------
        # ENG-055 — Resource Scale
        # --------------------------------------------------------------

        if command.name == "scale_resource":
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

            self._project.require_resource(
                resource_id
            )

            scale = command.payload.get(
                "scale"
            )

            if not isinstance(
                scale,
                dict,
            ):
                raise TypeError(
                    "scale must be a dictionary"
                )

            if set(scale.keys()) != {
                "x",
                "y",
                "z",
            }:
                raise ValueError(
                    "scale must contain exactly x, y, and z"
                )

            spatial_scale = AtlasSpatialScale(
                x=scale["x"],
                y=scale["y"],
                z=scale["z"],
            )

            # Validation is complete before mutation.
            self._project.spatial_states.set_scale(
                resource_id,
                spatial_scale,
            )

            return spatial_scale.as_mapping()

        raise NotImplementedError(
            f"Command '{command.name}' is not implemented"
        )

    # ------------------------------------------------------------------
    # Query Execution
    # ------------------------------------------------------------------

    def query(
        self,
        query: AtlasQuery,
    ) -> Any:
        """
        Execute an application query.

        Canonical reads are delegated to the Project-owned state.
        """
        if not isinstance(
            query,
            AtlasQuery,
        ):
            raise TypeError(
                "query must be an AtlasQuery"
            )

        # --------------------------------------------------------------
        # ENG-039 — Project
        # --------------------------------------------------------------

        if query.name == "get_project":
            return self._project

        # --------------------------------------------------------------
        # ENG-053 — Resource Position
        # --------------------------------------------------------------

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

            self._project.require_resource(
                resource_id
            )

            position = (
                self._project.spatial_states.require_position(
                    resource_id
                )
            )

            return position.as_mapping()

        # --------------------------------------------------------------
        # ENG-054 — Resource Rotation
        # --------------------------------------------------------------

        if query.name == "get_resource_rotation":
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

            self._project.require_resource(
                resource_id
            )

            rotation = (
                self._project.spatial_states.require_rotation(
                    resource_id
                )
            )

            return rotation.as_mapping()

        # --------------------------------------------------------------
        # ENG-055 — Resource Scale
        # --------------------------------------------------------------

        if query.name == "get_resource_scale":
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

            self._project.require_resource(
                resource_id
            )

            scale = (
                self._project.spatial_states.require_scale(
                    resource_id
                )
            )

            return scale.as_mapping()

        raise NotImplementedError(
            f"Query '{query.name}' is not implemented"
        )

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

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
            properties=dict(
                resource.properties
            ),
            metadata=dict(
                resource.metadata
            ),
            lifecycle=str(
                resource.lifecycle
            ),
        )
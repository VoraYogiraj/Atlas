"""
Atlas JSON Serialization

Specification:
ENG-036 — Atlas JSON Serialization
"""

from __future__ import annotations

import json
from typing import Any

from atlas.categories.category import AtlasCategory
from atlas.classification.classification import (
    AtlasClassification,
)
from atlas.core.aid import AtlasID
from atlas.core.resource import AtlasResource
from atlas.lifecycle.lifecycle import AtlasLifecycle
from atlas.project.project import AtlasProject
from atlas.properties.property import AtlasProperty
from atlas.relationships.relationship import AtlasRelationship
from atlas.semantic_tags.tag import AtlasSemanticTag


class AtlasJSONSerializer:
    """
    Canonical JSON serializer for Atlas domain objects.

    ENG-036 intentionally operates only on the in-memory
    Atlas domain model.

    File persistence, import/export workflows, databases,
    provenance systems, and revision history are outside
    the scope of this serializer.
    """

    SERIALIZATION_VERSION = "0.1.0"
    ATLAS_VERSION = "0.1.0"

    @property
    def serialization_version(self) -> str:
        """Return the Atlas JSON serialization version."""
        return self.SERIALIZATION_VERSION

    @property
    def atlas_version(self) -> str:
        """Return the Atlas version represented by the serializer."""
        return self.ATLAS_VERSION

    # ------------------------------------------------------------------
    # Resource Serialization
    # ------------------------------------------------------------------

    def resource_to_dict(
        self,
        resource: AtlasResource,
    ) -> dict[str, Any]:
        """
        Serialize an AtlasResource into a JSON-compatible dictionary.

        Relationships are intentionally excluded from the Resource
        representation. Project-level serialization owns the canonical
        relationship collection so that endpoints can be represented
        by stable Atlas IDs rather than recursively serializing Resources.
        """
        if not isinstance(
            resource,
            AtlasResource,
        ):
            raise TypeError(
                "resource must be an AtlasResource"
            )

        return {
            "id": str(resource.aid),
            "classification": (
                resource.classification.id
            ),
            "name": resource.name,
            "properties": {
                property_id: self._property_to_dict(
                    property
                )
                for property_id, property
                in resource.properties.items()
            },
            "metadata": dict(
                resource.metadata
            ),
            "tags": [
                self._tag_to_dict(tag)
                for tag in resource.tags
            ],
            "categories": [
                self._category_to_dict(category)
                for category in resource.categories
            ],
            "lifecycle": resource.lifecycle.value,
        }

    def resource_from_dict(
        self,
        data: dict[str, Any],
    ) -> AtlasResource:
        """
        Reconstruct an AtlasResource from a resource dictionary.

        This method is primarily intended for resource-level
        serialization tests and isolated resource reconstruction.

        A classification embedded in the payload is reconstructed
        directly when necessary.
        """
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "resource data must be a dictionary"
            )

        resource_id = self._require_string(
            data,
            "id",
        )

        classification_data = data.get(
            "classification"
        )

        classification = (
            self._classification_from_value(
                classification_data
            )
        )

        resource = AtlasResource(
            classification=classification,
            name=data.get("name"),
        )

        self._set_resource_identity(
            resource,
            resource_id,
        )

        properties = data.get(
            "properties",
            {},
        )

        if not isinstance(
            properties,
            dict,
        ):
            raise ValueError(
                "resource properties must be a dictionary"
            )

        for property_data in properties.values():
            resource.set_property(
                self._property_from_dict(
                    property_data
                )
            )

        metadata = data.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "resource metadata must be a dictionary"
            )

        resource.metadata.update(
            metadata
        )

        tags = data.get(
            "tags",
            [],
        )

        if not isinstance(
            tags,
            list,
        ):
            raise ValueError(
                "resource tags must be a list"
            )

        for tag_data in tags:
            resource.add_tag(
                self._tag_from_dict(
                    tag_data
                )
            )

        categories = data.get(
            "categories",
            [],
        )

        if not isinstance(
            categories,
            list,
        ):
            raise ValueError(
                "resource categories must be a list"
            )

        for category_data in categories:
            resource.add_category(
                self._category_from_dict(
                    category_data
                )
            )

        lifecycle_value = data.get(
            "lifecycle",
            AtlasLifecycle.CREATED.value,
        )

        self._restore_lifecycle(
            resource,
            lifecycle_value,
        )

        return resource

    # ------------------------------------------------------------------
    # Project Serialization
    # ------------------------------------------------------------------

    def project_to_dict(
        self,
        project: AtlasProject,
    ) -> dict[str, Any]:
        """
        Serialize an AtlasProject into the canonical ENG-036 envelope.
        """
        if not isinstance(
            project,
            AtlasProject,
        ):
            raise TypeError(
                "project must be an AtlasProject"
            )

        classifications = [
            self._classification_to_dict(
                classification
            )
            for classification in project.classifications
        ]

        resources = [
            self.resource_to_dict(
                resource
            )
            for resource in project.resources
        ]

        relationships = [
            self._relationship_to_dict(
                relationship
            )
            for relationship in project.graph
        ]

        return {
            "atlas": {
                "serialization_version": (
                    self.serialization_version
                ),
                "atlas_version": (
                    self.atlas_version
                ),
            },
            "project": {
                "id": str(project.aid),
                "name": project.name,
                "metadata": dict(
                    project.metadata
                ),
                "classifications": classifications,
                "resources": resources,
                "relationships": relationships,
            },
        }

    def project_from_dict(
        self,
        data: dict[str, Any],
    ) -> AtlasProject:
        """
        Reconstruct an AtlasProject from a canonical ENG-036 dictionary.
        """
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "project data must be a dictionary"
            )

        atlas = data.get(
            "atlas"
        )

        if not isinstance(
            atlas,
            dict,
        ):
            raise ValueError(
                "atlas section is required"
            )

        project_data = data.get(
            "project"
        )

        if not isinstance(
            project_data,
            dict,
        ):
            raise ValueError(
                "project section is required"
            )

        serialization_version = atlas.get(
            "serialization_version"
        )

        if not isinstance(
            serialization_version,
            str,
        ) or not serialization_version.strip():
            raise ValueError(
                "serialization_version is required"
            )

        name = project_data.get(
            "name"
        )

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ValueError(
                "project name is required"
            )

        metadata = project_data.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "project metadata must be a dictionary"
            )

        project = AtlasProject(
            name=name,
            metadata=dict(
                metadata
            ),
        )

        project_id = project_data.get(
            "id"
        )

        if project_id is None:
            raise ValueError(
                "project id is required"
            )

        self._set_project_identity(
            project,
            project_id,
        )

        classifications_data = project_data.get(
            "classifications",
            [],
        )

        if not isinstance(
            classifications_data,
            list,
        ):
            raise ValueError(
                "project classifications must be a list"
            )

        classifications = (
            self._restore_classifications(
                classifications_data
            )
        )

        for classification in classifications:
            project.add_classification(
                classification
            )

        resources_data = project_data.get(
            "resources",
            [],
        )

        if not isinstance(
            resources_data,
            list,
        ):
            raise ValueError(
                "project resources must be a list"
            )

        resources_by_id: dict[
            str,
            AtlasResource,
        ] = {}

        for resource_data in resources_data:
            if not isinstance(
                resource_data,
                dict,
            ):
                raise ValueError(
                    "resource entry must be a dictionary"
                )

            resource = (
                self._resource_from_project_dict(
                    resource_data,
                    project.classification_registry,
                )
            )

            project.add_resource(
                resource
            )

            resource_id = str(
                resource.aid
            )

            if resource_id in resources_by_id:
                raise ValueError(
                    "Duplicate Resource ID: "
                    f"{resource_id}"
                )

            resources_by_id[
                resource_id
            ] = resource

        relationships_data = project_data.get(
            "relationships",
            [],
        )

        if not isinstance(
            relationships_data,
            list,
        ):
            raise ValueError(
                "project relationships must be a list"
            )

        for relationship_data in relationships_data:
            relationship = (
                self._relationship_from_dict(
                    relationship_data,
                    resources_by_id,
                )
            )

            project.add_relationship(
                relationship
            )

        return project

    # ------------------------------------------------------------------
    # JSON Text
    # ------------------------------------------------------------------

    def dumps(
        self,
        project: AtlasProject,
    ) -> str:
        """
        Serialize an AtlasProject into deterministic JSON text.
        """
        data = self.project_to_dict(
            project
        )

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )

    def loads(
        self,
        text: str,
    ) -> AtlasProject:
        """
        Deserialize an AtlasProject from JSON text.
        """
        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text must be a string"
            )

        try:
            data = json.loads(
                text
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid JSON text"
            ) from exc

        return self.project_from_dict(
            data
        )

    # ------------------------------------------------------------------
    # Primitive Serializers
    # ------------------------------------------------------------------

    @staticmethod
    def _property_to_dict(
        property: AtlasProperty,
    ) -> dict[str, Any]:
        return {
            "id": property.id,
            "name": property.name,
            "value": property.value,
            "data_type": property.data_type,
            "unit": property.unit,
            "description": property.description,
            "required": property.required,
        }

    @staticmethod
    def _property_from_dict(
        data: dict[str, Any],
    ) -> AtlasProperty:
        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "property entry must be a dictionary"
            )

        return AtlasProperty(
            id=data["id"],
            name=data["name"],
            value=data.get("value"),
            data_type=data["data_type"],
            unit=data.get("unit"),
            description=data.get(
                "description",
                "",
            ),
            required=data.get(
                "required",
                False,
            ),
        )

    @staticmethod
    def _tag_to_dict(
        tag: AtlasSemanticTag,
    ) -> dict[str, str]:
        return {
            "id": tag.id,
            "name": tag.name,
            "description": tag.description,
        }

    @staticmethod
    def _tag_from_dict(
        data: dict[str, Any],
    ) -> AtlasSemanticTag:
        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "tag entry must be a dictionary"
            )

        return AtlasSemanticTag(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description",
                "",
            ),
        )

    @staticmethod
    def _category_to_dict(
        category: AtlasCategory,
    ) -> dict[str, str]:
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
        }

    @staticmethod
    def _category_from_dict(
        data: dict[str, Any],
    ) -> AtlasCategory:
        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "category entry must be a dictionary"
            )

        return AtlasCategory(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description",
                "",
            ),
        )

    @staticmethod
    def _classification_to_dict(
        classification: AtlasClassification,
    ) -> dict[str, Any]:
        return {
            "id": classification.id,
            "name": classification.name,
            "description": classification.description,
            "parent": (
                classification.parent.id
                if classification.parent
                is not None
                else None
            ),
        }

    @staticmethod
    def _relationship_to_dict(
        relationship: AtlasRelationship,
    ) -> dict[str, str]:
        return {
            "id": relationship.id,
            "relationship_type": (
                relationship.relationship_type
            ),
            "source": str(
                relationship.source.aid
            ),
            "target": str(
                relationship.target.aid
            ),
            "description": (
                relationship.description
            ),
        }

    # ------------------------------------------------------------------
    # Classification Reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _restore_classifications(
        items: list[dict[str, Any]],
    ) -> list[AtlasClassification]:
        """
        Reconstruct classifications in parent-safe order.

        Parent references are represented by IDs, so a classification
        may be defined before or after its parent in the serialized
        source. Reconstruction therefore resolves them iteratively.
        """
        pending = [
            dict(item)
            for item in items
        ]

        restored: dict[
            str,
            AtlasClassification,
        ] = {}

        while pending:
            progress = False

            remaining: list[
                dict[str, Any]
            ] = []

            for item in pending:
                classification_id = item.get(
                    "id"
                )

                if not isinstance(
                    classification_id,
                    str,
                ) or not classification_id.strip():
                    raise ValueError(
                        "classification id is required"
                    )

                parent_id = item.get(
                    "parent"
                )

                if parent_id is None:
                    parent = None
                else:
                    parent = restored.get(
                        parent_id
                    )

                    if parent is None:
                        remaining.append(
                            item
                        )
                        continue

                restored[
                    classification_id
                ] = AtlasClassification(
                    id=classification_id,
                    name=item["name"],
                    description=item.get(
                        "description",
                        "",
                    ),
                    parent=parent,
                )

                progress = True

            if not progress:
                raise ValueError(
                    "Unable to resolve classification hierarchy"
                )

            pending = remaining

        return list(
            restored.values()
        )

    @staticmethod
    def _classification_from_value(
        value: Any,
    ) -> AtlasClassification:
        """
        Reconstruct an isolated Resource classification.

        Resource-level serialization stores the classification ID.
        Since isolated Resource reconstruction has no Project
        classification registry, this creates a minimal classification
        placeholder preserving the canonical classification identity.
        """
        if isinstance(
            value,
            str,
        ):
            return AtlasClassification(
                id=value,
                name=value,
            )

        if isinstance(
            value,
            dict,
        ):
            return AtlasClassification(
                id=value["id"],
                name=value["name"],
                description=value.get(
                    "description",
                    "",
                ),
            )

        raise ValueError(
            "resource classification is required"
        )

    # ------------------------------------------------------------------
    # Project Resource Reconstruction
    # ------------------------------------------------------------------

    def _resource_from_project_dict(
        self,
        data: dict[str, Any],
        classification_registry: Any,
    ) -> AtlasResource:
        classification_id = data.get(
            "classification"
        )

        if not isinstance(
            classification_id,
            str,
        ) or not classification_id.strip():
            raise ValueError(
                "resource classification is required"
            )

        classification = (
            classification_registry.get(
                classification_id
            )
        )

        if classification is None:
            raise ValueError(
                "Unknown Resource classification: "
                f"{classification_id}"
            )

        resource = AtlasResource(
            classification=classification,
            name=data.get("name"),
        )

        resource_id = data.get(
            "id"
        )

        if not isinstance(
            resource_id,
            str,
        ) or not resource_id.strip():
            raise ValueError(
                "resource id is required"
            )

        self._set_resource_identity(
            resource,
            resource_id,
        )

        properties = data.get(
            "properties",
            {},
        )

        if not isinstance(
            properties,
            dict,
        ):
            raise ValueError(
                "resource properties must be a dictionary"
            )

        for property_data in properties.values():
            resource.set_property(
                self._property_from_dict(
                    property_data
                )
            )

        metadata = data.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "resource metadata must be a dictionary"
            )

        resource.metadata.update(
            metadata
        )

        tags = data.get(
            "tags",
            [],
        )

        if not isinstance(
            tags,
            list,
        ):
            raise ValueError(
                "resource tags must be a list"
            )

        for tag_data in tags:
            resource.add_tag(
                self._tag_from_dict(
                    tag_data
                )
            )

        categories = data.get(
            "categories",
            [],
        )

        if not isinstance(
            categories,
            list,
        ):
            raise ValueError(
                "resource categories must be a list"
            )

        for category_data in categories:
            resource.add_category(
                self._category_from_dict(
                    category_data
                )
            )

        self._restore_lifecycle(
            resource,
            data.get(
                "lifecycle",
                AtlasLifecycle.CREATED.value,
            ),
        )

        return resource

    # ------------------------------------------------------------------
    # Relationship Reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _relationship_from_dict(
        data: dict[str, Any],
        resources_by_id: dict[
            str,
            AtlasResource,
        ],
    ) -> AtlasRelationship:
        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "relationship entry must be a dictionary"
            )

        source_id = data.get(
            "source"
        )

        target_id = data.get(
            "target"
        )

        source = resources_by_id.get(
            source_id
        )

        target = resources_by_id.get(
            target_id
        )

        if source is None:
            raise ValueError(
                "Unknown relationship source Resource: "
                f"{source_id}"
            )

        if target is None:
            raise ValueError(
                "Unknown relationship target Resource: "
                f"{target_id}"
            )

        return AtlasRelationship(
            id=data["id"],
            relationship_type=data[
                "relationship_type"
            ],
            source=source,
            target=target,
            description=data.get(
                "description",
                "",
            ),
        )

    # ------------------------------------------------------------------
    # Lifecycle Reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _restore_lifecycle(
        resource: AtlasResource,
        lifecycle_value: str,
    ) -> None:
        try:
            target = AtlasLifecycle(
                lifecycle_value
            )
        except ValueError as exc:
            raise ValueError(
                "Unknown lifecycle value: "
                f"{lifecycle_value}"
            ) from exc

        if target is AtlasLifecycle.CREATED:
            return

        transitions = {
            AtlasLifecycle.ACTIVE: (
                resource.activate,
            ),
            AtlasLifecycle.ARCHIVED: (
                resource.activate,
                resource.archive,
            ),
            AtlasLifecycle.DELETED: (
                resource.activate,
                resource.delete,
            ),
        }

        try:
            operations = transitions[
                target
            ]
        except KeyError as exc:
            raise ValueError(
                "Unsupported lifecycle value: "
                f"{lifecycle_value}"
            ) from exc

        for operation in operations:
            operation()

    # ------------------------------------------------------------------
    # Identity Restoration
    # ------------------------------------------------------------------

    @staticmethod
    def _set_resource_identity(
        resource: AtlasResource,
        value: str,
    ) -> None:
        try:
            resource._id = AtlasID.from_string(
                value
            )
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as exc:
            raise ValueError(
                f"Invalid Resource AtlasID: {value}"
            ) from exc

    @staticmethod
    def _set_project_identity(
        project: AtlasProject,
        value: str,
    ) -> None:
        try:
            project._aid = AtlasID.from_string(
                value
            )
        except (
            AttributeError,
            ValueError,
            TypeError,
        ) as exc:
            raise ValueError(
                f"Invalid Project AtlasID: {value}"
            ) from exc

    # ------------------------------------------------------------------
    # Validation Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_string(
        data: dict[str, Any],
        key: str,
    ) -> str:
        value = data.get(
            key
        )

        if not isinstance(
            value,
            str,
        ) or not value.strip():
            raise ValueError(
                f"{key} is required"
            )

        return value
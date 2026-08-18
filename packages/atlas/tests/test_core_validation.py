"""
ENG-058 — Atlas Core Validation Baseline

Focused RED tests for the Phase 12 validation baseline.

These tests validate cross-capability architectural invariants established
through Phase 11.

RED-phase rules:
- Do not modify production code.
- Do not introduce a new validation engine.
- Do not introduce a second Resource model.
- Do not introduce a second Registry, Graph, or Spatial State system.
- Tests must exercise the existing canonical Atlas APIs.
"""

from __future__ import annotations

import pytest

from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.project.project import AtlasProject
from atlas.resource_registry import AtlasResourceRegistry
from atlas.validation.engine import AtlasValidationEngine


def _project_with_resource() -> tuple[AtlasProject, AtlasResource]:
    """Create a minimal canonical project containing one Resource."""
    project = AtlasProject(name="ENG-058 Validation Test Project")

    classification = AtlasClassification(
        id="wall",
        name="Wall",
    )
    project.add_classification(classification)

    resource = AtlasResource(
        classification=classification,
        name="Wall-01",
    )
    project.add_resource(resource)

    return project, resource


# ============================================================================
# 1. RESOURCE REGISTRY VALIDATION BOUNDARY
# ============================================================================


class TestResourceRegistryValidationBoundary:
    def test_register_rejects_non_resource(self) -> None:
        """
        The canonical Resource Registry must reject an object that is not
        an AtlasResource.

        RED expectation:
        The current implementation is expected to fail this contract because
        invalid objects reach AtlasID access before explicit type validation.
        """
        registry = AtlasResourceRegistry()

        with pytest.raises(TypeError):
            registry.register(object())  # type: ignore[arg-type]

        # Invalid registration must not create canonical membership.
        assert registry.count == 0


# ============================================================================
# 2. RELATIONSHIP GRAPH VALIDATION BOUNDARY
# ============================================================================


class TestRelationshipGraphValidationBoundary:
    def test_add_relationship_rejects_non_relationship(self) -> None:
        """
        The canonical Relationship Graph must reject an object that is not
        an AtlasRelationship.

        Invalid relationship insertion must not mutate graph state.
        """
        project, _resource = _project_with_resource()

        with pytest.raises(TypeError):
            project.graph.add_relationship(object())  # type: ignore[arg-type]

        assert project.relationship_count == 0

    def test_for_resource_rejects_non_resource(self) -> None:
        """
        Resource-specific graph lookup must reject an object that is not an
        AtlasResource.

        Invalid lookup must not mutate graph state.
        """
        project, _resource = _project_with_resource()

        with pytest.raises(TypeError):
            project.graph.for_resource(object())  # type: ignore[arg-type]

        assert project.relationship_count == 0


# ============================================================================
# 3. VALIDATION ENGINE VALIDATION BOUNDARY
# ============================================================================


class TestValidationEngineBoundary:
    def test_validate_rejects_non_resource(self) -> None:
        """
        The canonical Validation Engine must reject an object that is not
        an AtlasResource.
        """
        engine = AtlasValidationEngine()

        with pytest.raises(TypeError):
            engine.validate(object())  # type: ignore[arg-type]

    def test_validate_does_not_mutate_resource(self) -> None:
        """
        Validation must be observational.

        Running validation must not mutate canonical Resource state.
        """
        _project, resource = _project_with_resource()

        engine = AtlasValidationEngine()

        before = {
            "aid": resource.aid,
            "name": resource.name,
            "classification": resource.classification,
            "properties": dict(resource.properties),
            "tags": list(resource.tags),
            "categories": list(resource.categories),
            "lifecycle": resource.lifecycle,
        }

        engine.validate(resource)

        assert resource.aid == before["aid"]
        assert resource.name == before["name"]
        assert resource.classification is before["classification"]
        assert resource.properties == before["properties"]
        assert resource.tags == before["tags"]
        assert resource.categories == before["categories"]
        assert resource.lifecycle == before["lifecycle"]
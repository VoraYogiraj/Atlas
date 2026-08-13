"""
ENG-038 — Atlas Import / Export

RED test suite.

Defines the generic adapter boundary for external representations.

No concrete format such as IFC, CAD, Revit, CSV, or PDF is implemented
by ENG-038 itself.
"""

from __future__ import annotations

import pytest

from atlas.classification.classification import AtlasClassification
from atlas.core.resource import AtlasResource
from atlas.exchange.exporter import AtlasExporter
from atlas.exchange.importer import AtlasImporter
from atlas.exchange.result import (
    AtlasExportResult,
    AtlasImportResult,
)
from atlas.project.project import AtlasProject


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------


class DummyImporter(AtlasImporter):
    """Minimal importer implementation for contract testing."""

    format_id = "dummy"
    name = "Dummy Importer"

    @property
    def capabilities(self) -> frozenset[str]:
        return frozenset(
            {
                "import",
                "resources",
                "relationships",
            }
        )

    def import_data(
        self,
        source,
    ) -> AtlasImportResult:
        project = AtlasProject(
            name="Imported Project"
        )

        return AtlasImportResult(
            project=project
        )


class DummyExporter(AtlasExporter):
    """Minimal exporter implementation for contract testing."""

    format_id = "dummy"
    name = "Dummy Exporter"

    @property
    def capabilities(self) -> frozenset[str]:
        return frozenset(
            {
                "export",
                "resources",
                "relationships",
            }
        )

    def export_data(
        self,
        project: AtlasProject,
    ) -> AtlasExportResult:
        return AtlasExportResult(
            representation={
                "project_name": project.name
            }
        )


def create_project() -> AtlasProject:
    """Create a valid AtlasProject for exchange tests."""
    classification = AtlasClassification(
        id="building-element",
        name="Building Element",
    )

    project = AtlasProject(
        name="Atlas Import Export Test"
    )

    project.add_classification(
        classification
    )

    project.add_resource(
        AtlasResource(
            classification=classification,
            name="Wall A",
        )
    )

    return project


# ---------------------------------------------------------------------------
# Importer Contract
# ---------------------------------------------------------------------------


def test_importer_can_be_instantiated():
    importer = DummyImporter()

    assert importer is not None


def test_importer_exposes_format_id():
    importer = DummyImporter()

    assert importer.format_id == "dummy"


def test_importer_exposes_name():
    importer = DummyImporter()

    assert importer.name == "Dummy Importer"


def test_importer_exposes_capabilities():
    importer = DummyImporter()

    assert importer.capabilities == frozenset(
        {
            "import",
            "resources",
            "relationships",
        }
    )


def test_importer_capabilities_are_immutable():
    importer = DummyImporter()

    with pytest.raises(
        AttributeError
    ):
        importer.capabilities.add(
            "geometry"
        )


def test_importer_imports_external_data():
    importer = DummyImporter()

    result = importer.import_data(
        "dummy-input"
    )

    assert isinstance(
        result,
        AtlasImportResult,
    )

    assert isinstance(
        result.project,
        AtlasProject,
    )


def test_import_result_contains_project():
    importer = DummyImporter()

    result = importer.import_data(
        "dummy-input"
    )

    assert result.project.name == (
        "Imported Project"
    )


# ---------------------------------------------------------------------------
# Exporter Contract
# ---------------------------------------------------------------------------


def test_exporter_can_be_instantiated():
    exporter = DummyExporter()

    assert exporter is not None


def test_exporter_exposes_format_id():
    exporter = DummyExporter()

    assert exporter.format_id == "dummy"


def test_exporter_exposes_name():
    exporter = DummyExporter()

    assert exporter.name == "Dummy Exporter"


def test_exporter_exposes_capabilities():
    exporter = DummyExporter()

    assert exporter.capabilities == frozenset(
        {
            "export",
            "resources",
            "relationships",
        }
    )


def test_exporter_capabilities_are_immutable():
    exporter = DummyExporter()

    with pytest.raises(
        AttributeError
    ):
        exporter.capabilities.add(
            "geometry"
        )


def test_exporter_exports_project():
    project = create_project()
    exporter = DummyExporter()

    result = exporter.export_data(
        project
    )

    assert isinstance(
        result,
        AtlasExportResult,
    )


def test_export_result_contains_representation():
    project = create_project()
    exporter = DummyExporter()

    result = exporter.export_data(
        project
    )

    assert result.representation == {
        "project_name": "Atlas Import Export Test"
    }


# ---------------------------------------------------------------------------
# Result Contracts
# ---------------------------------------------------------------------------


def test_import_result_supports_warnings():
    result = AtlasImportResult(
        project=AtlasProject(
            name="Imported"
        ),
        warnings=[
            "Unsupported property"
        ],
    )

    assert result.warnings == [
        "Unsupported property"
    ]


def test_import_result_supports_errors():
    result = AtlasImportResult(
        project=AtlasProject(
            name="Imported"
        ),
        errors=[
            "Conversion failure"
        ],
    )

    assert result.errors == [
        "Conversion failure"
    ]


def test_export_result_supports_warnings():
    result = AtlasExportResult(
        representation={},
        warnings=[
            "Unsupported category"
        ],
    )

    assert result.warnings == [
        "Unsupported category"
    ]


def test_export_result_supports_errors():
    result = AtlasExportResult(
        representation={},
        errors=[
            "Conversion failure"
        ],
    )

    assert result.errors == [
        "Conversion failure"
    ]


# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------


def test_importer_rejects_invalid_format_id():
    class InvalidImporter(AtlasImporter):
        format_id = ""
        name = "Invalid Importer"

        @property
        def capabilities(self) -> frozenset[str]:
            return frozenset()

        def import_data(
            self,
            source,
        ) -> AtlasImportResult:
            raise NotImplementedError

    with pytest.raises(
        ValueError
    ):
        InvalidImporter()


def test_exporter_rejects_invalid_format_id():
    class InvalidExporter(AtlasExporter):
        format_id = ""
        name = "Invalid Exporter"

        @property
        def capabilities(self) -> frozenset[str]:
            return frozenset()

        def export_data(
            self,
            project: AtlasProject,
        ) -> AtlasExportResult:
            raise NotImplementedError

    with pytest.raises(
        ValueError
    ):
        InvalidExporter()


def test_importer_rejects_invalid_name():
    class InvalidImporter(AtlasImporter):
        format_id = "invalid"
        name = ""

        @property
        def capabilities(self) -> frozenset[str]:
            return frozenset()

        def import_data(
            self,
            source,
        ) -> AtlasImportResult:
            raise NotImplementedError

    with pytest.raises(
        ValueError
    ):
        InvalidImporter()


def test_exporter_rejects_invalid_name():
    class InvalidExporter(AtlasExporter):
        format_id = "invalid"
        name = ""

        @property
        def capabilities(self) -> frozenset[str]:
            return frozenset()

        def export_data(
            self,
            project: AtlasProject,
        ) -> AtlasExportResult:
            raise NotImplementedError

    with pytest.raises(
        ValueError
    ):
        InvalidExporter()


# ---------------------------------------------------------------------------
# Export Source Immutability
# ---------------------------------------------------------------------------


def test_export_does_not_modify_source_project():
    project = create_project()

    original_id = project.aid
    original_name = project.name
    original_metadata = dict(
        project.metadata
    )
    original_resource_count = (
        project.resource_count
    )

    exporter = DummyExporter()

    exporter.export_data(
        project
    )

    assert project.aid == original_id
    assert project.name == original_name
    assert project.metadata == original_metadata
    assert project.resource_count == (
        original_resource_count
    )


# ---------------------------------------------------------------------------
# Import Produces New Project
# ---------------------------------------------------------------------------


def test_import_produces_new_project_instance():
    importer = DummyImporter()

    result = importer.import_data(
        "external-data"
    )

    assert result.project is not None

    assert isinstance(
        result.project,
        AtlasProject,
    )


# ---------------------------------------------------------------------------
# Adapter Independence
# ---------------------------------------------------------------------------


def test_importer_does_not_require_specific_external_format_type():
    importer = DummyImporter()

    result = importer.import_data(
        {
            "anything": "accepted by adapter"
        }
    )

    assert isinstance(
        result.project,
        AtlasProject,
    )


def test_exporter_accepts_canonical_atlas_project():
    project = create_project()
    exporter = DummyExporter()

    result = exporter.export_data(
        project
    )

    assert result.representation[
        "project_name"
    ] == project.name
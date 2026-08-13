"""
Atlas Import / Export Results

Specification:
ENG-038 — Atlas Import / Export
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from atlas.project.project import AtlasProject


@dataclass(slots=True)
class AtlasImportResult:
    """
    Result of an Atlas import operation.

    `project` is the canonical Atlas result.
    Warnings and errors provide structured adapter feedback.
    """

    project: AtlasProject
    warnings: list[str] = field(
        default_factory=list
    )
    errors: list[str] = field(
        default_factory=list
    )


@dataclass(slots=True)
class AtlasExportResult:
    """
    Result of an Atlas export operation.

    `representation` contains the external-format representation.
    Warnings and errors provide structured adapter feedback.
    """

    representation: Any
    warnings: list[str] = field(
        default_factory=list
    )
    errors: list[str] = field(
        default_factory=list
    )
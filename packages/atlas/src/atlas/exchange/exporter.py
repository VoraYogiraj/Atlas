"""
Atlas Exporter Contract

Specification:
ENG-038 — Atlas Import / Export
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from atlas.exchange.result import AtlasExportResult
from atlas.project.project import AtlasProject


class AtlasExporter(ABC):
    """
    Abstract contract for exporting Atlas projects into
    external representations.

    Concrete format adapters should inherit from this class.
    """

    format_id: str
    name: str

    def __init__(self) -> None:
        format_id = getattr(
            self,
            "format_id",
            None,
        )

        name = getattr(
            self,
            "name",
            None,
        )

        if not isinstance(
            format_id,
            str,
        ) or not format_id.strip():
            raise ValueError(
                "Exporter format_id cannot be empty"
            )

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ValueError(
                "Exporter name cannot be empty"
            )

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[str]:
        """
        Return the immutable set of capabilities supported by the exporter.
        """
        raise NotImplementedError

    @abstractmethod
    def export_data(
        self,
        project: AtlasProject,
    ) -> AtlasExportResult:
        """
        Export an AtlasProject into an external representation.
        """
        raise NotImplementedError
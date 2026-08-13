"""
Atlas Importer Contract

Specification:
ENG-038 — Atlas Import / Export
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from atlas.exchange.result import AtlasImportResult


class AtlasImporter(ABC):
    """
    Abstract contract for importing external representations into Atlas.

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
                "Importer format_id cannot be empty"
            )

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ValueError(
                "Importer name cannot be empty"
            )

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[str]:
        """
        Return the immutable set of capabilities supported by the importer.
        """
        raise NotImplementedError

    @abstractmethod
    def import_data(
        self,
        source: Any,
    ) -> AtlasImportResult:
        """
        Import an external representation into Atlas.
        """
        raise NotImplementedError
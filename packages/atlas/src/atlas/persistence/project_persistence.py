"""
Atlas Project Persistence

Specification:
ENG-037 — Project Save / Load
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from atlas.project.project import AtlasProject
from atlas.serialization.json_serializer import AtlasJSONSerializer


class AtlasProjectPersistence:
    """
    Filesystem persistence boundary for AtlasProject.

    ENG-037 delegates Atlas representation and reconstruction
    entirely to AtlasJSONSerializer.

    This class is responsible only for:

    - file path handling
    - UTF-8 file I/O
    - overwrite protection
    - filesystem error propagation
    """

    def __init__(
        self,
        *,
        serializer: AtlasJSONSerializer | None = None,
    ) -> None:
        self._serializer = (
            serializer
            if serializer is not None
            else AtlasJSONSerializer()
        )

    @property
    def serializer(self) -> AtlasJSONSerializer:
        """Return the serializer used by this persistence layer."""
        return self._serializer

    def save(
        self,
        project: AtlasProject,
        path: str | PathLike[str],
        *,
        overwrite: bool = False,
    ) -> Path:
        """
        Save an AtlasProject to a UTF-8 JSON file.

        Existing files are protected unless overwrite=True.

        Returns
        -------
        Path
            The exact path written.
        """
        if not isinstance(
            project,
            AtlasProject,
        ):
            raise TypeError(
                "project must be an AtlasProject"
            )

        target = self._coerce_path(path)

        if target.exists():
            if target.is_dir():
                raise IsADirectoryError(
                    target
                )

            if not overwrite:
                raise FileExistsError(
                    target
                )

        # Serialize before opening the file.
        # This prevents a serialization failure from truncating
        # an existing file.
        text = self._serializer.dumps(
            project
        )

        # Parent directory creation is intentionally not performed.
        # The caller must provide an existing parent directory.
        with target.open(
            "w",
            encoding="utf-8",
            newline="\n",
        ) as file:
            file.write(text)
            file.write("\n")

        return target

    def load(
        self,
        path: str | PathLike[str],
    ) -> AtlasProject:
        """
        Load an AtlasProject from a UTF-8 JSON file.

        Returns
        -------
        AtlasProject
            A newly reconstructed project instance.
        """
        target = self._coerce_path(path)

        if target.is_dir():
            raise IsADirectoryError(
                target
            )

        text = target.read_text(
            encoding="utf-8"
        )

        return self._serializer.loads(
            text
        )

    @staticmethod
    def _coerce_path(
        path: str | PathLike[str],
    ) -> Path:
        """
        Convert a supported filesystem path value to pathlib.Path.
        """
        if path is None:
            raise TypeError(
                "path must be a str or path-like object"
            )

        if not isinstance(
            path,
            (str, PathLike),
        ):
            raise TypeError(
                "path must be a str or path-like object"
            )

        if isinstance(
            path,
            str,
        ) and not path.strip():
            raise ValueError(
                "path cannot be empty"
            )

        return Path(path)
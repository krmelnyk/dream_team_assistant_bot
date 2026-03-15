"""JSON persistence adapters."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Generic, Protocol, TypeVar

from ..domain.exceptions import StorageError


T = TypeVar("T")


class Reader(Protocol[T]):
    """Converts raw JSON-compatible data into a domain object."""

    def __call__(self, payload: Any) -> T:
        ...


class Writer(Protocol[T]):
    """Converts a domain object into JSON-compatible data."""

    def __call__(self, value: T) -> Any:
        ...


def read_json(path: str | Path, default: Any = None) -> Any:
    """Read JSON from disk, returning default for missing or empty files."""

    file_path = Path(path)

    if not file_path.exists():
        return default

    if file_path.stat().st_size == 0:
        return default

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Invalid JSON in '{file_path.name}'. "
            "Please fix or remove the file."
        ) from error
    except OSError as error:
        raise StorageError(
            f"Unable to read data file '{file_path.name}'."
        ) from error


def write_json(path: str | Path, payload: Any) -> None:
    """Persist JSON to disk using atomic replace."""

    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write into a temporary file first to avoid leaving a half-written
        # JSON file behind if the process is interrupted.
        temp_path = file_path.with_name(f".{file_path.name}.tmp")

        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

        os.replace(temp_path, file_path)
    except OSError as error:
        raise StorageError(
            f"Unable to write data file '{file_path.name}'."
        ) from error


class JsonFileStorage(Generic[T]):
    """File-backed JSON storage with pluggable encode/decode functions."""

    def __init__(
        self,
        path: str | Path,
        *,
        decoder: Reader[T],
        encoder: Writer[T],
        default_factory: Callable[[], T],
    ) -> None:
        self._path = Path(path)
        self._decoder = decoder
        self._encoder = encoder
        self._default_factory = default_factory

    @property
    def path(self) -> Path:
        return self._path

    def read(self) -> T:
        payload = read_json(self._path, default=None)
        if payload is None:
            return self._default_factory()
        return self._decoder(payload)

    def write(self, value: T) -> None:
        payload = self._encoder(value)
        write_json(self._path, payload)

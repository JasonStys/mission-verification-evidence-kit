"""Bounded, duplicate-safe JSON and atomic file operations. Created by Jason Stys."""
# Vendored/adapted from secure-delivery-pipeline-lab; exact lines: docs/CODE_INDEX.md.

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any

MAX_FILE = 2 * 1024 * 1024


class Rejected(ValueError):
    """A trust, format, or resource boundary failed; callers must not promote."""


def read_bytes(path: Path, limit: int = MAX_FILE) -> bytes:
    """Read one regular, non-link file up to limit bytes; never follow a final symlink."""
    if path.is_symlink() or path.is_junction():
        raise Rejected("links are not accepted")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise Rejected("file type is not accepted")
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise Rejected("file type or size is not accepted")
            data = stream.read(limit + 1)
    except OSError as error:
        raise Rejected("required file could not be read") from error
    if len(data) > limit:
        raise Rejected("file exceeds the byte limit")
    return data


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys instead of allowing a later value to override policy."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    """Reject nonstandard JSON NaN/Infinity; value is intentionally not echoed."""
    raise Rejected("non-finite JSON number")


def load_json(path: Path, limit: int = MAX_FILE) -> Any:
    """Decode bounded UTF-8 JSON with duplicate keys and non-finite values rejected."""
    try:
        return json.loads(
            read_bytes(path, limit),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise Rejected("invalid JSON document") from error


def canonical(value: Any) -> bytes:
    """Encode deterministic finite JSON for manifests and atomic state updates."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def atomic_write(path: Path, data: bytes) -> None:
    """Flush a same-directory temporary file, then atomically replace the destination."""
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

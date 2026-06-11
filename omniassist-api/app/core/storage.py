"""File storage abstraction (local FS by default; swap for S3/Supabase in prod)."""
from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings

_BASE = Path(os.getenv("STORAGE_DIR", "./uploads")).resolve()


def _safe_path(key: str) -> Path:
    target = (_BASE / key).resolve()
    if not str(target).startswith(str(_BASE)):
        raise ValueError("Invalid storage key (path traversal).")
    return target


def save(key: str, content: bytes) -> str:
    path = _safe_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return str(path.relative_to(_BASE))


def read(key: str) -> bytes:
    return _safe_path(key).read_bytes()


def delete(key: str) -> None:
    path = _safe_path(key)
    if path.exists():
        path.unlink()


# Expose configured bucket name for callers building object keys.
BUCKET = settings.STORAGE_BUCKET

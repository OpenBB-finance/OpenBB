"""Type stubs for the mixin pattern."""

from __future__ import annotations

import threading
from pathlib import Path


class _MixinBase:
    """Type-checker stub. Never instantiated directly."""

    blob: dict
    _boc: dict
    _statscan: dict
    _generated_at: str
    _source: str
    _lock: threading.Lock
    _initialized: bool

    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        raise NotImplementedError

    def _apply_blob(self, blob: dict) -> None:
        raise NotImplementedError

    def _load_from_cache(self) -> bool:
        raise NotImplementedError

    def _save_user_cache(self) -> None:
        raise NotImplementedError

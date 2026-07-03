"""Type stubs for the mixin pattern.

Each mixin inherits from ``_MixinBase`` so that both ty and pylint
can see cross-mixin attribute and method references. The methods all
raise ``NotImplementedError`` — they exist only so type-checkers know
the signatures; the real implementations live in the individual mixins
and override these via normal MRO.

This is the exact pattern introduced by ``openbb-oecd`` (PR #7413)
and is the cleanest way to keep ty strict-mode happy across a multi-
mixin class without resorting to ``# type: ignore`` sprinkles.
"""

from __future__ import annotations

import threading
from pathlib import Path


class _MixinBase:
    """Type-checker stub. Never instantiated directly."""

    # -- instance attributes (initialised in GovernmentCaMetadata.__init__) --
    blob: dict
    _boc: dict
    _statscan: dict
    _generated_at: str
    _source: str
    _lock: threading.Lock
    _initialized: bool

    # -- methods from CacheMixin --
    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        raise NotImplementedError

    def _apply_blob(self, blob: dict) -> None:
        raise NotImplementedError

    def _load_from_cache(self) -> bool:
        raise NotImplementedError

    def _save_user_cache(self) -> None:
        raise NotImplementedError

    # -- methods from LoaderMixin --
    # (populated in Phase 2 — for now the singleton just exposes the
    # loaded blob as ``self.blob`` with ``.boc`` and ``.statscan``
    # accessors.)

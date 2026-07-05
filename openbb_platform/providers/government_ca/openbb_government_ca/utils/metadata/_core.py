"""Core ``GovernmentCaMetadata`` singleton."""

from __future__ import annotations

import threading
from typing import Annotated

from fastapi import Depends

from openbb_government_ca.utils.metadata._cache_mixin import CacheMixin
from openbb_government_ca.utils.metadata._loader_mixin import LoaderMixin
from openbb_government_ca.utils.metadata._typing import _MixinBase


class GovernmentCaMetadata(  # type: ignore[misc]
    CacheMixin,
    LoaderMixin,
    _MixinBase,
):
    """Thread-safe singleton that lazily loads and caches Government of Canada metadata.

    Exposes two accessor properties:

    - ``.boc``       — Bank of Canada section of the cache
    - ``.statscan``  — Statistics Canada section of the cache
    """

    _instance: GovernmentCaMetadata | None = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> GovernmentCaMetadata:
        """Ensure only one instance of ``GovernmentCaMetadata`` exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # pragma: no cover - TOCTOU race guard
                    inst = object.__new__(cls)
                    cls._instance = inst
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize the singleton (idempotent — runs at most once)."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:  # pragma: no cover - TOCTOU race guard
                return

            self.blob: dict = {}
            self._boc: dict = {}
            self._statscan: dict = {}
            self._generated_at: str = ""
            self._source: str = "unknown"
            self._load_from_cache()
            self.__class__._initialized = True

    def __call__(self) -> GovernmentCaMetadata:
        """Make the singleton usable as a FastAPI ``Depends`` callable."""
        return self

    def __deepcopy__(self, memo: dict) -> GovernmentCaMetadata:
        """Singletons are not copyable — return ``self`` so deepcopy stops."""
        return self

    def __copy__(self) -> GovernmentCaMetadata:
        """Singletons are not copyable — return ``self`` so copy stops."""
        return self

    @classmethod
    def _reset(cls) -> None:
        """Destroy the singleton (for testing only)."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    @property
    def boc(self) -> dict:
        """Return the Bank of Canada section of the cache."""
        return self._boc

    @property
    def statscan(self) -> dict:
        """Return the Statistics Canada section of the cache."""
        return self._statscan

    @property
    def generated_at(self) -> str:
        """Return the ISO 8601 timestamp when the cache was generated."""
        return self._generated_at

    @property
    def source(self) -> str:
        """Return the cache source (``'build-hook'`` or ``'user'``)."""
        return self._source


GovernmentCaMetadataDependency = Annotated[
    GovernmentCaMetadata, Depends(GovernmentCaMetadata)
]

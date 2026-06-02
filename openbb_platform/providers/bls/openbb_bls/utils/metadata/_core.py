"""Singleton ``BlsMetadata`` over the shipped ``bls_cache.zip`` archive."""

from __future__ import annotations

import io
import json
import threading
import zipfile
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from openbb_bls.utils.metadata._constants import _SHIPPED_CACHE_FILE

if TYPE_CHECKING:
    from pandas import DataFrame


class BlsMetadata:
    """Thread-safe singleton holding lazily-loaded BLS metadata.

    The shipped ``bls_cache.zip`` is opened once at first instantiation
    and its ``index.json`` is read upfront. Per-category series tables
    and code maps are parsed on first access and memoized so that any
    subsequent lookup is a dict / DataFrame hit.

    Public API
    ----------
    categories : list[str]
        Cache-resident category keys (e.g. ``"cpi"``, ``"ppi"``).
    category_info(category) : dict
        ``{"name": str, "surveys": list[str], "series_count": int}``.
    get_series(category) : DataFrame
        The full series listing for *category*, loaded once.
    get_codes(category) : dict[str, dict[str, dict[str, str]]]
        Resolved code maps keyed by survey then dimension.

    All public methods are safe to call from any thread.
    """

    _instance: BlsMetadata | None = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> BlsMetadata:
        """Return the singleton instance, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        """Open the cache archive and seed the per-category memo tables."""
        if self._initialized:
            return
        with self._lock:
            if self._initialized:  # pragma: no cover - TOCTOU guard
                return
            self._index: dict[str, dict] = {}
            self._series_cache: dict[str, DataFrame] = {}
            self._codes_cache: dict[str, dict[str, dict[str, dict[str, str]]]] = {}
            self._archive_bytes: bytes | None = None
            self._load_archive()
            self.__class__._initialized = True

    def __call__(self) -> BlsMetadata:
        """Return ``self`` so the class can stand in for a FastAPI dependency."""
        return self

    def __deepcopy__(self, memo: dict) -> BlsMetadata:
        """Singletons are not copyable — return self so the deepcopy walker stops."""
        return self

    def __copy__(self) -> BlsMetadata:
        """Singletons are not copyable — return self so the copy module stops."""
        return self

    @classmethod
    def _reset(cls) -> None:
        """Destroy the singleton (for testing only)."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    def _load_archive(self) -> None:
        """Read ``bls_cache.zip`` into memory and parse ``index.json``."""
        if not _SHIPPED_CACHE_FILE.exists():
            return
        self._archive_bytes = _SHIPPED_CACHE_FILE.read_bytes()
        with zipfile.ZipFile(io.BytesIO(self._archive_bytes)) as zf:
            names = set(zf.namelist())
            if "index.json" not in names:
                return
            with zf.open("index.json") as fh:
                blob = json.load(fh)
        self._index = blob.get("categories", {})

    def _open(self) -> zipfile.ZipFile:
        """Return a new ``ZipFile`` reader over the in-memory archive bytes."""
        if self._archive_bytes is None:
            raise FileNotFoundError(
                f"BLS cache archive not found at {_SHIPPED_CACHE_FILE}. "
                "Run `generate-bls-cache` to materialize it."
            )
        return zipfile.ZipFile(io.BytesIO(self._archive_bytes))

    @property
    def categories(self) -> list[str]:
        """Return the sorted list of category keys present in the cache."""
        return sorted(self._index)

    def category_info(self, category: str) -> dict:
        """Return the index entry for *category*, or an empty dict if missing."""
        return self._index.get(category, {})

    def get_series(self, category: str) -> DataFrame:
        """Return the full series DataFrame for *category*, memoised."""
        if category in self._series_cache:
            return self._series_cache[category]
        if category not in self._index:
            raise KeyError(
                f"Unknown BLS category '{category}'. Choose from {self.categories}."
            )
        from pandas import read_csv

        with self._open() as zf, zf.open(f"{category}/series.csv") as fh:
            df = read_csv(fh, low_memory=False, dtype="object")
        df = df.where(df.notna(), None)
        self._series_cache[category] = df
        return df

    def get_codes(self, category: str) -> dict[str, dict[str, dict[str, str]]]:
        """Return the ``{survey: {dim_code: {value: label}}}`` map for *category*."""
        if category in self._codes_cache:
            return self._codes_cache[category]
        if category not in self._index:
            raise KeyError(
                f"Unknown BLS category '{category}'. Choose from {self.categories}."
            )
        with self._open() as zf:
            try:
                with zf.open(f"{category}/codes.json") as fh:
                    codes = json.load(fh)
            except KeyError:
                codes = {}
        self._codes_cache[category] = codes
        return codes


BlsMetadataDependency = Annotated[BlsMetadata, Depends(BlsMetadata)]

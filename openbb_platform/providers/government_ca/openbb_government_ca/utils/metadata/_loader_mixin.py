"""Loader mixin for ``GovernmentCaMetadata``.

In Phase 1 this is intentionally minimal — just enough to satisfy the
type-checker. Real loader logic (lazy fetching, partial refresh,
ETag-based conditional requests) lands in Phase 2 alongside the cache
generator.
"""

from __future__ import annotations

from openbb_government_ca.utils.metadata._typing import _MixinBase


class LoaderMixin(_MixinBase):
    """Methods for lazily loading metadata from upstream (Phase 2+)."""

    def _ensure_boc_loaded(self) -> None:
        """Ensure the BoC section of the cache is loaded.

        Phase 1 stub: the cache is loaded eagerly in ``__init__``, so
        this is a no-op. Phase 3 will turn it into a lazy fetcher that
        populates ``self._boc`` from the Valet API if the shipped
        cache is missing.
        """
        return None

    def _ensure_statscan_loaded(self) -> None:
        """Ensure the StatsCan section of the cache is loaded.

        Phase 1 stub — see ``_ensure_boc_loaded``.
        """
        return None

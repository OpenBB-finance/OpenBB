"""Loader mixin for ``GovernmentCaMetadata``."""

from __future__ import annotations

from openbb_government_ca.utils.metadata._typing import _MixinBase


class LoaderMixin(_MixinBase):
    """Methods for lazily loading metadata from upstream."""

    def _ensure_boc_loaded(self) -> None:
        """No-op: the cache is loaded eagerly in ``__init__``."""
        return None

    def _ensure_statscan_loaded(self) -> None:
        """No-op: the cache is loaded eagerly in ``__init__``."""
        return None

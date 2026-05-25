"""Cache load mixin."""

from __future__ import annotations

import json
import lzma
import warnings

from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.metadata._constants import _SHIPPED_CACHE_FILE
from openbb_imf.utils.metadata._typing import _MixinBase


class CacheMixin(_MixinBase):
    """Load the shipped SDMX metadata blob into the singleton."""

    def _load_from_cache(self: _MixinBase) -> bool:
        """Load metadata from ``imf_cache.json.xz``."""
        if not _SHIPPED_CACHE_FILE.exists():
            return False

        try:
            with lzma.open(_SHIPPED_CACHE_FILE, "rb") as f:
                cache = json.loads(f.read().decode())

            self.dataflows = cache.get("dataflows", {})
            self.datastructures = cache.get("datastructures", {})
            self.conceptschemes = cache.get("conceptschemes", {})
            self.dataflow_groups = cache.get("dataflow_groups", {})
            self._metadata_cache = cache.get("metadata_cache", {})
            self._constraints_cache = cache.get("constraints_cache", {})
            self._codelist_cache = cache.get("codelist_cache", {})
            self._codelist_descriptions = cache.get("codelist_descriptions", {})
            self._dataflow_parameters_cache = cache.get("dataflow_parameters", {})
            self._dataflow_indicators_cache = cache.get("dataflow_indicators", {})
            self.hierarchies = cache.get("hierarchies", {})
            self._hierarchy_to_codelist_map = self._build_hierarchy_to_codelist_map()
            self._codelist_to_hierarchies_map = (
                self._build_codelist_to_hierarchies_map()
            )

            return True

        except Exception as e:  # noqa: BLE001
            warnings.warn(f"Error loading cache: {e}", OpenBBWarning)
            return False

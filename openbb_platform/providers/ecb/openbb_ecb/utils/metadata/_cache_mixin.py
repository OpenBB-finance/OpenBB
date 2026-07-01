"""Loading the shipped LZMA metadata cache into the singleton."""

from __future__ import annotations

import json
import lzma

from openbb_ecb.utils.metadata._constants import SHIPPED_CACHE_FILE
from openbb_ecb.utils.metadata._typing import MetadataBase


class CacheMixin(MetadataBase):
    """Hydrate the singleton from ``ecb_cache.json.xz``."""

    def _load_from_cache(self) -> bool:
        """Populate the in-memory catalog from the shipped cache."""
        if not SHIPPED_CACHE_FILE.exists():
            import warnings

            warnings.warn(
                f"ECB metadata cache not found at {SHIPPED_CACHE_FILE}. "
                "Run `generate-ecb-cache` (or build the package) to materialize "
                "it; catalog features will be limited until then.",
                stacklevel=2,
            )
            return False

        with lzma.open(SHIPPED_CACHE_FILE, "rb") as fh:
            blob = json.loads(fh.read().decode("utf-8"))

        self.dataflows = blob.get("dataflows", {})
        self.datastructures = blob.get("datastructures", {})
        self.codelists = blob.get("codelists", {})
        self.concepts = blob.get("concepts", {})
        self.categories = blob.get("categories", {})
        self.dataflow_categories = blob.get("dataflow_categories", {})
        self.category_dataflows = blob.get("category_dataflows", {})
        self.presentation_tables = blob.get("presentation_tables", {})
        self.dataflow_constraints = blob.get("dataflow_constraints", {})
        self.dataflow_info = blob.get("dataflow_info", {})
        self.portal_concepts = blob.get("portal_concepts", {})
        return True

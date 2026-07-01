"""``EcbMetadata`` singleton over the ECB SDMX 2.1 catalog."""

from __future__ import annotations

import threading

from openbb_ecb.utils.metadata._cache_mixin import CacheMixin
from openbb_ecb.utils.metadata._category_mixin import CategoryMixin
from openbb_ecb.utils.metadata._loader_mixin import LoaderMixin
from openbb_ecb.utils.metadata._query_mixin import QueryMixin
from openbb_ecb.utils.metadata._search_mixin import SearchMixin
from openbb_ecb.utils.metadata._table_mixin import TableMixin


class EcbMetadata(
    CacheMixin,
    LoaderMixin,
    QueryMixin,
    SearchMixin,
    CategoryMixin,
    TableMixin,
):
    """Thread-safe singleton over the ECB SDMX metadata catalog."""

    _instance: EcbMetadata | None = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> EcbMetadata:
        """Return the singleton, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # pragma: no cover
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialise the singleton's caches once."""
        if self._initialized:
            return
        with self._lock:
            if self._initialized:  # pragma: no cover
                return
            self.dataflows = {}
            self.datastructures = {}
            self.codelists = {}
            self.concepts = {}
            self.categories = {}
            self.dataflow_categories = {}
            self.category_dataflows = {}
            self.presentation_tables = {}
            self.dataflow_constraints = {}
            self.dataflow_info = {}
            self.portal_concepts = {}
            self._dataflow_parameters_cache = {}
            self._load_from_cache()
            self._initialized = True

    @classmethod
    def _reset(cls) -> None:
        """Drop the singleton."""
        with cls._lock:
            cls._instance = None

    def __deepcopy__(self, memo: dict) -> EcbMetadata:
        """Return self."""
        return self

    def __copy__(self) -> EcbMetadata:
        """Return self."""
        return self

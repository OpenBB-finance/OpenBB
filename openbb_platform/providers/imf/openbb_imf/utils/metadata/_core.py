"""``ImfMetadata`` singleton."""

from __future__ import annotations

import threading

from openbb_imf.utils.metadata._cache_mixin import CacheMixin
from openbb_imf.utils.metadata._helpers import HelpersMixin
from openbb_imf.utils.metadata._indicator_mixin import IndicatorMixin
from openbb_imf.utils.metadata._loader_mixin import LoaderMixin
from openbb_imf.utils.metadata._query_mixin import QueryMixin
from openbb_imf.utils.metadata._search_mixin import SearchMixin
from openbb_imf.utils.metadata._table_mixin import TableMixin


class ImfMetadata(
    HelpersMixin,
    CacheMixin,
    LoaderMixin,
    SearchMixin,
    QueryMixin,
    IndicatorMixin,
    TableMixin,
):
    """Thread-safe singleton over the IMF SDMX metadata catalog."""

    _instance: ImfMetadata | None = None
    _lock = threading.Lock()
    _codelist_lock = threading.Lock()
    _constraints_lock = threading.Lock()
    _initialized: bool | None = None

    def __new__(cls) -> ImfMetadata:
        """Return the singleton, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialise the singleton's caches once."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self.dataflows: dict[str, dict] = {}
            self.datastructures: dict[str, dict] = {}
            self.conceptschemes: dict[str, dict] = {}
            self.dataflow_groups: dict[str, list[dict]] = {}
            self.hierarchies: dict[str, dict] = {}
            self._codelist_cache: dict[str, dict] = {}
            self._codelist_descriptions: dict[str, dict] = {}
            self._metadata_cache: dict = {}
            self._constraints_cache: dict = {}
            self._dataflow_parameters_cache: dict[str, dict] = {}
            self._dataflow_indicators_cache: dict[str, list] = {}
            self._hierarchy_to_codelist_map: dict[str, str] = {}
            self._codelist_to_hierarchies_map: dict[str, list[str]] = {}

            _ = self._load_from_cache()
            self._initialized = True

    @classmethod
    def _reset(cls) -> None:
        """Drop the singleton."""
        with cls._lock:
            cls._instance = None

    def __deepcopy__(self, memo: dict) -> ImfMetadata:
        """Singletons are not copyable — return self so the deepcopy walker stops."""
        return self

    def __copy__(self) -> ImfMetadata:
        """Singletons are not copyable — return self so the copy module stops."""
        return self

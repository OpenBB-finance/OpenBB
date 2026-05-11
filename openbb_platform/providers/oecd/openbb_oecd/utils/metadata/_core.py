"""Core OecdMetadata singleton class assembled from mixins."""

import threading
from typing import Annotated

from fastapi import Depends

from openbb_oecd.utils.metadata._cache_mixin import CacheMixin
from openbb_oecd.utils.metadata._indicator_mixin import IndicatorMixin
from openbb_oecd.utils.metadata._loader_mixin import LoaderMixin
from openbb_oecd.utils.metadata._public_api_mixin import PublicApiMixin
from openbb_oecd.utils.metadata._query_mixin import QueryMixin
from openbb_oecd.utils.metadata._search_mixin import SearchMixin


class OecdMetadata(
    CacheMixin,
    LoaderMixin,
    PublicApiMixin,
    IndicatorMixin,
    SearchMixin,
    QueryMixin,
):
    """Thread-safe singleton that lazily loads and caches OECD SDMX metadata.

    Public API
    ----------
    list_dataflows(topic=None)                → list[dict]
    list_topics()                             → list[dict]
    list_dataflows_by_topic()                 → list[dict]
    get_dataflow_info(dataflow_id)            → dict
    get_dataflow_parameters(dataflow_id)      → dict[str, list[dict]]
    resolve_country_codes(dataflow_id, input) → list[str]
    get_codelist_for_dimension(df_id, dim_id) → dict[str, str]
    get_indicators_in(dataflow_id)            → list[dict]
    search_indicators(query, dataflows, …)    → list[dict]
    get_dimension_order(dataflow_id)          → list[str]

    All public methods are safe to call from any thread.
    """

    _instance: "OecdMetadata | None" = None
    _lock = threading.Lock()
    _codelist_lock = threading.Lock()
    _initialized: bool = False
    _search_index: list[tuple[str, dict]] | None = None

    def __new__(cls) -> "OecdMetadata":
        """Ensure only one instance of OecdMetadata exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = object.__new__(cls)
                    cls._instance = inst
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize the OecdMetadata class."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:  # pragma: no cover - TOCTOU race guard; only reached when a second thread finishes init while we wait on the lock
                return

            self.dataflows: dict[str, dict] = {}
            self.datastructures: dict[str, dict] = {}
            self.codelists: dict[str, dict[str, str]] = {}
            self._short_id_map: dict[str, str] = {}
            self._codelist_descriptions: dict[str, dict[str, str]] = {}
            self._codelist_parents: dict[str, dict[str, str]] = {}
            self._codelist_comp_rules: dict[str, dict[str, str]] = {}
            self._dataflow_constraints: dict[str, dict[str, list[str]]] = {}
            self._dataflow_parameters_cache: dict[str, dict] = {}
            self._dataflow_indicators_cache: dict[str, list] = {}
            self._availability_cache: dict[str, dict[str, list[str]]] = {}
            self._indicator_dim_cache: dict[str, str | None] = {}
            self._table_map: dict[str, dict] = {}
            self._full_catalogue_loaded: bool = False
            self._taxonomy_tree: list[dict] = []
            self._df_to_categories: dict[str, list[str]] = {}
            self._category_to_dfs: dict[str, list[str]] = {}
            self._category_names: dict[str, str] = {}
            self._taxonomy_loaded: bool = False
            self._cache_dirty: bool = False
            self._load_from_cache()
            self.__class__._initialized = True

    def __call__(self) -> "OecdMetadata":
        return self

    @classmethod
    def _reset(cls) -> None:
        """Destroy the singleton (for testing only)."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False


OECDMetadataDependency = Annotated[OecdMetadata, Depends(OecdMetadata)]

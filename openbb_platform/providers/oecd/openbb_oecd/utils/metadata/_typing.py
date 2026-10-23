"""Type stubs for the mixin pattern.

Each mixin inherits from ``_MixinBase`` so that both mypy and pylint can
see cross-mixin attribute and method references.  The methods all raise
``NotImplementedError`` — they exist only so type-checkers know the
signatures; the real implementations live in the individual mixins and
override these via normal MRO.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path


class _MixinBase:
    # -- instance attributes (initialised in OecdMetadata.__init__) --
    dataflows: dict[str, dict]
    datastructures: dict[str, dict]
    codelists: dict[str, dict[str, str]]
    _short_id_map: dict[str, str]
    _codelist_lock: threading.Lock
    _codelist_descriptions: dict[str, dict[str, str]]
    _codelist_parents: dict[str, dict[str, str]]
    _codelist_comp_rules: dict[str, dict[str, str]]
    _dataflow_constraints: dict[str, dict[str, list[str]]]
    _dataflow_parameters_cache: dict[str, dict]
    _dataflow_indicators_cache: dict[str, list]
    _availability_cache: dict[str, dict[str, list[str]]]
    _indicator_dim_cache: dict[str, str | None]
    _table_map: dict[str, dict]
    _full_catalogue_loaded: bool
    _cache_dirty: bool
    _taxonomy_tree: list[dict]
    _df_to_categories: dict[str, list[str]]
    _category_to_dfs: dict[str, list[str]]
    _category_names: dict[str, str]
    _taxonomy_loaded: bool
    _search_index: list[tuple[str, dict]] | None

    # -- class attributes --
    _CL_KEY_RE: re.Pattern[str]

    # -- methods from CacheMixin --
    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        raise NotImplementedError

    def _apply_blob(self, blob: dict) -> None:
        raise NotImplementedError

    def _infer_orphan_parents(self) -> None:
        raise NotImplementedError

    @staticmethod
    def _closest_common_ancestor(
        codes: list[str], parents: dict[str, str]
    ) -> str | None:
        raise NotImplementedError

    def _load_from_cache(self) -> bool:
        raise NotImplementedError

    def _save_cache(self) -> None:
        raise NotImplementedError

    # -- methods from LoaderMixin --
    def _ensure_dataflows(self) -> None:
        raise NotImplementedError

    def _rebuild_short_id_map(self) -> None:
        raise NotImplementedError

    def _ensure_taxonomy(self) -> None:
        raise NotImplementedError

    def _resolve_dataflow_id(self, dataflow_id: str) -> str:
        raise NotImplementedError

    def _ensure_description(self, full_id: str) -> None:
        raise NotImplementedError

    def _ensure_structure(self, dataflow_id: str, *, force: bool = False) -> None:
        raise NotImplementedError

    # -- methods from PublicApiMixin --
    def list_dataflows(self, topic: str | None = None) -> list[dict]:
        raise NotImplementedError

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        raise NotImplementedError

    def get_dimension_order(self, dataflow_id: str) -> list[str]:
        raise NotImplementedError

    def get_dimension_info(self, dataflow_id: str) -> list[dict]:
        raise NotImplementedError

    def get_table_groups(self, dataflow_id: str) -> list[dict]:
        raise NotImplementedError

    def get_constrained_values(self, dataflow_id: str) -> dict[str, list[dict]]:
        raise NotImplementedError

    def table_map(self, *, include_empty: bool = False) -> list[dict]:
        raise NotImplementedError

    def find_tables(self, query: str) -> list[dict]:
        raise NotImplementedError

    def _get_codelist(
        self,
        codelist_id: str,
        _dataflow_id: str | None = None,
    ) -> dict[str, str]:
        raise NotImplementedError

    # -- methods from IndicatorMixin --
    def _get_indicator_dim(self, full_id: str) -> str | None:
        raise NotImplementedError

    def _find_indicator_dimension(
        self,
        dataflow_id: str,
        indicator_code: str | None = None,
    ) -> str | None:
        raise NotImplementedError

    def get_codelist_for_dimension(
        self, dataflow_id: str, dim_id: str
    ) -> dict[str, str]:
        raise NotImplementedError

    def get_indicator_tree(self, dataflow_id: str) -> list[dict]:
        raise NotImplementedError

    # -- methods from SearchMixin --
    def describe_dataflow(self, dataflow_id: str) -> dict:
        raise NotImplementedError

    # -- methods from QueryMixin --
    def fetch_availability(
        self,
        dataflow_id: str,
        pinned: dict[str, str] | None = None,
    ) -> dict[str, list[str]]:
        raise NotImplementedError

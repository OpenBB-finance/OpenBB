"""Type stubs for the IMF metadata mixin pattern."""

from __future__ import annotations

import threading


class _MixinBase:
    dataflows: dict[str, dict]
    datastructures: dict[str, dict]
    conceptschemes: dict[str, dict]
    dataflow_groups: dict[str, list[dict]]
    hierarchies: dict[str, dict]
    _metadata_cache: dict
    _constraints_cache: dict
    _codelist_cache: dict[str, dict]
    _codelist_descriptions: dict[str, dict]
    _dataflow_parameters_cache: dict[str, dict]
    _dataflow_indicators_cache: dict[str, list]
    _hierarchy_to_codelist_map: dict[str, str]
    _codelist_to_hierarchies_map: dict[str, list[str]]
    _codelist_lock: threading.Lock
    _constraints_lock: threading.Lock

    @staticmethod
    def _parse_agency_from_urn(code_urn: str) -> str | None:
        raise NotImplementedError

    @staticmethod
    def _parse_codelist_urn(urn: str) -> str | None:
        raise NotImplementedError

    @staticmethod
    def _parse_indicator_code_from_urn(code_urn: str) -> str | None:
        raise NotImplementedError

    @staticmethod
    def _parse_codelist_id_from_urn(code_urn: str) -> str | None:
        raise NotImplementedError

    @staticmethod
    def _parse_query(query: str) -> list[list[str]]:
        raise NotImplementedError

    @staticmethod
    def _build_time_period_parameters(
        constraints_response: dict | None,
    ) -> tuple[list[dict], str | None]:
        raise NotImplementedError

    def _extract_all_codelists_from_hierarchy(self, hierarchy: dict) -> set[str]:
        raise NotImplementedError

    def _build_hierarchy_to_codelist_map(self) -> dict[str, str]:
        raise NotImplementedError

    def _build_codelist_to_hierarchies_map(self) -> dict[str, list[str]]:
        raise NotImplementedError

    def _get_dimension_for_codelist(
        self, dataflow_id: str, codelist_id: str
    ) -> str | None:
        raise NotImplementedError

    def _load_from_cache(self) -> bool:
        raise NotImplementedError

    def _fetch_single_codelist(self, agency_id: str, codelist_id: str) -> bool:
        raise NotImplementedError

    def _bulk_fetch_and_cache_codelists(self, agency_id: str, dataflow_id: str) -> None:
        raise NotImplementedError

    def _get_codelist_map(
        self,
        codelist_id: str,
        agency_id: str,
        dataflow_id: str,
        include_descriptions: bool = False,
    ) -> dict:
        raise NotImplementedError

    def list_dataflows(self) -> list[dict]:
        raise NotImplementedError

    def search_dataflows(self, query: str) -> list[dict]:
        raise NotImplementedError

    def search_indicators(
        self,
        query: str,
        dataflows: list[str] | str | None = None,
        keywords: list[str] | None = None,
    ) -> list[dict]:
        raise NotImplementedError

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        raise NotImplementedError

    def get_available_constraints(
        self,
        dataflow_id: str,
        key: str,
        component_id: str | None = None,
        mode: str | None = None,
        references: str | None = None,
        **kwargs,
    ) -> dict:
        raise NotImplementedError

    def _resolve_codelist_id(
        self, dataflow_id: str, dsd_id: str | None, dim_id: str, dim_meta: dict
    ) -> str | None:
        raise NotImplementedError

    def get_indicators_in(self, dataflow_id: str) -> list:
        raise NotImplementedError

    def get_dataflow_hierarchies(self, dataflow_id: str) -> list[dict]:
        raise NotImplementedError

    def get_dataflow_table_structure(
        self, dataflow_id: str, table_id: str | None = None
    ) -> dict:
        raise NotImplementedError

    def list_all_dataflow_tables(self) -> dict[str, list[dict]]:
        raise NotImplementedError

    def _validate_hierarchy_queryable(self, dataflow_id: str, codes: list) -> bool:
        raise NotImplementedError

    def _fix_irfcl_hierarchy(self, indicators: list[dict]) -> list[dict]:
        raise NotImplementedError

    def _create_synthetic_groups_for_shared_prefixes(
        self, indicators: list[dict]
    ) -> list[dict]:
        raise NotImplementedError

    def _build_indicator_table_maps(
        self, dataflow_ids: set[str]
    ) -> tuple[dict[str, list[dict]], dict[str, str]]:
        raise NotImplementedError

    def _collect_indicators(
        self,
        dataflow_ids: set[str],
        indicator_to_tables: dict[str, list[dict]],
        indicator_table_text: dict[str, str],
    ) -> list[dict]:
        raise NotImplementedError

    def _filter_indicators_by_query(
        self, indicators: list[dict], query: str
    ) -> list[dict]:
        raise NotImplementedError

    def _filter_indicators_by_keywords(
        self, indicators: list[dict], keywords: list[str] | None
    ) -> list[dict]:
        raise NotImplementedError

    def _find_indicator_codelist_for_hierarchies(
        self, dataflow_id: str, dsd_id: str, dimensions: list
    ) -> str | None:
        raise NotImplementedError

    def _split_irfcl_hierarchy(
        self,
        dataflow_id: str,
        hier_id: str,
        hier_obj: dict,
        top_level_codes: list[dict],
        indicator_codelist_id: str,
    ) -> list[dict]:
        raise NotImplementedError

    @staticmethod
    def _select_hierarchy(
        table_id: str | None, available_hierarchies: list[dict]
    ) -> tuple[str | None, str | None, dict | None, str]:
        raise NotImplementedError

    def _process_hierarchical_codes(
        self,
        codes: list,
        *,
        dataflow_id: str,
        agency_clean: str,
        indicator_dimension_order: dict[str, int],
        codelist_dimension_cache: dict[str, str | None],
        codelist_labels_cache: dict[str, dict],
        codelist_desc_cache: dict[str, dict],
        parent_id: str | None = None,
        depth: int = 0,
        parent_codes: list | None = None,
        parent_dimension_codes: dict[str, str] | None = None,
        order_counter: list | None = None,
        parent_full_label: str | None = None,
        ancestor_labels: list | None = None,
    ) -> list[dict]:
        raise NotImplementedError

    def _resolve_dimension_for_code(
        self,
        dataflow_id: str,
        codelist_id_for_code: str | None,
        code_urn: str,
        codelist_dimension_cache: dict[str, str | None],
        codelist_labels_cache: dict[str, dict],
        codelist_desc_cache: dict[str, dict],
    ) -> str | None:
        raise NotImplementedError

    @staticmethod
    def _wrap_with_suffix_groups(
        path_children: list[dict],
        split_labels: list[list[str]],
        shared_suffix_count: int,
        parent_id: str | None,
        synthetic_groups: list[dict],
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def _wrap_with_prefix_group(
        path_children: list[dict],
        split_labels: list[list[str]],
        shared_prefix_count: int,
        parent_id: str | None,
        synthetic_groups: list[dict],
    ) -> None:
        raise NotImplementedError

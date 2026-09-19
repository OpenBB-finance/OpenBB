"""IMF Table Builder - Handles hierarchical table data fetching with validation."""

from __future__ import annotations

import warnings
from collections import defaultdict
from datetime import datetime

from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.helpers import parse_codelist_id_from_urn


def _calculate_depth(
    indicator: dict, indicator_by_code: dict, visited: set | None = None
) -> int:
    """Calculate the actual depth of an indicator by tracing its parent_id chain."""
    if visited is None:
        visited = set()

    code = indicator.get("indicator_code", "")
    if not code or code in visited:
        return 0
    visited.add(code)

    parent_id = indicator.get("parent_id")
    if parent_id is None or parent_id not in indicator_by_code:
        return 0

    return 1 + _calculate_depth(
        indicator_by_code[parent_id], indicator_by_code, visited
    )


class ImfTableBuilder:
    """Handles fetching and organizing IMF data according to hierarchical presentation tables."""

    def __init__(self):
        """Initialize the table builder with its own query builder instance."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        self.query_builder = ImfQueryBuilder()
        self.metadata = self.query_builder.metadata

    def _validate_dimension_constraints(self, dataflow: str, **kwargs) -> None:
        """Validate that the provided dimension parameter combinations are valid according

        Parameters
        ----------
        dataflow : str
            The dataflow ID
        **kwargs
            Dimension parameters to validate

        Raises
        ------
        ValueError
            If the parameter combination is invalid according to API constraints
        """
        self.query_builder.validate_dimension_constraints(dataflow, **kwargs)

    def get_table(
        self,
        dataflow: str | None = None,
        table_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        depth: int | None = None,
        parent_id: str | None = None,
        indicators: list[str] | str | None = None,
        **kwargs,
    ) -> dict:
        """Fetch data organized according to a hierarchy/presentation table structure.

        Parameters
        ----------
        dataflow : str | None
            The dataflow ID (e.g., "BOP", "IRFCL", "FAS"). Can be omitted if table_id
            is in the format "dataflow_id::table_id".
        table_id : str | None
            The specific hierarchy/table ID. Can be in format "dataflow_id::table_id"
            (as returned by list_tables with as_choices=True). If None, uses the
            first available table for the dataflow.
        start_date : str | None
            Start date for the time series (format: YYYY, YYYY-MM, or YYYY-QN)
        end_date : str | None
            End date for the time series
        depth : int | None
            Limit to indicators at specific depth level(s). Use 0 for top-level only.
            Can help avoid URL length limits by fetching data in stages.
        parent_id : str | None
            Fetch only indicators under a specific parent group. Useful for drilling
            down into sections of the hierarchy.
        indicators : list[str] | str | None
            Fetch specific indicator codes. If provided, overrides depth/parent_id.
        **kwargs
            Additional dimension parameters (e.g., COUNTRY="US", FREQUENCY="A")

        Returns
        -------
        dict
            A dictionary containing:
            - table_metadata: Information about the table/hierarchy
            - structure: Full hierarchy structure (not filtered, for reference)
            - data: Data rows with hierarchy ordering columns
            - series_metadata: Additional metadata for each series

        Examples
        --------
        >>> from openbb_imf.utils.table_builder import ImfTableBuilder
        >>> tb = ImfTableBuilder()

        >>> # Get only top-level indicators (avoid URL length issues)
        >>> result = tb.get_table("IRFCL", depth=0, COUNTRY="US", FREQUENCY="A")

        >>> # Get all indicators under a specific group
        >>> result = tb.get_table("IRFCL", parent_id="FA", COUNTRY="US")

        >>> # Get specific indicators
        >>> result = tb.get_table("IRFCL", indicators=["A", "FA", "L"], COUNTRY="US")

        >>> # Combine depth with parent to drill down
        >>> result = tb.get_table("BOP", parent_id="NETCD_T", depth=1, COUNTRY="US")

        >>> # Use combined dataflow::table_id format from list_tables choices
        >>> result = tb.get_table(table_id="BOP::H_BOP_BOP_AGG_STANDARD_PRESENTATION", COUNTRY="USA", FREQUENCY="A")
        """
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        if table_id and "::" in table_id:
            parts = table_id.split("::", 1)
            parsed_dataflow = parts[0]
            parsed_table_id = parts[1]
            if dataflow is not None and dataflow != parsed_dataflow:
                raise ValueError(
                    f"Dataflow mismatch: provided '{dataflow}' but table_id "
                    f"specifies '{parsed_dataflow}'. Use one or the other."
                )
            dataflow = parsed_dataflow
            table_id = parsed_table_id

        if dataflow is None:
            raise ValueError(
                "dataflow is required. Either provide it directly or use "
                "table_id in 'dataflow_id::table_id' format."
            )

        if kwargs or start_date or end_date:
            self._validate_dimension_constraints(
                dataflow, start_date=start_date, end_date=end_date, **kwargs
            )

        if table_id is None:
            available_tables = self.metadata.get_dataflow_hierarchies(dataflow)
            if len(available_tables) == 1:
                table_id = available_tables[0]["id"]
            elif len(available_tables) == 0:
                raise ValueError(
                    f"No tables/hierarchies found for dataflow '{dataflow}'"
                )

        table_structure = self.metadata.get_dataflow_table_structure(dataflow, table_id)
        table_metadata = {
            "hierarchy_id": table_structure["hierarchy_id"],
            "hierarchy_name": table_structure["hierarchy_name"],
            "hierarchy_description": table_structure["hierarchy_description"],
            "dataflow_id": table_structure["dataflow_id"],
            "codelist_id": table_structure["codelist_id"],
            "agency_id": table_structure["agency_id"],
            "version": table_structure["version"],
            "total_groups": table_structure["total_groups"],
            "type": table_structure["type"],
        }
        filtered_hierarchy_entries = table_structure["indicators"]

        if indicators is not None:
            indicator_set = (
                {indicators} if isinstance(indicators, str) else set(indicators)
            )
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("indicator_code") in indicator_set
            ]
        elif parent_id is not None:
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("parent_id") == parent_id
            ]
        elif depth is not None:
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("depth") == depth
            ]

        entries_with_codes = [
            entry for entry in filtered_hierarchy_entries if entry.get("indicator_code")
        ]

        if not entries_with_codes:
            raise ValueError(
                "No indicators match the specified filters "
                f"(depth={depth}, parent_id={parent_id}, indicators={indicators}). "
                f"Total entries in hierarchy: {len(table_structure['indicators'])}"
            )

        dimension_codes: dict = defaultdict(list)
        dimension_codes_with_depth = defaultdict(list)
        codelist_to_dimension_cache = {}

        for entry in entries_with_codes:
            indicator_code = entry.get("indicator_code")
            code_urn = entry.get("code_urn", "")

            if not indicator_code:
                continue  # pragma: no cover -- entries_with_codes is pre-filtered to require indicator_code at line 199-201

            dimension_id = entry.get("dimension_id")

            if not dimension_id:
                codelist_id = parse_codelist_id_from_urn(code_urn)

                if not codelist_id:
                    warnings.warn(
                        f"Could not parse codelist from code_urn for {indicator_code}: {code_urn}",
                        OpenBBWarning,
                    )
                    continue

                if "_LABELS" in codelist_id or "_TABLE_LEVEL" in codelist_id:
                    continue

                if codelist_id not in codelist_to_dimension_cache:
                    dimension_id = self.metadata._get_dimension_for_codelist(
                        dataflow, codelist_id
                    )
                    if not dimension_id:
                        codelist_upper = codelist_id.upper()
                        dimension_patterns = [
                            ("INDICATOR", "INDICATOR"),
                            ("COUNTRY", "REF_AREA"),
                            ("REF_AREA", "REF_AREA"),
                            ("UNIT", "UNIT_MEASURE"),
                            ("FREQ", "FREQ"),
                            ("ACCOUNTING_ENTRY", "BOP_ACCOUNTING_ENTRY"),
                            ("PRODUCTION_INDEX", "INDEX_TYPE"),
                            ("COICOP_1999", "COICOP_1999"),
                            ("ACTIVITY", "ACTIVITY"),
                            ("SECTOR", "SECTOR"),
                        ]
                        df_obj = self.metadata.dataflows.get(dataflow, {})
                        dsd_id = df_obj.get("structureRef", {}).get("id")
                        dsd = self.metadata.datastructures.get(dsd_id, {})
                        dsd_dims = [
                            d.get("id")
                            for d in dsd.get("dimensions", [])
                            if d.get("id")
                        ]
                        for pattern, default_dim in dimension_patterns:
                            if pattern in codelist_upper:
                                for dsd_dim in dsd_dims:
                                    if (
                                        pattern in dsd_dim.upper()
                                        or dsd_dim.upper() == default_dim
                                    ):
                                        dimension_id = dsd_dim
                                        break
                                if dimension_id:
                                    break
                    codelist_to_dimension_cache[codelist_id] = dimension_id
                else:
                    dimension_id = codelist_to_dimension_cache[codelist_id]

                if not dimension_id:
                    warnings.warn(
                        f"Could not map codelist {codelist_id} to dimension for dataflow {dataflow}",
                        OpenBBWarning,
                    )
                    continue

            if indicator_code not in dimension_codes[dimension_id]:
                dimension_codes[dimension_id].append(indicator_code)
                code_depth = entry.get("depth", 0)
                dimension_codes_with_depth[dimension_id].append(
                    (indicator_code, code_depth)
                )

        if not dimension_codes:
            raise ValueError(
                f"No valid indicator codes found after filtering and dimension mapping. "
                f"Filtered entries: {len(entries_with_codes)}"
            )

        hierarchy_order_map = {}
        hierarchy_by_series_id = {}
        hierarchy_by_sorted_codes = {}
        hierarchy_by_composite_key: dict[tuple[str, str], list[dict]] = defaultdict(
            list
        )
        parents_by_indicator_code: dict[str, set[str]] = defaultdict(set)

        indicator_by_code = {}
        for ind in table_structure["indicators"]:
            code = ind.get("indicator_code")
            if code:
                indicator_by_code[code] = ind

        dataflow_obj = self.metadata.dataflows.get(dataflow, {})
        series_id_prefix = f"{dataflow}::"

        structure_ref = dataflow_obj.get("structureRef", {})
        dsd_id = structure_ref.get("id")
        indicator_dimension_order: dict[str, int] = {}

        if dsd_id and dsd_id in self.metadata.datastructures:
            dsd = self.metadata.datastructures[dsd_id]
            dimensions = dsd.get("dimensions", [])

            indicator_id_candidates = [
                "INDICATOR",
                "PRODUCTION_INDEX",
                "COICOP_1999",
                "ACTIVITY",
                "INDEX_TYPE",
                "CPI_INDEX_TYPE",
                "PRODUCT",
                "SERIES",
                "ITEM",
                "SECTOR",
                "BOP_ACCOUNTING_ENTRY",
                "ACCOUNTING_ENTRY",
            ]

            for idx, dim in enumerate(dimensions):
                dim_id = dim.get("id", "")
                if not dim_id:
                    continue
                is_indicator_candidate = dim_id in indicator_id_candidates or any(
                    keyword in dim_id
                    for keyword in ["INDICATOR", "ACCOUNTING_ENTRY", "ENTRY"]
                )
                if is_indicator_candidate:
                    indicator_dimension_order[dim_id] = idx

        for _, ind in enumerate(table_structure["indicators"]):
            indicator_code = ind.get("indicator_code")
            if not indicator_code:
                continue

            order_value = ind.get("order")

            if order_value is None:
                continue

            depth = ind.get("depth")

            if depth is None:
                depth = _calculate_depth(ind, indicator_by_code)

            parent_node_id = ind.get("parent_id")
            parent_indicator_code = None

            if parent_node_id:
                for other_ind in table_structure["indicators"]:
                    other_id = other_ind.get("id")
                    other_code = other_ind.get("indicator_code")
                    if parent_node_id in (other_id, other_code):
                        parent_indicator_code = other_code
                        break

            hierarchy_info = {
                "order": order_value,
                "level": depth,
                "parent_id": parent_node_id,  # Keep original for reference
                "parent_code": parent_indicator_code,  # Add resolved parent code
                "label": ind.get("label", ""),
                "indicator_code": indicator_code,
                "is_group": ind.get("is_group", False),
                "hierarchy_node_id": ind.get(
                    "id"
                ),  # Hierarchy node ID for parent matching
                "hierarchy_series_id": ind.get("series_id", ""),
            }
            hierarchy_order_map[indicator_code] = hierarchy_info

            if parent_indicator_code:
                composite_key = (indicator_code, parent_indicator_code)
                hierarchy_by_composite_key[composite_key].append(hierarchy_info)
                parents_by_indicator_code[indicator_code].add(parent_indicator_code)

            if series_id := ind.get("series_id"):
                hierarchy_by_series_id[series_id] = hierarchy_info
                if series_id.startswith(series_id_prefix):
                    codes_str = series_id[len(series_id_prefix) :]
                    sorted_codes = "_".join(sorted(codes_str.split("_")))
                    hierarchy_by_sorted_codes[sorted_codes] = hierarchy_info
                else:
                    dataflow_marker = f"_{dataflow}_"
                    if dataflow_marker in series_id:
                        idx = series_id.find(dataflow_marker) + len(dataflow_marker)
                        codes_str = series_id[idx:]
                        if codes_str:
                            sorted_codes = "_".join(sorted(codes_str.split("_")))
                            hierarchy_by_sorted_codes[sorted_codes] = hierarchy_info
                            new_format_id = f"{dataflow}::{codes_str}"
                            hierarchy_by_series_id[new_format_id] = hierarchy_info

        table_metadata["total_indicators"] = len(entries_with_codes)
        fetch_kwargs = kwargs.copy()

        try:
            builder = ImfParamsBuilder(dataflow)
            dims_in_order = builder._get_dimensions_in_order()
            dim_id_map = {d.lower(): d for d in dims_in_order}

            country_dims = ["COUNTRY", "REF_AREA", "JURISDICTION", "COUNTERPART_AREA"]
            for country_dim in country_dims:
                if country_dim in dims_in_order:
                    dim_id_map["country"] = country_dim
                    break

            indicator_dims = ["INDICATOR", "CLASSIFICATION"]
            for indicator_dim in indicator_dims:
                if indicator_dim in dims_in_order:
                    dim_id_map["indicator"] = indicator_dim
                    break

            normalized_kwargs = {}
            for key, value in kwargs.items():
                matched_dim = dim_id_map.get(key.lower())
                if matched_dim:
                    normalized_kwargs[matched_dim] = value
                else:
                    normalized_kwargs[key] = value

            fetch_kwargs = normalized_kwargs.copy()
            empty_dimensions: list[str] = []
            for dim_id in dims_in_order:
                if dim_id in normalized_kwargs and dim_id not in dimension_codes:
                    user_value = normalized_kwargs[dim_id]

                    if user_value != "*":
                        available_options = builder.get_options_for_dimension(dim_id)
                        available_values = {opt["value"] for opt in available_options}

                        user_values = (
                            user_value.split("+")
                            if isinstance(user_value, str) and "+" in user_value
                            else [user_value]
                        )
                        invalid_values = [
                            v
                            for v in user_values
                            if v not in available_values and v != "*"
                        ]

                        if invalid_values:
                            prior_selections = {
                                d: normalized_kwargs.get(d)
                                for d in dims_in_order
                                if d in normalized_kwargs
                                and dims_in_order.index(d) < dims_in_order.index(dim_id)
                            }
                            display_values = sorted(available_values)
                            raise ValueError(
                                f"Invalid value(s) for dimension '{dim_id}': {invalid_values}. "
                                f"Given prior selections {prior_selections}, "
                                f"available values are: {display_values}"
                            )

                    builder.set_dimension((dim_id, user_value))
                    fetch_kwargs[dim_id] = user_value
                elif dim_id in dimension_codes:
                    user_override = normalized_kwargs.get(dim_id)
                    codes = dimension_codes[dim_id]
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = {opt["value"] for opt in available_options}
                    filtered_codes = [c for c in codes if c in available_values]
                    if not filtered_codes and dim_id in {"INDICATOR", "CLASSIFICATION"}:
                        for hier_code in codes:
                            matching_codes = [
                                av
                                for av in available_values
                                if av.startswith(hier_code + "_") or av == hier_code
                            ]
                            filtered_codes.extend(matching_codes)
                        filtered_codes = list(dict.fromkeys(filtered_codes))

                    if filtered_codes:
                        joined_codes = "+".join(filtered_codes)
                        MAX_CODES_LENGTH = 850
                        use_wildcard_for_fetch = len(joined_codes) > MAX_CODES_LENGTH

                        if use_wildcard_for_fetch:
                            fetch_kwargs[dim_id] = "*"
                            if "_indicator_codes_to_filter" not in fetch_kwargs:
                                fetch_kwargs["_indicator_codes_to_filter"] = set()
                            fetch_kwargs["_indicator_codes_to_filter"].update(
                                filtered_codes
                            )
                        else:
                            fetch_kwargs[dim_id] = joined_codes

                        if len(joined_codes) > MAX_CODES_LENGTH:
                            code_depths = dict(
                                dimension_codes_with_depth.get(dim_id, [])
                            )
                            shallow_codes = [
                                c for c in codes if code_depths.get(c, 0) <= 1
                            ]
                            shallow_available = [
                                c for c in shallow_codes if c in available_values
                            ]
                            if shallow_available:
                                constraint_key = "+".join(shallow_available)
                                if len(constraint_key) > MAX_CODES_LENGTH:
                                    constraint_key = "*"
                            else:
                                truncated = []
                                length = 0
                                for c in filtered_codes:
                                    if length + len(c) + 1 > MAX_CODES_LENGTH:
                                        break
                                    truncated.append(c)
                                    length += len(c) + 1
                                constraint_key = (
                                    "+".join(truncated) if truncated else "*"
                                )
                                if len(constraint_key) > MAX_CODES_LENGTH:
                                    constraint_key = "*"  # pragma: no cover -- defensive: truncation loop ensures length <= MAX_CODES_LENGTH
                        else:
                            constraint_key = joined_codes

                        builder_key = user_override if user_override else constraint_key
                        builder.set_dimension((dim_id, builder_key))
                    else:
                        empty_dimensions.append(dim_id)
                        prior_selections = {
                            d: normalized_kwargs.get(d)
                            for d in dims_in_order
                            if d in normalized_kwargs
                            and dims_in_order.index(d) < dims_in_order.index(dim_id)
                        }
                        raise ValueError(
                            f"No data available: Table indicator codes do not match "
                            f"available data for dimension '{dim_id}'. "
                            f"Table has indicators: {codes}"
                            f"but given {prior_selections}, "
                            f"available indicators are: {available_values}"
                        )

            indicator_dims_set = {"INDICATOR", "BOP_ACCOUNTING_ENTRY", "SERIES", "ITEM"}
            missing_indicator_dims = [
                d for d in empty_dimensions if d in indicator_dims_set
            ]
            expected_indicator_dims = [
                d for d in dims_in_order if d in indicator_dims_set
            ]
            unmapped_indicator_dims = [
                d
                for d in expected_indicator_dims
                if d not in dimension_codes and d not in fetch_kwargs
            ]
            if unmapped_indicator_dims:
                raise ValueError(
                    f"Table indicators could not be mapped to dimension(s) {unmapped_indicator_dims}. "
                    f"The hierarchy's indicator codes are not compatible with dataflow '{dataflow}'. "
                    f"Hierarchy had codes from codelists: {list(codelist_to_dimension_cache.keys())}, "
                    f"but none matched the dataflow's indicator dimension."
                )

            if (
                missing_indicator_dims
                and not any(  # pragma: no cover -- dead: line 547 unconditionally raises when empty_dimensions is appended to, so missing_indicator_dims is always empty here
                    d in fetch_kwargs for d in indicator_dims_set
                )
            ):
                for dim_id in (
                    missing_indicator_dims
                ):  # pragma: no cover -- dead: see line 575 reason
                    invalid_values = dimension_codes.get(
                        dim_id, []
                    )  # pragma: no cover -- dead: see line 575 reason
                    available_options = builder.get_options_for_dimension(
                        dim_id
                    )  # pragma: no cover -- dead: see line 575 reason
                    available_values = (
                        sorted(  # pragma: no cover -- dead: see line 575 reason
                            {opt["value"] for opt in available_options}
                        )
                    )
                    prior_selections = {  # pragma: no cover -- dead: see line 575 reason
                        d: normalized_kwargs.get(d)
                        for d in dims_in_order
                        if d in normalized_kwargs
                        and dims_in_order.index(d) < dims_in_order.index(dim_id)
                    }
                    raise ValueError(  # pragma: no cover -- dead: see line 575 reason
                        f"Invalid value(s) for dimension '{dim_id}': {invalid_values}. "
                        f"Given prior selections {prior_selections}, "
                        f"available values are: {available_values}"
                    )

            for dim_id, codes in dimension_codes.items():
                if dim_id not in dims_in_order and dim_id not in fetch_kwargs:
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = {opt["value"] for opt in available_options}
                    filtered_codes = [c for c in codes if c in available_values]

                    if not filtered_codes:
                        for hier_code in codes:
                            matching_codes = [
                                av
                                for av in available_values
                                if av.startswith(hier_code + "_") or av == hier_code
                            ]
                            filtered_codes.extend(matching_codes)
                        filtered_codes = list(dict.fromkeys(filtered_codes))

                    if filtered_codes:
                        joined_codes = "+".join(filtered_codes)
                        if len(joined_codes) > 1500:
                            fetch_kwargs[dim_id] = "*"
                            if "_indicator_codes_to_filter" not in fetch_kwargs:
                                fetch_kwargs["_indicator_codes_to_filter"] = set()
                            fetch_kwargs["_indicator_codes_to_filter"].update(
                                filtered_codes
                            )
                        else:
                            fetch_kwargs[dim_id] = joined_codes
                    else:
                        prior_selections = {
                            d: fetch_kwargs.get(d) or normalized_kwargs.get(d)
                            for d in dims_in_order
                            if fetch_kwargs.get(d) or normalized_kwargs.get(d)
                        }
                        raise ValueError(
                            f"No valid values for dimension '{dim_id}' given constraints. "
                            f"Table indicator codes: {codes}"
                            f"available for {prior_selections}: {sorted(available_values)}"
                        )

        except (KeyError, ValueError) as e:
            error_msg = str(e)
            if (
                "Invalid value(s) for dimension" in error_msg
                or "not compatible with dataflow" in error_msg
            ):
                raise ValueError(error_msg) from e
            warnings.warn(
                f"Progressive constraint filtering failed: {e}. Using unfiltered codes.",
                OpenBBWarning,
            )
            for dim_id, codes in dimension_codes.items():
                if dim_id not in fetch_kwargs:
                    joined_codes = "+".join(codes)
                    if len(joined_codes) > 1500:
                        fetch_kwargs[dim_id] = "*"
                        if "_indicator_codes_to_filter" not in fetch_kwargs:
                            fetch_kwargs["_indicator_codes_to_filter"] = set()
                        fetch_kwargs["_indicator_codes_to_filter"].update(codes)
                    else:
                        fetch_kwargs[dim_id] = joined_codes

        if "INDICATOR" in fetch_kwargs and fetch_kwargs["INDICATOR"] != "*":
            next_dim = builder.get_next_dimension_to_select()
            if next_dim:
                _ = builder.get_options_for_dimension(next_dim)

        if start_date or end_date:
            last_response = getattr(builder, "_last_constraints_response", None)
            if last_response:
                full_response = last_response.get("full_response", {})
                data_constraints = full_response.get("data", {}).get(
                    "dataConstraints", []
                )

                for constraint in data_constraints:
                    annotations = constraint.get("annotations", [])
                    time_start = None
                    time_end = None

                    for ann in annotations:
                        ann_id = ann.get("id", "")
                        ann_title = ann.get("title", "")
                        if ann_id == "time_period_start":
                            time_start = ann_title
                        elif ann_id == "time_period_end":
                            time_end = ann_title

                    if time_start and time_end:

                        def parse_date(date_str: str) -> datetime | None:
                            if not date_str:
                                return None  # pragma: no cover -- defensive: all callers gate on truthiness before invoking
                            if "-Q" in date_str.upper():
                                year, q = date_str.upper().split("-Q")
                                month = int(q) * 3
                                return datetime(int(year), month, 1)
                            if len(date_str) == 7:
                                return datetime.strptime(date_str, "%Y-%m")
                            if len(date_str) >= 10:
                                return datetime.strptime(date_str[:10], "%Y-%m-%d")
                            return datetime(int(date_str[:4]), 1, 1)

                        try:
                            avail_start = parse_date(time_start)
                            avail_end = parse_date(time_end)
                            req_start = parse_date(start_date) if start_date else None
                            req_end = parse_date(end_date) if end_date else None
                        except (ValueError, TypeError):
                            break

                        no_overlap = False
                        if req_start and avail_end and req_start > avail_end:
                            no_overlap = True
                        if req_end and avail_start and req_end < avail_start:
                            no_overlap = True

                        if no_overlap:
                            raise ValueError(
                                f"No data available for the requested time period. "
                                f"Data for this table with country "
                                f"'{fetch_kwargs.get('COUNTRY', 'N/A')}' is only available "
                                f"from {time_start} to {time_end}. "
                                f"Your request: {start_date or 'beginning'} to {end_date or 'present'}."
                            )
                        break

        indicator_codes_to_filter = fetch_kwargs.pop("_indicator_codes_to_filter", None)

        data_result = self.query_builder.fetch_data(
            dataflow=dataflow,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            _skip_validation=True,  # We already validated above
            **fetch_kwargs,
        )

        data_rows = data_result.get("data", [])

        if indicator_codes_to_filter:
            original_count = len(data_rows)
            data_rows = [
                row
                for row in data_rows
                if row.get("INDICATOR_code") in indicator_codes_to_filter
                or row.get("indicator_code") in indicator_codes_to_filter
            ]
            filtered_count = len(data_rows)
            if filtered_count < original_count:
                data_result["data"] = data_rows

        priority_columns = ["order", "level", "parent_id", "series_id"]

        indicator_code_fields = [
            "INDICATOR_code",
            "COICOP_1999_code",
            "INDEX_TYPE_code",
            "CPI_INDEX_TYPE_code",
            "PRODUCTION_INDEX_code",
            "ACTIVITY_code",
            "PRODUCT_code",
            "SERIES_code",
            "ITEM_code",
            "CLASSIFICATION_code",
        ]

        for row in data_rows:
            indicator_code = ""
            for field in indicator_code_fields:
                indicator_code = row.get(field, "")
                if indicator_code:
                    break

            if not indicator_code:
                continue

            hier_info = None
            row_series_id = row.get("series_id", "")

            if row_series_id:
                hier_info = hierarchy_by_series_id.get(row_series_id)

            if not hier_info and row_series_id and "::" in row_series_id:
                codes_part = row_series_id.split("::", 1)[1]
                if codes_part:
                    sorted_codes = "_".join(sorted(codes_part.split("_")))
                    hier_info = hierarchy_by_sorted_codes.get(sorted_codes)

            bop_entry_code = row.get("BOP_ACCOUNTING_ENTRY_code", "") or row.get(
                "bop_accounting_entry_code", ""
            )
            if (
                not hier_info
                and not row_series_id
                and bop_entry_code
                and indicator_code
            ):
                constructed_sorted = "_".join(sorted([indicator_code, bop_entry_code]))
                hier_info = hierarchy_by_sorted_codes.get(constructed_sorted)

            if not hier_info and bop_entry_code and indicator_code:

                def _choose_from_candidates(
                    candidates: list[dict], entry_code: str
                ) -> dict | None:
                    if not candidates:
                        return None
                    if len(candidates) == 1:
                        return candidates[0]

                    entry_code_upper = entry_code.upper()
                    markers: set[str] = {entry_code_upper}
                    if entry_code_upper in {"CD_T", "NEGCD_T"}:
                        markers |= {"CD", "CREDIT"}
                    elif entry_code_upper == "DB_T":
                        markers |= {"DB", "DEBIT"}
                    elif entry_code_upper == "A_P":
                        markers |= {"ASSET", "ASSETS"}
                    elif entry_code_upper == "L_P":
                        markers |= {"LIAB", "LIABILITIES", "LIABILITY"}

                    for cand in candidates:
                        haystack = f"{cand.get('hierarchy_node_id', '')} {cand.get('hierarchy_series_id', '')}".upper()
                        if any(m in haystack for m in markers):
                            return cand

                    return candidates[0]

                composite_key = (indicator_code, bop_entry_code)
                hier_info = _choose_from_candidates(
                    hierarchy_by_composite_key.get(composite_key, []), bop_entry_code
                )

                if not hier_info and bop_entry_code in {"CD_T", "DB_T"}:
                    candidate_parents = parents_by_indicator_code.get(
                        indicator_code, set()
                    )
                    net_parent: str | None = None
                    if "NETCD_T" in candidate_parents:
                        net_parent = "NETCD_T"
                    else:
                        net_like = sorted(
                            p for p in candidate_parents if p.startswith("NET")
                        )
                        if len(net_like) == 1 or net_like:
                            net_parent = net_like[0]

                    if net_parent:
                        hier_info = _choose_from_candidates(
                            hierarchy_by_composite_key.get(
                                (indicator_code, net_parent), []
                            ),
                            bop_entry_code,
                        )

            if not hier_info and not bop_entry_code:
                hier_info = hierarchy_order_map.get(indicator_code)

            if not hier_info:
                for hier_code, info in hierarchy_order_map.items():
                    if indicator_code.startswith(hier_code + "_"):
                        hier_info = info
                        break

            if not hier_info:
                continue

            row["order"] = hier_info["order"]
            row["level"] = hier_info["level"]
            row["parent_id"] = hier_info["parent_id"]
            row["parent_code"] = hier_info["parent_code"]
            row["label"] = hier_info["label"]
            row["hierarchy_node_id"] = hier_info.get("hierarchy_node_id")

        data_rows = [row for row in data_rows if row.get("order") is not None]

        indicator_codelist = {}
        indicator_codelist_id = None  # Initialize to avoid UnboundLocalError

        df_obj = self.metadata.dataflows.get(dataflow, {})
        dsd_id = df_obj.get("structureRef", {}).get("id")
        dsd_id = df_obj.get("structureRef", {}).get("id")
        if dsd_id:
            dsd = self.metadata.datastructures.get(dsd_id, {})
            dimensions = dsd.get("dimensions", []) if isinstance(dsd, dict) else []

            indicator_dim_candidates = [
                "INDICATOR",
                "CLASSIFICATION",
                "SERIES",
                "ITEM",
                "PRODUCT",
                "ACTIVITY",
            ]
            for dim in dimensions:
                dim_id = dim.get("id", "")
                if dim_id in indicator_dim_candidates or "INDICATOR" in dim_id:
                    indicator_codelist_id = self.metadata._resolve_codelist_id(
                        dataflow, dsd_id, dim_id, dim
                    )
                    if indicator_codelist_id:
                        indicator_codelist = self.metadata._codelist_cache.get(
                            indicator_codelist_id, {}
                        )
                    break

        sector_codelist = self.metadata._codelist_cache.get("CL_SECTOR", {})

        for row in data_rows:
            row["is_category_header"] = False

            ind_code = row.get("INDICATOR_code", "")

            ind_name = indicator_codelist.get(ind_code, "")

            if ind_name and ", " in ind_name:
                name_parts = ind_name.split(", ")
                unit_patterns = [
                    "US dollar",
                    "Percent",
                    "Euro",
                    "Domestic currency",
                    "SDR",
                    "Yen",
                    "Pound",
                    "Yuan",
                    "National currency",
                    "Basis points",
                    "Units",
                ]

                gfs_recording_suffixes = [
                    "Stock positions",
                    "Transactions",
                    "Flows",
                    "Stocks",
                    "Cash basis",
                    "Transactions (cash basis of recording)",
                    "Memorandum Item",
                ]

                fsi_classification_tags = ["(Core FSI)", "(Additional FSI)"]

                if any(name_parts[-1].startswith(u) for u in unit_patterns):
                    name_parts = name_parts[:-1]

                while len(name_parts) > 1 and name_parts[-1] in gfs_recording_suffixes:
                    name_parts = name_parts[:-1]

                name_parts = [p for p in name_parts if p not in fsi_classification_tags]

                deduped_parts: list = []
                for p in name_parts:
                    if not deduped_parts or deduped_parts[-1] != p:
                        deduped_parts.append(p)
                name_parts = deduped_parts

                if len(name_parts) >= 1:
                    ind_name = ", ".join(name_parts)

            sector_prefix = None
            is_gfs_indicator = (
                indicator_codelist_id and indicator_codelist_id.startswith("CL_GFS")
            )

            if is_gfs_indicator:
                sector_code = row.get("SECTOR_code")
                if sector_code and sector_code in sector_codelist:
                    sector_prefix = sector_code
            elif ind_code and "_" in ind_code:
                first_part = ind_code.split("_")[0]
                if first_part in sector_codelist:
                    sector_prefix = first_part

            uses_path_labels = indicator_codelist_id and (
                indicator_codelist_id.endswith("_INDICATOR_PUB")
                or indicator_codelist_id.endswith("_INDICATOR_DEFAULT_PUB")
                or indicator_codelist_id == "CL_DIP_INDICATOR"
            )

            if uses_path_labels and row.get("label"):
                row["title"] = row["label"]
            elif ind_name:
                if sector_prefix:
                    sector_name = sector_codelist.get(sector_prefix, "")
                    if sector_name:
                        row["title"] = f"{sector_name}, {ind_name}"
                    else:
                        row["title"] = ind_name
                else:
                    row["title"] = ind_name

            if not row.get("title") and row.get("label"):
                row["title"] = row["label"]

            if not row.get("title") and ind_code:
                readable_code = ind_code.replace("_", " ")
                row["title"] = readable_code

            bop_entry = row.get("BOP_ACCOUNTING_ENTRY_code")
            if bop_entry and row.get("title"):
                bop_entry_labels = {
                    "CD_T": "Credit",
                    "DB_T": "Debit",
                    "NETCD_T": "Net",
                    "A_T": "Assets",
                    "L_T": "Liabilities",
                    "A_P": "Assets",
                    "L_P": "Liabilities",
                    "A_NFA_T": "Assets (excl. reserves)",
                    "L_NIL_T": "Liabilities (incl. net incurrence)",
                    "NNAFANIL_T": "Net (Assets excl. reserves less Liabilities)",
                }
                entry_label = bop_entry_labels.get(bop_entry)
                if entry_label:
                    row["title"] = f"{row['title']}, {entry_label}"

            if not bop_entry and row.get("title"):
                series_id = row.get("series_id", "")
                title_lower = row["title"].lower()
                has_asset_context = "asset" in title_lower
                has_liab_context = "liabilit" in title_lower

                if not has_asset_context and not has_liab_context:
                    if "_IIP_A_P_" in series_id or "_IIP_A_P" in series_id:
                        row["title"] = f"{row['title']} (Assets)"
                    elif "_IIP_L_P_" in series_id or "_IIP_L_P" in series_id:
                        row["title"] = f"{row['title']} (Liabilities)"

            currency_code = row.get("CURRENCY_code")
            currency_label = row.get("CURRENCY")
            unit_code = row.get("unit_code") or row.get("UNIT_MEASURE_code")
            if currency_code and currency_label and row.get("title"):
                skip_currencies = {"_T", "W0", "W1", "W2", "ALL"}
                if currency_code not in skip_currencies and currency_code != unit_code:
                    row["title"] = f"{row['title']} ({currency_label})"

            if (
                dataflow == "CPI"
                and (index_type_code := row.get("INDEX_TYPE_code"))
                and index_type_code != "CPI"
                and row.get("title")
            ):
                row["title"] = f"{row['title']} ({index_type_code})"

            if not row.get("indicator_code"):
                row["indicator_code"] = ind_code

        cl_unit_cache = self.metadata._codelist_cache.get("CL_UNIT", {})
        special_aggregate_codes = {"ALL", "W0", "W1", "W2"}
        for row in data_rows:
            if not row.get("unit"):
                row["unit"] = row.get("TYPE_OF_TRANSFORMATION") or row.get(
                    "TRANSFORMATION"
                )

            is_gfs_dataflow = dataflow in {"GFS", "QGFS", "GFSR", "GFSY"}
            if not row.get("unit") and is_gfs_dataflow:
                ind_code = row.get("indicator_code") or row.get("INDICATOR_code", "")
                if ind_code:
                    parts = ind_code.rsplit("_", 1)
                    if len(parts) == 2:
                        unit_code = parts[1]
                        if (
                            unit_code not in special_aggregate_codes
                            and unit_code in cl_unit_cache
                        ):
                            row["unit"] = cl_unit_cache[unit_code]

        matched_orders = {row.get("order") for row in data_rows}
        existing_net_base_labels: set[str] = set()
        for row in data_rows:
            title = row.get("title", "")
            net_idx = title.find(", Net")
            if net_idx > 0:
                existing_net_base_labels.add(title[:net_idx])

        for ind in table_structure["indicators"]:
            order = ind.get("order")
            if order is not None and order not in matched_orders:
                depth = ind.get("depth")
                if depth is None:
                    depth = _calculate_depth(ind, indicator_by_code)
                indicator_code = ind.get("indicator_code", "")
                node_id = ind.get("id", "")
                base_label = ind.get("label", ind.get("name", ""))

                if base_label in existing_net_base_labels:
                    continue

                if base_label == indicator_code and indicator_code:
                    codelist_name = indicator_codelist.get(indicator_code, "")
                    if not codelist_name:
                        for cl_code, cl_name in indicator_codelist.items():
                            if cl_code.startswith(indicator_code + "_"):
                                codelist_name = cl_name
                                break
                    if codelist_name:
                        if ", " in codelist_name:
                            name_parts = codelist_name.split(", ")
                            unit_patterns = [
                                "US dollar",
                                "Percent",
                                "Euro",
                                "Domestic currency",
                                "SDR",
                                "Yen",
                                "Pound",
                                "Yuan",
                                "National currency",
                                "Basis points",
                                "Units",
                            ]
                            fsi_tags = ["(Core FSI)", "(Additional FSI)"]
                            if any(name_parts[-1].startswith(u) for u in unit_patterns):
                                name_parts = name_parts[:-1]
                            name_parts = [p for p in name_parts if p not in fsi_tags]
                            deduped: list = []
                            for p in name_parts:
                                if not deduped or deduped[-1] != p:
                                    deduped.append(p)
                            base_label = ", ".join(deduped) if deduped else base_label
                        else:
                            base_label = codelist_name

                gfs_header_suffixes = [
                    "Stock positions",
                    "Transactions",
                    "Flows",
                    "Stocks",
                    "Cash basis",
                    "Transactions (cash basis of recording)",
                    "Memorandum Item",
                ]
                if base_label and ", " in base_label:
                    label_parts = base_label.split(", ")
                    while (
                        len(label_parts) > 1 and label_parts[-1] in gfs_header_suffixes
                    ):
                        label_parts = label_parts[:-1]
                    base_label = ", ".join(label_parts)

                scale = None
                unit = None
                child_indicator_code = None
                for row in data_rows:
                    if row.get("parent_id") == node_id:
                        scale = row.get("scale")
                        unit = (
                            row.get("unit")
                            or row.get("UNIT")
                            or row.get("TYPE_OF_TRANSFORMATION")
                            or row.get("TRANSFORMATION")
                        )
                        child_indicator_code = row.get("indicator_code") or row.get(
                            "INDICATOR_code"
                        )
                        break

                cl_unit = self.metadata._codelist_cache.get("CL_UNIT", {})
                special_aggregate_codes = {"ALL", "W0", "W1", "W2"}
                is_gfs_dataflow = dataflow in {"GFS", "QGFS", "GFSR", "GFSY"}
                if not unit and is_gfs_dataflow:
                    parent_id = ind.get("parent_id", "")
                    codes_to_try = [
                        child_indicator_code,
                        indicator_code,
                        parent_id,  # Parent might have the unit suffix
                    ]
                    for code_to_parse in codes_to_try:
                        if code_to_parse:
                            parts = code_to_parse.rsplit("_", 1)
                            if len(parts) == 2:
                                unit_code = parts[1]
                                if (
                                    unit_code not in special_aggregate_codes
                                    and unit_code in cl_unit
                                ):
                                    unit = cl_unit[unit_code]
                                    break

                valid_scale = scale and str(scale) != "nan"
                valid_unit = unit and str(unit) != "nan"

                if valid_scale and valid_unit:
                    header_title = f"{base_label} ({scale}, {unit})"
                elif valid_scale:
                    header_title = f"{base_label} ({scale})"
                elif valid_unit:
                    header_title = f"{base_label} ({unit})"
                else:
                    header_title = base_label

                if indicator_code and "_" in indicator_code:
                    first_part = indicator_code.split("_")[0]
                    if first_part in sector_codelist:
                        sector_name = sector_codelist.get(first_part, "")
                        if sector_name:
                            header_title = f"{sector_name}, {header_title}"

                header_row = {
                    "order": order,
                    "level": depth,  # Use calculated depth for proper indentation
                    "parent_id": ind.get("parent_id"),
                    "hierarchy_node_id": node_id,  # Hierarchy node ID for parent matching
                    "series_id": ind.get("series_id", ""),
                    "title": header_title,
                    "indicator_code": indicator_code,
                    "is_category_header": True,  # Flag to identify headers
                    "scale": scale,
                    "unit": unit,
                }
                data_rows.append(header_row)

        order_series_counts: dict = defaultdict(set)
        order_series_idx: dict = {}
        for row in data_rows:
            order = row.get("order")
            series_id = row.get("series_id", "")
            if order is not None:
                order_series_counts[order].add(series_id)
        for row in data_rows:
            order = row.get("order")
            series_id = row.get("series_id", "")
            if order is not None and len(order_series_counts[order]) > 1:
                key = (order, series_id)
                if key not in order_series_idx:
                    order_series_idx[key] = len(
                        [k for k in order_series_idx if k[0] == order]
                    )
                sub_idx = order_series_idx[key]
                row["order"] = float(order) + (sub_idx * 0.001)

        data_rows.sort(key=lambda x: x.get("order", float("inf")))

        cleaned_rows: list = []
        for row in data_rows:
            cleaned_row = {
                k: v for k, v in row.items() if k not in ["indicator_codes", "label"]
            }

            ordered_row: dict = {}
            for col in priority_columns:
                if col in cleaned_row:
                    ordered_row[col] = cleaned_row.pop(col)

            ordered_row.update(cleaned_row)
            cleaned_rows.append(ordered_row)

        all_metadata = data_result.get("metadata", {})
        dataset_metadata = all_metadata.pop("dataset", {})

        if dataset_metadata:
            table_metadata["dataflow_name"] = dataset_metadata.get("dataflow_name", "")
            table_metadata["dataflow_description"] = dataset_metadata.get(
                "dataflow_description", ""
            )
            for key in [
                "keywords",
                "source",
                "source_url",
                "publisher",
                "department",
                "contact_point",
                "license",
                "suggested_citation",
                "short_source_citation",
                "full_source_citation",
                "publication_date",
                "last_updated",
                "methodology_notes",
                "topics",
            ]:
                if key in dataset_metadata:
                    table_metadata[key] = dataset_metadata[key]

        return {
            "table_metadata": table_metadata,
            "data": cleaned_rows,  # List of dicts with hierarchy ordering
            "series_metadata": all_metadata,  # Series-level metadata keyed by series_id
        }

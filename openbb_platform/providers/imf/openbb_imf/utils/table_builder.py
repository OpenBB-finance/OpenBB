"""IMF Table Builder - Handles hierarchical table data fetching with validation."""

# pylint: disable=C0302,C0103,R0903,R0911,R0912,R0913,R0914,R0915,R0917,R1702,W0212
# flake8: noqa: PLR0911,PLR0912,PLR0913,PLR0917

import warnings
from collections import defaultdict
from datetime import datetime

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_imf.utils.helpers import parse_codelist_id_from_urn


def _calculate_depth(
    indicator: dict, indicator_by_code: dict, visited: set | None = None
) -> int:
    """
    Calculate the actual depth of an indicator by tracing its parent_id chain.

    This provides proper hierarchical indentation where children are always
    indented more than their parents, unlike the 'level' field which only
    distinguishes top-level (0) from nested (1+).

    Args:
        indicator: The indicator dictionary with 'indicator_code' and 'parent_id' fields.
        indicator_by_code: Lookup dictionary mapping indicator_code to indicator dict.
        visited: Set of already visited codes to prevent infinite loops.

    Returns:
        The depth (0 for root nodes, 1+ for nested nodes based on parent chain length).
    """
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
    """
    Handles fetching and organizing IMF data according to hierarchical presentation tables.

    This class validates dimension constraints and builds properly ordered tabular data
    with hierarchy information (order, level, parent_id) embedded in each row.
    """

    def __init__(self):
        """Initialize the table builder with its own query builder instance."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        self.query_builder = ImfQueryBuilder()
        self.metadata = self.query_builder.metadata

    def _validate_dimension_constraints(self, dataflow: str, **kwargs) -> None:
        """
        Validate that the provided dimension parameter combinations are valid according
        to IMF API constraints. Delegates to query_builder.validate_dimension_constraints.

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

        This method allows flexible querying of hierarchical data by depth level,
        parent group, or specific indicators. This avoids URL length issues when
        fetching large tables.

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
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        # Parse dataflow_id::table_id format if provided
        if table_id and "::" in table_id:
            parts = table_id.split("::", 1)
            parsed_dataflow = parts[0]
            parsed_table_id = parts[1]
            # If dataflow was also provided, validate it matches
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

        # Validate parameter combinations using progressive helper
        if kwargs or start_date or end_date:
            self._validate_dimension_constraints(
                dataflow, start_date=start_date, end_date=end_date, **kwargs
            )

        # If table_id not provided, auto-select if only one table available
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
            # Filter to specific indicator codes
            indicator_set = (
                {indicators} if isinstance(indicators, str) else set(indicators)
            )
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("indicator_code") in indicator_set
            ]
        elif parent_id is not None:
            # Filter by parent_id
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("parent_id") == parent_id
            ]
        elif depth is not None:
            # Filter by depth
            filtered_hierarchy_entries = [
                entry
                for entry in filtered_hierarchy_entries
                if entry.get("depth") == depth
            ]

        # Extract entries with actual indicator codes (skip pure groups with no code)
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
                continue

            dimension_id = entry.get("dimension_id")

            if not dimension_id:
                # Parse codelist ID from the code_urn
                codelist_id = parse_codelist_id_from_urn(code_urn)

                if not codelist_id:
                    # Fallback: if we can't parse code_urn, skip this entry
                    warnings.warn(
                        f"Could not parse codelist from code_urn for {indicator_code}: {code_urn}",
                        OpenBBWarning,
                    )
                    continue

                # Skip known meta/label codelists that are structural grouping nodes
                if "_LABELS" in codelist_id or "_TABLE_LEVEL" in codelist_id:
                    continue

                # Map codelist to dimension
                if codelist_id not in codelist_to_dimension_cache:
                    dimension_id = self.metadata._get_dimension_for_codelist(
                        dataflow, codelist_id
                    )
                    # Fallback: infer dimension from known patterns in codelist name
                    if not dimension_id:
                        codelist_upper = codelist_id.upper()
                        # Check for common dimension keywords in the codelist name
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
                        # Get actual dimension IDs from the DSD
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
                                # Find matching dimension in DSD
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

            # Add code to the appropriate dimension
            if indicator_code not in dimension_codes[dimension_id]:
                dimension_codes[dimension_id].append(indicator_code)
                # Track depth for constraint URL length optimization
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
        # Some hierarchies can legitimately contain multiple nodes with the same
        # (indicator_code, parent_code) (e.g., BOP Credit vs Debit variants under a Net parent),
        # so store a list and disambiguate later.
        # Key: (indicator_code, parent_code) e.g., ("O", "A_P") vs ("O", "L_P")
        hierarchy_by_composite_key: dict[tuple[str, str], list[dict]] = defaultdict(
            list
        )
        parents_by_indicator_code: dict[str, set[str]] = defaultdict(set)

        # Build indicator_by_code lookup for depth calculation
        indicator_by_code = {}
        for ind in table_structure["indicators"]:
            code = ind.get("indicator_code")
            if code:
                indicator_by_code[code] = ind

        dataflow_obj = self.metadata.dataflows.get(dataflow, {})
        # Series ID prefix in the new format: dataflow::
        series_id_prefix = f"{dataflow}::"

        # Build dimension order mapping (needed for fallback matching)
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

            # All nodes (groups and leaves) have order and can have data
            order_value = ind.get("order")

            if order_value is None:
                continue

            # The 'depth' field is calculated during hierarchy parsing
            depth = ind.get("depth")

            if depth is None:
                depth = _calculate_depth(ind, indicator_by_code)

            # Also resolve parent_id from node ID to indicator code for proper parent tracking
            parent_node_id = ind.get("parent_id")
            parent_indicator_code = None

            if parent_node_id:
                # parent_id may be a full node ID (CL_BOP_ACCOUNTING_ENTRY___L_P)
                # or just an indicator code (L_P). Handle both cases.
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

            # Store composite key lookup for indicators with same code but different parents
            # This handles cases like "Other investment" under both Assets (A_P) and Liabilities (L_P)
            if parent_indicator_code:
                composite_key = (indicator_code, parent_indicator_code)
                hierarchy_by_composite_key[composite_key].append(hierarchy_info)
                parents_by_indicator_code[indicator_code].add(parent_indicator_code)

            # Both groups and leaves can have data and should be matched
            if series_id := ind.get("series_id"):
                hierarchy_by_series_id[series_id] = hierarchy_info
                # "IIP::A_P_D" (dataflow::codes)
                # "IMF_STA_IIP_A_P_D" (agency_dataflow_codes)
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

        # Filter dimension codes against available constraints given user's kwargs
        try:
            builder = ImfParamsBuilder(dataflow)
            dims_in_order = builder._get_dimensions_in_order()
            dim_id_map = {d.lower(): d for d in dims_in_order}

            # Country-like dimension aliases - user can pass 'country' and it maps to
            # whichever country dimension this dataflow uses
            country_dims = ["COUNTRY", "REF_AREA", "JURISDICTION", "COUNTERPART_AREA"]
            for country_dim in country_dims:
                if country_dim in dims_in_order:
                    dim_id_map["country"] = country_dim
                    break

            # Indicator-like dimension aliases
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

            # Replace fetch_kwargs with normalized kwargs (uppercase dimension IDs)
            fetch_kwargs = normalized_kwargs.copy()
            # Track dimensions with zero valid codes (hierarchy mismatch)
            empty_dimensions: list[str] = []
            # Process dimensions in order, setting both user kwargs and hierarchy codes
            for dim_id in dims_in_order:
                # If user provided this dimension, set it and add to fetch_kwargs
                if dim_id in normalized_kwargs and dim_id not in dimension_codes:
                    # Validate user-provided value against available options
                    user_value = normalized_kwargs[dim_id]

                    # Skip validation for wildcard - it's always valid
                    if user_value != "*":
                        available_options = builder.get_options_for_dimension(dim_id)
                        available_values = {opt["value"] for opt in available_options}

                        # Handle multi-value selections (e.g., "USA+CAN")
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
                            # Build prior selections for context
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
                # If this dimension has hierarchy codes, filter them against available
                elif dim_id in dimension_codes:
                    # Check if user explicitly provided this dimension (e.g., INDICATOR='*')
                    # If so, use their value for the builder but still process hierarchy codes
                    user_override = normalized_kwargs.get(dim_id)
                    codes = dimension_codes[dim_id]
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = {opt["value"] for opt in available_options}
                    filtered_codes = [c for c in codes if c in available_values]
                    # If no exact matches, try prefix matching for INDICATOR dimension
                    # Hierarchies may use base codes (FSI688_TREGK) while dataflow has
                    # suffixed codes (FSI688_TREGK_USD, FSI688_TREGK_EUR, FSI688_TREGK_XDC)
                    if not filtered_codes and dim_id in {"INDICATOR", "CLASSIFICATION"}:
                        # Find all available codes that start with a hierarchy code
                        for hier_code in codes:
                            matching_codes = [
                                av
                                for av in available_values
                                if av.startswith(hier_code + "_") or av == hier_code
                            ]
                            filtered_codes.extend(matching_codes)
                        # Remove duplicates while preserving order
                        filtered_codes = list(dict.fromkeys(filtered_codes))

                    if filtered_codes:
                        # Build the joined codes string
                        joined_codes = "+".join(filtered_codes)
                        # Check if codes portion would be too long for IMF API
                        MAX_CODES_LENGTH = 850
                        use_wildcard_for_fetch = len(joined_codes) > MAX_CODES_LENGTH

                        if use_wildcard_for_fetch:
                            # Use wildcard for data fetch - will filter results post-request
                            fetch_kwargs[dim_id] = "*"
                            # Store the actual codes we want for post-fetch filtering
                            if "_indicator_codes_to_filter" not in fetch_kwargs:
                                fetch_kwargs["_indicator_codes_to_filter"] = set()
                            fetch_kwargs["_indicator_codes_to_filter"].update(
                                filtered_codes
                            )
                        else:
                            # URL length is OK - include codes directly
                            fetch_kwargs[dim_id] = joined_codes

                        # For constraint checking, limit to depth 0-1 codes when codes
                        # string is too long.
                        if len(joined_codes) > MAX_CODES_LENGTH:
                            # Get depth info for hierarchy codes
                            code_depths = dict(
                                dimension_codes_with_depth.get(dim_id, [])
                            )
                            # Filter to level 0 and 1 only (group/category codes)
                            shallow_codes = [
                                c for c in codes if code_depths.get(c, 0) <= 1
                            ]
                            # Only use shallow codes if they exist AND are in available
                            shallow_available = [
                                c for c in shallow_codes if c in available_values
                            ]
                            # Fall back to truncated codes if no shallow codes available
                            if shallow_available:
                                constraint_key = "+".join(shallow_available)
                                # Check if shallow codes are still too long
                                if len(constraint_key) > MAX_CODES_LENGTH:
                                    constraint_key = "*"
                            else:
                                # Truncate to fit URL limit
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
                                # Final safety check
                                if len(constraint_key) > MAX_CODES_LENGTH:
                                    constraint_key = "*"
                        else:
                            constraint_key = joined_codes

                        builder_key = user_override if user_override else constraint_key
                        builder.set_dimension((dim_id, builder_key))
                    else:
                        # No codes available for this dimension given prior constraints
                        # This means the table's indicators don't exist for this country/period
                        empty_dimensions.append(dim_id)
                        # Build context for error message
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

            # If ALL indicator dimensions had zero matches, the hierarchy doesn't apply
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
                # The hierarchy's indicator codes couldn't be mapped
                # this table doesn't work for this dataflow
                raise ValueError(
                    f"Table indicators could not be mapped to dimension(s) {unmapped_indicator_dims}. "
                    f"The hierarchy's indicator codes are not compatible with dataflow '{dataflow}'. "
                    f"Hierarchy had codes from codelists: {list(codelist_to_dimension_cache.keys())}, "
                    f"but none matched the dataflow's indicator dimension."
                )

            if missing_indicator_dims and not any(
                d in fetch_kwargs for d in indicator_dims_set
            ):
                # Use the same error format as query_builder validation
                for dim_id in missing_indicator_dims:
                    invalid_values = dimension_codes.get(dim_id, [])
                    # Get available values for this dimension
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = sorted(  # type: ignore
                        {opt["value"] for opt in available_options}
                    )
                    # Build prior selections dict
                    prior_selections = {
                        d: normalized_kwargs.get(d)
                        for d in dims_in_order
                        if d in normalized_kwargs
                        and dims_in_order.index(d) < dims_in_order.index(dim_id)
                    }
                    raise ValueError(
                        f"Invalid value(s) for dimension '{dim_id}': {invalid_values}. "
                        f"Given prior selections {prior_selections}, "
                        f"available values are: {available_values}"
                    )

            # Handle any dimension codes not in the standard order
            for dim_id, codes in dimension_codes.items():
                if dim_id not in dims_in_order and dim_id not in fetch_kwargs:
                    # Validate these codes against available options
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = {opt["value"] for opt in available_options}
                    filtered_codes = [c for c in codes if c in available_values]

                    # If no exact matches, try prefix matching
                    if not filtered_codes:
                        for hier_code in codes:
                            matching_codes = [
                                av
                                for av in available_values
                                if av.startswith(hier_code + "_") or av == hier_code
                            ]
                            filtered_codes.extend(matching_codes)
                        # Deduplicate
                        filtered_codes = list(dict.fromkeys(filtered_codes))

                    if filtered_codes:
                        # Check if URL would be too long
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
                        # No valid codes - this dimension has no data for given constraints
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
            # Check if this is a validation error - don't suppress those
            error_msg = str(e)
            if (
                "Invalid value(s) for dimension" in error_msg
                or "not compatible with dataflow" in error_msg
            ):
                raise ValueError(error_msg) from e
            # Fallback: use all codes if progressive validation fails
            warnings.warn(
                f"Progressive constraint filtering failed: {e}. Using unfiltered codes.",
                OpenBBWarning,
            )
            for dim_id, codes in dimension_codes.items():
                if dim_id not in fetch_kwargs:
                    # Check if URL would be too long
                    joined_codes = "+".join(codes)
                    if len(joined_codes) > 1500:
                        fetch_kwargs[dim_id] = "*"
                        # Store codes for post-fetch filtering
                        if "_indicator_codes_to_filter" not in fetch_kwargs:
                            fetch_kwargs["_indicator_codes_to_filter"] = set()
                        fetch_kwargs["_indicator_codes_to_filter"].update(codes)
                    else:
                        fetch_kwargs[dim_id] = joined_codes

        if "INDICATOR" in fetch_kwargs and fetch_kwargs["INDICATOR"] != "*":
            # Find a dimension after INDICATOR to query - this triggers the constraint call
            next_dim = builder.get_next_dimension_to_select()
            if next_dim:
                _ = builder.get_options_for_dimension(next_dim)

        # The constraints response from the LAST get_options_for_dimension call
        # contains time_period_start and time_period_end in the annotations.
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
                                return None
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
                            # Date parsing failed - skip validation
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

        # Extract post-fetch filter codes before passing to fetch_data
        indicator_codes_to_filter = fetch_kwargs.pop("_indicator_codes_to_filter", None)

        # Skip validation in fetch_data since we already validated progressively
        data_result = self.query_builder.fetch_data(
            dataflow=dataflow,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            _skip_validation=True,  # We already validated above
            **fetch_kwargs,
        )

        # Enrich data rows with hierarchical ordering information
        data_rows = data_result.get("data", [])

        # Post-fetch filtering: if we used wildcard for INDICATOR dimension,
        # filter to only include rows whose indicator code is in our hierarchy
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
                # Update the data_result with filtered rows
                data_result["data"] = data_rows

        # Define column order: hierarchy fields first, then the rest
        priority_columns = ["order", "level", "parent_id", "series_id"]

        # Determine which dimension contains the indicator code for this dataflow
        # Different dataflows use different dimension names (INDICATOR, COICOP_1999, etc.)
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
            # Try each possible indicator field
            indicator_code = ""
            for field in indicator_code_fields:
                indicator_code = row.get(field, "")
                if indicator_code:
                    break

            if not indicator_code:
                continue

            # Multi-stage hierarchy matching:
            # 1. Try exact series_id match (includes all dimension codes)
            # 2. Try sorted codes match (order-agnostic)
            # 3. Fall back to indicator code lookup
            hier_info = None
            row_series_id = row.get("series_id", "")

            # Stage 1: Exact series_id match
            if row_series_id:
                hier_info = hierarchy_by_series_id.get(row_series_id)

            # Stage 2: Sorted codes match (handles dimension order differences)
            if not hier_info and row_series_id and "::" in row_series_id:
                codes_part = row_series_id.split("::", 1)[1]
                if codes_part:
                    sorted_codes = "_".join(sorted(codes_part.split("_")))
                    hier_info = hierarchy_by_sorted_codes.get(sorted_codes)

            # Stage 2.25: Constructed sorted-codes match when series_id is missing.
            # Some IMF responses omit or vary series_id formats, but the hierarchy encodes
            # series IDs like "..._BOP_DB_T_D74XEF". For BOP-style tables, we can reconstruct
            # a comparable key from the row's indicator + accounting entry codes.
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

            # Stage 2.5: Composite key lookup for same indicator with different parents
            # This handles cases like "Other investment" appearing under both Assets (A_P)
            # and Liabilities (L_P) in BOP/IIP data
            # Stage 2.5: Composite key lookup for same indicator with different parents
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
                        haystack = f"{cand.get('hierarchy_node_id','')} {cand.get('hierarchy_series_id','')}".upper()
                        if any(m in haystack for m in markers):
                            return cand

                    return candidates[0]

                # Check for BOP_ACCOUNTING_ENTRY dimension which distinguishes Assets vs Liabilities.
                composite_key = (indicator_code, bop_entry_code)
                hier_info = _choose_from_candidates(
                    hierarchy_by_composite_key.get(composite_key, []), bop_entry_code
                )

                # BOP Credit/Debit rows are typically grouped under a Net parent in the IMF hierarchy.
                # The hierarchy's discriminator for these rows is the Net node (e.g., NETCD_T), not
                # the row's accounting entry code (CD_T/DB_T). Prefer the hierarchy's Net parent.
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

            # Stage 3: Indicator code lookup (single dimension)
            # BUT: if we have a bop_entry_code, don't use generic indicator match
            # as it would place the row under the wrong section (e.g., Assets instead of Liabilities)
            if not hier_info and not bop_entry_code:
                hier_info = hierarchy_order_map.get(indicator_code)

            # Stage 4: Prefix matching for unit-suffixed codes
            # (e.g., FSI688_TREGK_USD → FSI688_TREGK)
            if not hier_info:
                for hier_code, info in hierarchy_order_map.items():
                    if indicator_code.startswith(hier_code + "_"):
                        hier_info = info
                        break

            if not hier_info:
                continue

            # Apply hierarchy info to row
            row["order"] = hier_info["order"]
            row["level"] = hier_info["level"]
            row["parent_id"] = hier_info["parent_id"]
            row["parent_code"] = hier_info["parent_code"]
            row["label"] = hier_info["label"]
            row["hierarchy_node_id"] = hier_info.get("hierarchy_node_id")

        # Filter out rows that didn't get matched (no hierarchy info)
        data_rows = [row for row in data_rows if row.get("order") is not None]

        # Get the indicator codelist for name lookups
        # The hierarchy's codelist may be a label codelist, so we need to get the
        # actual INDICATOR dimension's codelist from the dataflow's DSD
        indicator_codelist = {}
        indicator_codelist_id = None  # Initialize to avoid UnboundLocalError

        # Get the DSD for this dataflow
        df_obj = self.metadata.dataflows.get(dataflow, {})
        dsd_id = df_obj.get("structureRef", {}).get("id")
        dsd_id = df_obj.get("structureRef", {}).get("id")
        if dsd_id:
            dsd = self.metadata.datastructures.get(dsd_id, {})
            dimensions = dsd.get("dimensions", []) if isinstance(dsd, dict) else []

            # Find ANY indicator-like dimension and get its codelist
            # Different dataflows use different dimension names for indicators
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

        # Get sector codelist for MFS-style indicator differentiation
        # MFS indicators like S121_A_ACO_NRES, ODCORP_A_ACO_NRES have the same label
        # but different sector prefixes - we need to prepend sector names to differentiate
        sector_codelist = self.metadata._codelist_cache.get("CL_SECTOR", {})

        # Mark data rows as non-headers and set title from indicator name
        for row in data_rows:
            row["is_category_header"] = False

            # Get indicator code (the actual code with unit suffix like FSI688_TREGK_USD)
            ind_code = row.get("INDICATOR_code", "")

            # Look up the proper name from the codelist
            ind_name = indicator_codelist.get(ind_code, "")

            if ind_name and ", " in ind_name:
                name_parts = ind_name.split(", ")
                # Unit patterns to strip from the end
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

                # GFS classification suffixes - these indicate data type and should be
                # stripped but the rest of the name should be preserved
                # e.g., "Financial assets, Stock positions" -> "Financial assets"
                # GFS classification suffixes - these indicate recording basis/type and should be
                # stripped, but debtor/creditor info should be KEPT as it's meaningful
                # e.g., "Revenue, Transactions (cash basis), Cash basis" -> "Revenue"
                # e.g., "Liabilities, Foreign Creditors, Cash basis" -> "Liabilities, Foreign Creditors"
                gfs_recording_suffixes = [
                    "Stock positions",
                    "Transactions",
                    "Flows",
                    "Stocks",
                    "Cash basis",
                    "Transactions (cash basis of recording)",
                    "Memorandum Item",
                ]

                # FSI classification tags - these are metadata, not meaningful names
                # e.g., "(Core FSI)", "(Additional FSI)" should be stripped
                fsi_classification_tags = ["(Core FSI)", "(Additional FSI)"]

                # Strip unit from end if present
                if any(name_parts[-1].startswith(u) for u in unit_patterns):
                    name_parts = name_parts[:-1]

                # Strip GFS recording/classification suffixes from the end (can be multiple)
                while len(name_parts) > 1 and name_parts[-1] in gfs_recording_suffixes:
                    name_parts = name_parts[:-1]

                # Strip FSI classification tags from any position
                name_parts = [p for p in name_parts if p not in fsi_classification_tags]

                # Remove duplicate consecutive parts
                # e.g., "Loans to X, Loans to X" -> "Loans to X"
                deduped_parts: list = []
                for p in name_parts:
                    if not deduped_parts or deduped_parts[-1] != p:
                        deduped_parts.append(p)
                name_parts = deduped_parts

                if len(name_parts) >= 1:
                    ind_name = ", ".join(name_parts)

            # For MFS-style indicators, check if we need to add sector prefix
            # to differentiate otherwise identical labels (e.g., S121_A_ACO_NRES vs ODCORP_A_ACO_NRES)
            sector_prefix = None
            is_gfs_indicator = (
                indicator_codelist_id and indicator_codelist_id.startswith("CL_GFS")
            )

            # For GFS indicators with multiple SECTOR values (SECTOR="*"), get sector from SECTOR_code
            # This differentiates rows like "General government" vs "Central government" for same indicator
            if is_gfs_indicator:
                sector_code = row.get("SECTOR_code")
                if sector_code and sector_code in sector_codelist:
                    sector_prefix = sector_code
            elif ind_code and "_" in ind_code:
                # For MFS indicators, extract sector prefix from indicator code
                first_part = ind_code.split("_")[0]
                # Check if it's a known sector code
                if first_part in sector_codelist:
                    sector_prefix = first_part

            # For codelists that store full comma-separated path labels (e.g., CL_IRFCL_INDICATOR_PUB),
            # prefer the hierarchy label which contains just the node-level label.
            # The hierarchy structure already provides parent-child context, so we don't need
            # the full path repeated in each label.
            uses_path_labels = indicator_codelist_id and (
                indicator_codelist_id.endswith("_INDICATOR_PUB")
                or indicator_codelist_id.endswith("_INDICATOR_DEFAULT_PUB")
                or indicator_codelist_id == "CL_DIP_INDICATOR"
            )

            # Set the title - for path-label codelists, prefer hierarchy label
            if uses_path_labels and row.get("label"):
                # Hierarchy already has proper node-level label
                row["title"] = row["label"]
            elif ind_name:
                # If we have a sector prefix, prepend the sector name to differentiate
                if sector_prefix:
                    sector_name = sector_codelist.get(sector_prefix, "")
                    if sector_name:
                        row["title"] = f"{sector_name}, {ind_name}"
                    else:
                        row["title"] = ind_name
                else:
                    row["title"] = ind_name

            # Fallback: prefer hierarchy label if no title was set.
            # This keeps output consistent with the IMF hierarchy (source of truth)
            # when codelist lookups are unavailable or incomplete.
            if not row.get("title") and row.get("label"):
                row["title"] = row["label"]

            # Final fallback: if still no title, use the indicator code itself.
            # This ensures every row has some identifying label.
            if not row.get("title") and ind_code:
                readable_code = ind_code.replace("_", " ")
                row["title"] = readable_code

            # For BOP data, append the accounting entry type (Credit/Debit/Net) to title
            # This differentiates rows like "Goods, Credit" vs "Goods, Debit" vs "Goods"
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

            # For IIP data without explicit BOP_ACCOUNTING_ENTRY, extract asset/liability
            # context from series_id pattern (e.g., _A_P_ for Assets, _L_P_ for Liabilities)
            # This differentiates rows like "Other investment (Assets)" vs
            # "Other investment (Liabilities)" that would otherwise have identical titles
            if not bop_entry and row.get("title"):
                series_id = row.get("series_id", "")
                title_lower = row["title"].lower()
                # Check for IIP-style series_id patterns
                # _A_P_ or _A_P at end = Assets position
                # _L_P_ or _L_P at end = Liabilities position
                has_asset_context = "asset" in title_lower
                has_liab_context = "liabilit" in title_lower

                if not has_asset_context and not has_liab_context:
                    # Series ID pattern: IMF_STA_IIP_A_P_xxx (Assets) or IMF_STA_IIP_L_P_xxx (Liabilities)
                    if "_IIP_A_P_" in series_id or "_IIP_A_P" in series_id:
                        row["title"] = f"{row['title']} (Assets)"
                    elif "_IIP_L_P_" in series_id or "_IIP_L_P" in series_id:
                        row["title"] = f"{row['title']} (Liabilities)"

            # For IIPCC currency composition data, append currency to title
            # This differentiates rows by currency (Euro, US dollar, Other currencies, etc.)
            currency_code = row.get("CURRENCY_code")
            currency_label = row.get("CURRENCY")
            unit_code = row.get("unit_code") or row.get("UNIT_MEASURE_code")
            if currency_code and currency_label and row.get("title"):
                # Don't append if currency is the same as the unit (e.g., both USD)
                skip_currencies = {"_T", "W0", "W1", "W2", "ALL"}
                if currency_code not in skip_currencies and currency_code != unit_code:
                    row["title"] = f"{row['title']} ({currency_label})"

            # For CPI data with multiple INDEX_TYPEs (CPI, HICP, etc.), append the index type
            if (
                dataflow == "CPI"
                and (index_type_code := row.get("INDEX_TYPE_code"))
                and index_type_code != "CPI"
                and row.get("title")
            ):
                row["title"] = f"{row['title']} ({index_type_code})"

            # Set indicator_code from INDICATOR_code if not already set
            # This ensures data rows have indicator_code just like category headers
            if not row.get("indicator_code"):
                row["indicator_code"] = ind_code

        # Extract unit for data rows when unit is missing
        # This handles dataflows like QGFS/GFS where unit is embedded in indicator code
        # and CPI where unit comes from TYPE_OF_TRANSFORMATION
        cl_unit_cache = self.metadata._codelist_cache.get("CL_UNIT", {})
        # Skip special aggregate codes that conflict with currency codes
        special_aggregate_codes = {"ALL", "W0", "W1", "W2"}
        for row in data_rows:
            if not row.get("unit"):
                # Try TYPE_OF_TRANSFORMATION or TRANSFORMATION fields first (CPI, etc.)
                row["unit"] = row.get("TYPE_OF_TRANSFORMATION") or row.get(
                    "TRANSFORMATION"
                )

            # Still no unit? Try extracting from indicator code suffix (QGFS/GFS)
            # BUT: Only do this for GFS-style dataflows, NOT for MFS where suffixes
            # like SVC mean "Survey Vertical Check", not currency codes
            is_gfs_dataflow = dataflow in {"GFS", "QGFS", "GFSR", "GFSY"}
            if not row.get("unit") and is_gfs_dataflow:
                ind_code = row.get("indicator_code") or row.get("INDICATOR_code", "")
                if ind_code:
                    parts = ind_code.rsplit("_", 1)
                    if len(parts) == 2:
                        unit_code = parts[1]
                        # Only use as unit if it's a real unit code in CL_UNIT
                        # Skip special aggregate codes like ALL, W0, W1, W2 which are
                        # dimension codes (e.g., "All entities") not unit codes
                        if (
                            unit_code not in special_aggregate_codes
                            and unit_code in cl_unit_cache
                        ):
                            row["unit"] = cl_unit_cache[unit_code]

        matched_orders = {row.get("order") for row in data_rows}
        existing_net_base_labels: set[str] = set()
        for row in data_rows:
            title = row.get("title", "")
            # Find ", Net" anywhere in title (not just at end)
            net_idx = title.find(", Net")
            if net_idx > 0:
                # Everything before ", Net" is the base label
                existing_net_base_labels.add(title[:net_idx])

        for ind in table_structure["indicators"]:
            order = ind.get("order")
            if order is not None and order not in matched_orders:
                # Use depth from hierarchy metadata, fall back to _calculate_depth only if needed
                # This matches the pattern used in the data matching loop above
                depth = ind.get("depth")
                if depth is None:
                    depth = _calculate_depth(ind, indicator_by_code)
                indicator_code = ind.get("indicator_code", "")
                node_id = ind.get("id", "")
                base_label = ind.get("label", ind.get("name", ""))

                # Skip creating synthetic header if there's a matching ", Net" data row
                # In BOP-style tables, "Goods, Net" serves as the header for the Goods group
                # so we don't need a separate "Goods" header
                if base_label in existing_net_base_labels:
                    continue

                # If label is just the indicator code (no proper name), try to look up
                # a proper name from the codelist. The codelist may have unit-suffixed
                # codes (e.g., "AQ1_XDC") while hierarchy uses base codes (e.g., "AQ1").
                if base_label == indicator_code and indicator_code:
                    # Try direct lookup first
                    codelist_name = indicator_codelist.get(indicator_code, "")
                    if not codelist_name:
                        # Try prefix matching - find any code that starts with this code
                        for cl_code, cl_name in indicator_codelist.items():
                            if cl_code.startswith(indicator_code + "_"):
                                codelist_name = cl_name
                                break
                    if codelist_name:
                        # Process the codelist name the same way as data row titles
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
                            # Strip unit suffix
                            if any(name_parts[-1].startswith(u) for u in unit_patterns):
                                name_parts = name_parts[:-1]
                            # Strip FSI classification tags
                            name_parts = [p for p in name_parts if p not in fsi_tags]
                            # Deduplicate consecutive parts
                            deduped: list = []
                            for p in name_parts:
                                if not deduped or deduped[-1] != p:
                                    deduped.append(p)
                            base_label = ", ".join(deduped) if deduped else base_label
                        else:
                            base_label = codelist_name

                # Strip GFS classification suffixes from header labels
                # These come from codelists and may have suffixes like "Transactions, Cash basis, Memorandum Item"
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

                # Try to find scale/unit from first child data row
                scale = None
                unit = None
                child_indicator_code = None
                # Look for children by finding data rows with matching parent_id
                # parent_id on data rows is the node ID (e.g., "BYINS"), not indicator_code
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

                # If unit is still None, try to extract from indicator code suffix
                # For dataflows like QGFS/GFS, indicator codes end with unit suffix
                # e.g., G1_T_XDC -> XDC (Domestic currency), G1_T_USD -> USD
                cl_unit = self.metadata._codelist_cache.get("CL_UNIT", {})
                # Skip special aggregate codes that conflict with currency codes
                special_aggregate_codes = {"ALL", "W0", "W1", "W2"}
                # Only extract unit from code suffix for GFS/QGFS dataflows
                is_gfs_dataflow = dataflow in {"GFS", "QGFS", "GFSR", "GFSY"}
                if not unit and is_gfs_dataflow:
                    # Try: child code -> header's own code -> parent code
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
                                # Only use as unit if it's a real unit code in CL_UNIT
                                # Skip special aggregate codes like ALL, W0, W1, W2 which are
                                # dimension codes (e.g., "All entities") not unit codes
                                if (
                                    unit_code not in special_aggregate_codes
                                    and unit_code in cl_unit
                                ):
                                    unit = cl_unit[unit_code]
                                    break

                # Format header title with scale and unit if available
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

                # For MFS-style indicators, prepend sector name to differentiate
                # headers with the same label but different sector prefixes
                if indicator_code and "_" in indicator_code:
                    first_part = indicator_code.split("_")[0]
                    if first_part in sector_codelist:
                        sector_name = sector_codelist.get(first_part, "")
                        if sector_name:
                            header_title = f"{sector_name}, {header_title}"

                # This is a group/category header without its own data point
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

        # Handle duplicate orders - create sub-orders for rows with same base order
        # This is needed for multi-dimension data like IIPCC where different currencies
        # map to the same indicator hierarchy node but need distinct rows
        # Convert orders like [2, 2, 2, 2, 2] to [2.0, 2.1, 2.2, 2.3, 2.4]
        order_series_counts: dict = defaultdict(set)
        order_series_idx: dict = {}
        # First pass: count unique series_ids per order
        for row in data_rows:
            order = row.get("order")
            series_id = row.get("series_id", "")
            if order is not None:
                order_series_counts[order].add(series_id)
        # Second pass: assign sub-orders only when multiple series share an order
        for row in data_rows:
            order = row.get("order")
            series_id = row.get("series_id", "")
            if order is not None and len(order_series_counts[order]) > 1:
                # Multiple series have this order - assign sub-order by series_id
                key = (order, series_id)  # type: ignore
                if key not in order_series_idx:
                    order_series_idx[key] = len(
                        [k for k in order_series_idx if k[0] == order]
                    )
                sub_idx = order_series_idx[key]
                # Use float to create sub-ordering: 2.0, 2.001, 2.002, etc.
                row["order"] = float(order) + (sub_idx * 0.001)

        # Sort by order
        data_rows.sort(key=lambda x: x.get("order", float("inf")))

        # Remove duplicate/unnecessary fields and reorder columns
        cleaned_rows: list = []
        for row in data_rows:
            # Remove indicator_codes (internal), label (duplicate of dimension labels), title (redundant)
            cleaned_row = {
                k: v for k, v in row.items() if k not in ["indicator_codes", "label"]
            }

            # Reorder: priority columns first, then rest alphabetically
            ordered_row: dict = {}
            for col in priority_columns:
                if col in cleaned_row:
                    ordered_row[col] = cleaned_row.pop(col)

            # Add remaining columns in their original order
            ordered_row.update(cleaned_row)
            cleaned_rows.append(ordered_row)

        # Extract series-level and dataset-level metadata
        all_metadata = data_result.get("metadata", {})
        dataset_metadata = all_metadata.pop("dataset", {})

        # Add dataset metadata to table_metadata
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

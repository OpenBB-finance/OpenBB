"""IMF Query Builder utilities."""

# pylint: disable=C0302,R0911,R0912,R0913,R0914,R0915,R0917,R1702,W0212
# flake8: noqa: PLR0911,PLR0912,PLR0913,PLR0917

import warnings

from openbb_imf.utils.metadata import ImfMetadata


class ImfQueryBuilder:
    """IMF Query Builder for constructing and executing SDMX REST queries."""

    def __init__(self):
        """Initialize the query builder with metadata singleton."""
        self.metadata = ImfMetadata()

    def build_url(
        self,
        dataflow: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        **kwargs,
    ) -> str:
        """Build the IMF SDMX REST API URL for data retrieval."""
        if dataflow not in self.metadata.dataflows:
            raise ValueError(f"Dataflow '{dataflow}' not found.")

        df = self.metadata.dataflows[dataflow]
        agency_id = df.get("agencyID")
        dsd_id = df.get("structureRef", {}).get("id")

        if not dsd_id or dsd_id not in self.metadata.datastructures:
            raise ValueError(f"Data structure not found for dataflow '{dataflow}'.")

        dsd = self.metadata.datastructures[dsd_id]
        all_dimensions = dsd.get("dimensions", [])
        dimension_ids = {d["id"] for d in all_dimensions if d.get("id")}
        # Create a map for case-insensitive matching of dimension IDs
        dimension_id_map = {d_id.lower(): d_id for d_id in dimension_ids}

        final_kwargs: dict = {}

        for key, value in kwargs.items():
            # Try to match the key (case-insensitive) to a known dimension ID
            matched_dim_id = dimension_id_map.get(key.lower())
            if matched_dim_id:
                final_kwargs[matched_dim_id] = value
            else:
                # If not a dimension, keep the original key
                final_kwargs[key] = value

        dimensions = sorted(
            [
                d
                for d in all_dimensions
                if d.get("id") is not None and d.get("position") is not None
            ],
            key=lambda x: int(x.get("position")),
        )
        key_parts: list = []
        # Use a set to keep track of dimensions that have been added to the key_parts
        # to avoid adding them again to query_params
        dimensions_in_key: set = set()

        for dim in dimensions:
            dim_id = dim.get("id")
            param_value = final_kwargs.get(dim_id)

            # Handle wildcards and empty values
            if (
                param_value is None
                or param_value in ["", "*"]
                or len(str(param_value)) > 1500
            ):
                key_parts.append("*")
            elif isinstance(param_value, list):
                key_parts.append("+".join(param_value))
            else:
                key_parts.append(str(param_value))
            dimensions_in_key.add(dim_id)

        key = ".".join(key_parts)

        if not agency_id:
            raise ValueError(f"Agency ID not found for dataflow '{dataflow}'.")

        url = (
            f"https://api.imf.org/external/sdmx/3.0/data/dataflow/"
            f"{agency_id}/{dataflow}/+/{key}"
        )
        # Only include parameters in query_params that are not dimensions
        query_params = {
            k: v for k, v in final_kwargs.items() if k not in dimensions_in_key
        }
        # Format dates for TIME_PERIOD filter
        frequency = (final_kwargs.get("FREQUENCY") or "").upper()

        def format_date(
            date_str: str, frequency: str, is_end_date: bool = False
        ) -> str:
            """Format date string based on frequency to match IMF TIME_PERIOD format."""
            if not date_str:
                return date_str

            # Parse the date - could be YYYY, YYYY-MM, or YYYY-MM-DD
            parts = date_str.split("-")
            year = int(parts[0])
            month = int(parts[1]) if len(parts) >= 2 else 1

            if frequency == "A" or len(parts) == 1:
                # Annual frequency or year-only input
                if is_end_date:
                    # For end date, use first day of next year
                    return f"{year + 1}-01-01"

                return f"{year}-01-01"

            if is_end_date:
                # For end date, use first day of next month
                month += 1
                if month > 12:
                    month = 1
                    year += 1

                return f"{year}-{month:02d}-01"

            return f"{year}-{month:02d}-01"

        c_params = []

        if start_date:
            formatted_start = format_date(start_date, frequency)
            c_params.append(f"ge:{formatted_start}")
        if end_date:
            formatted_end = format_date(end_date, frequency, is_end_date=True)
            c_params.append(f"le:{formatted_end}")
        if c_params:
            query_params["c[TIME_PERIOD]"] = "+".join(c_params)

        query_params = {k: v for k, v in query_params.items() if v is not None}

        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())

        url += (
            f"{'&' if '?' in url and not url.endswith('&') else '?'}"
            + "dimensionAtObservation=TIME_PERIOD&detail=full&includeHistory=false"
        )

        if limit is not None and limit > 0:
            url += f"&lastNObservations={limit}"

        return url

    def validate_dimension_constraints(self, dataflow: str, **kwargs) -> None:
        """
        Validate that the provided dimension parameter combinations are valid according
        to IMF API constraints. Uses progressive constraint checking to ensure the
        parameters are actually available for the dataflow.

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
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        try:
            builder = ImfParamsBuilder(dataflow)
            dimensions_in_order = builder._get_dimensions_in_order()

            # Build up selections progressively and validate each step
            for dim_id in dimensions_in_order:
                if dim_id in kwargs:
                    user_value = kwargs[dim_id]

                    # Normalize to list for checking
                    # Handle comma-separated or plus-separated strings
                    if isinstance(user_value, str):
                        if "," in user_value:
                            user_values = [v.strip() for v in user_value.split(",")]
                        elif "+" in user_value:
                            user_values = [v.strip() for v in user_value.split("+")]
                        else:
                            user_values = [user_value]
                    elif isinstance(user_value, list):
                        user_values = user_value
                    else:
                        user_values = [user_value] if user_value else []

                    # Filter out empty strings
                    user_values = [v for v in user_values if v]

                    if not user_values:
                        continue

                    # Skip wildcards - they're always valid
                    if user_values == ["*"] or len("+".join(user_values)) > 2000:
                        builder.set_dimension((dim_id, "*"))
                        continue

                    # Get available options for this dimension given prior selections
                    available_options = builder.get_options_for_dimension(dim_id)
                    available_values = {opt["value"] for opt in available_options}

                    # Check if user's values are valid
                    invalid_values = []
                    for val in user_values:
                        if val != "*" and val not in available_values:
                            invalid_values.append(val)

                    if invalid_values:
                        # Build helpful error message
                        prior_selections = {
                            d: kwargs.get(d)
                            for d in dimensions_in_order
                            if d in kwargs
                            and dimensions_in_order.index(d)
                            < dimensions_in_order.index(dim_id)
                        }

                        # Show all available values without truncation
                        all_values = sorted(available_values)
                        error_msg = (
                            f"Invalid value(s) for dimension '{dim_id}': {invalid_values}. "
                            f"Given prior selections {prior_selections}, "
                            f"available values are: {all_values}"
                        )
                        raise ValueError(error_msg)

                    # Set the valid value to progress the builder
                    builder.set_dimension((dim_id, user_values[0]))

            # Check time period constraints from the last dimension validation
            # The _last_constraints_response already contains contentConstraints with TIME_PERIOD info
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")

            if start_date or end_date:
                constraints = builder._last_constraints_response
                if constraints:
                    full_response = constraints.get("full_response", {})
                    data = full_response.get("data", {})

                    # Time period annotations can be in contentConstraints or dataConstraints
                    # Check both places
                    time_start = None
                    time_end = None

                    # Try contentConstraints first (primary location)
                    content_constraints = data.get("contentConstraints", [])
                    for constraint in content_constraints:
                        for annotation in constraint.get("annotations", []):
                            ann_id = annotation.get("id", "")
                            ann_title = annotation.get("title", "")
                            if ann_id == "time_period_start":
                                time_start = ann_title
                            elif ann_id == "time_period_end":
                                time_end = ann_title

                    # Fall back to dataConstraints if not found
                    if not (time_start and time_end):
                        data_constraints = data.get("dataConstraints", [])
                        for constraint in data_constraints:
                            for annotation in constraint.get("annotations", []):
                                ann_id = annotation.get("id", "")
                                ann_title = annotation.get("title", "")
                                if ann_id == "time_period_start":
                                    time_start = ann_title
                                elif ann_id == "time_period_end":
                                    time_end = ann_title

                    if time_start and time_end:
                        # Use >= because time_end represents the END of the last period
                        # e.g., time_end=2025-01-01 means data up to end of 2024
                        # So start_date=2025-01-01 would be requesting data AFTER the available range
                        if start_date and start_date >= time_end:
                            raise ValueError(
                                f"Requested start_date '{start_date}' is after the latest available data '{time_end}'. "
                                f"Available date range: {time_start} to {time_end}"
                            )
                        if end_date and end_date <= time_start:
                            raise ValueError(
                                f"Requested end_date '{end_date}' is before the earliest available data '{time_start}'. "
                                f"Available date range: {time_start} to {time_end}"
                            )

        except KeyError as e:
            # Dataflow not found or other metadata issue - let it pass through
            warnings.warn(
                f"Could not validate constraints for dataflow '{dataflow}': {e}",
                OpenBBWarning,
            )

    def fetch_data(
        self,
        dataflow: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        _skip_validation: bool = False,
        **kwargs,
    ) -> dict:
        """Fetch data from the IMF API for a given dataflow and parameters.

        Uses XML format for data retrieval as the JSON format has data truncation issues.

        Parameters
        ----------
        dataflow : str
            The dataflow ID
        start_date : str | None
            Start date for the query
        end_date : str | None
            End date for the query
        _skip_validation : bool
            If True, skip constraint validation (use when caller already validated)
        **kwargs
            Dimension parameters
        """
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import make_request
        from openbb_imf.utils.helpers import parse_time_period
        from openbb_imf.utils.table_presentation import (
            extract_unit_from_label,
            parse_unit_and_scale,
        )
        from pandas import DataFrame, to_numeric
        from requests.exceptions import RequestException

        # Validate dimension constraints before making the API call
        if not _skip_validation:
            self.validate_dimension_constraints(
                dataflow, start_date=start_date, end_date=end_date, **kwargs
            )

        url = self.build_url(dataflow, start_date, end_date, limit=limit, **kwargs)
        headers = {
            "Accept": "application/xml",
            "Cache-Control": "no-cache",
            "User-Agent": "Open Data Platform - IMF Data Fetcher",
        }
        response = None

        try:
            response = make_request(url, headers=headers)
            response.raise_for_status()
            xml_content = response.text
        except RequestException as e:
            res_content = response.text if response else ""
            raise OpenBBError(
                f"An error occurred during the HTTP request: {url} -> {e} -> {res_content}"
            ) from e

        # Parse XML
        try:
            import defusedxml.ElementTree as DefusedET

            root = DefusedET.fromstring(xml_content)
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(f"Failed to parse XML response: {url} -> {e}") from e

        # Define namespaces used in IMF SDMX responses
        namespaces = {
            "message": "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message",
            "ss": "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/data/structurespecific",
            "common": "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common",
        }

        # Find all Series elements
        dataset = root.find(".//message:DataSet", namespaces)
        if dataset is None:
            # Try without namespace prefix
            dataset = root.find(".//DataSet")
        if dataset is None:
            # Try with ss namespace
            dataset = root.find(".//ss:DataSet", namespaces)
        if dataset is None:
            raise OpenBBError(
                EmptyDataError(f"No data found in the response. URL: {url}")
            )

        # Parse Group elements to extract group-level attributes (UNIT, ACCOUNTING_ENTRY, etc.)
        # Group structure: <Group INDICATOR="..." ns1:type="GROUP_INDICATOR">
        #                    <Comp id="UNIT"><Value>USD</Value></Comp>
        #                    <Comp id="ACCOUNTING_ENTRY"><Value>NETLA</Value></Comp>
        #                  </Group>
        group_attributes: dict[str, dict[str, str]] = {}

        # Find all Group elements - they can have namespace prefix
        for group in dataset.findall("Group") + dataset.findall("ss:Group", namespaces):
            # The group key is typically the INDICATOR code or similar dimension
            group_key = None
            for attr_name, attr_value in group.attrib.items():
                # Skip namespace type attributes like ns1:type
                if "type" in attr_name.lower() and "group" in attr_value.lower():
                    continue
                # The first non-type attribute is the key (e.g., INDICATOR)
                group_key = attr_value
                break

            if not group_key:
                continue

            # Extract Comp elements containing group-level attribute values
            group_attrs: dict[str, str] = {}
            for comp in group.findall("Comp") + group.findall("ss:Comp", namespaces):
                comp_id = comp.attrib.get("id")
                if comp_id:
                    # Value is in a child <Value> element
                    value_elem = comp.find("Value") or comp.find("ss:Value", namespaces)
                    if value_elem is not None and value_elem.text:
                        group_attrs[comp_id] = value_elem.text

            if group_attrs:
                group_attributes[group_key] = group_attrs

        # Get dataflow metadata
        dataflow_obj = self.metadata.dataflows.get(dataflow, {})
        # Build translation maps for dimension values
        translation_maps = self._get_cached_translations(dataflow)
        # Build dimension order mapping for proper series_id construction
        structure_ref = dataflow_obj.get("structureRef", {})
        dsd_id = structure_ref.get("id")
        indicator_dimension_order: dict[str, int] = {}
        indicator_id_candidates = [
            "INDICATOR",
            "PRODUCTION_INDEX",
            "COICOP_1999",
            "INDEX_TYPE",
            "ACTIVITY",
            "PRODUCT",
            "SERIES",
            "ITEM",
            "BOP_ACCOUNTING_ENTRY",
            "ACCOUNTING_ENTRY",
        ]

        if dsd_id and dsd_id in self.metadata.datastructures:
            dsd = self.metadata.datastructures[dsd_id]
            dimensions = dsd.get("dimensions", [])

            for idx, dim in enumerate(dimensions):
                dim_id = dim.get("id", "")

                if not dim_id:
                    continue

                if dim_id in indicator_id_candidates or any(
                    keyword in dim_id
                    for keyword in ["INDICATOR", "ACCOUNTING_ENTRY", "ENTRY"]
                ):
                    indicator_dimension_order[dim_id] = idx

        # Process all Series elements
        all_data_rows: list = []
        all_unique_indicators: set = set()
        all_series_derivation_types: dict = {}

        # Build dimension order map for consistent title and series_id ordering
        dim_order_map: dict[str, int] = {}
        # Build attribute codelist map for proper code translation
        attr_codelist_map: dict[str, dict] = {}
        if dsd_id and dsd_id in self.metadata.datastructures:
            dsd = self.metadata.datastructures[dsd_id]
            for idx, dim in enumerate(dsd.get("dimensions", [])):
                dim_order_map[dim.get("id", "")] = idx
            # Resolve codelists for attributes (UNIT, SCALE, etc.)
            for attr in dsd.get("attributes", []):
                attr_id = attr.get("id")
                if attr_id:
                    codelist_id = self.metadata._resolve_codelist_id(
                        dataflow, dsd_id, attr_id, attr
                    )
                    if codelist_id and codelist_id in self.metadata._codelist_cache:
                        attr_codelist_map[attr_id] = self.metadata._codelist_cache[
                            codelist_id
                        ]

        # Find Series elements with multiple namespace approaches
        series_elements = dataset.findall("Series") + dataset.findall(
            "ss:Series", namespaces
        )

        # Remove duplicates while preserving order
        seen_series = set()
        unique_series = []
        for s in series_elements:
            s_id = id(s)
            if s_id not in seen_series:
                seen_series.add(s_id)
                unique_series.append(s)
        series_elements = unique_series

        for series in series_elements:
            # Extract series attributes (dimensions)
            series_meta: dict = {}
            indicator_code = None
            indicator_codes_list: list = []
            all_dimension_codes: list = []  # Track ALL dimension codes for series_id
            # Collect ALL dimension labels for building a complete title
            # Format: (position, dimension_id, display_value)
            title_parts: list[tuple[int, str, str]] = []
            # Dimensions to EXCLUDE from title (they have their own columns or are metadata)
            # Note: COUNTERPART_COUNTRY is NOT excluded - it's meaningful for DIP, BOP, etc.
            title_exclude_dims = {
                "COUNTRY",
                "REF_AREA",
                "TIME_PERIOD",
                "SCALE",
                "UNIT",
                "FREQ",
                "FREQUENCY",
                "OBS_VALUE",
                "OBS_STATUS",
            }

            for attr_name, attr_value in series.attrib.items():
                # Track ALL dimension codes for complete series_id
                all_dimension_codes.append((attr_name, attr_value))

                # Special handling for indicator-like dimensions
                if attr_name in indicator_id_candidates or "INDICATOR" in attr_name:
                    indicator_code = attr_value
                    indicator_codes_list.append((attr_name, attr_value))
                    all_unique_indicators.add(attr_value)

                    # Translate the code to human-readable label
                    if (
                        attr_name in translation_maps
                        and attr_value in translation_maps[attr_name]
                    ):
                        display_value = translation_maps[attr_name][attr_value]
                    else:
                        display_value = attr_value

                    series_meta[attr_name] = display_value
                    series_meta[f"{attr_name}_code"] = attr_value
                    # Add to title parts with high position (indicator goes last)
                    dim_pos = dim_order_map.get(attr_name, 999)
                    title_parts.append((dim_pos, attr_name, display_value))

                elif attr_name == "COUNTRY":
                    # Translate country code
                    if (
                        attr_name in translation_maps
                        and attr_value in translation_maps[attr_name]
                    ):
                        display_value = translation_maps[attr_name][attr_value]
                    else:
                        display_value = attr_value
                    series_meta[attr_name] = display_value
                    series_meta["country_code"] = attr_value

                elif attr_name == "COUNTERPART_COUNTRY":
                    if (
                        attr_name in translation_maps
                        and attr_value in translation_maps[attr_name]
                    ):
                        display_value = translation_maps[attr_name][attr_value]
                    else:
                        display_value = attr_value
                    series_meta[attr_name] = display_value
                    series_meta["counterpart_country_code"] = attr_value
                    # Add to title parts - COUNTERPART_COUNTRY is meaningful for DIP, BOP
                    dim_pos = dim_order_map.get(attr_name, 999)
                    title_parts.append((dim_pos, attr_name, display_value))

                elif attr_name == "SCALE":
                    # Handle scale/unit multiplier - use proper codelist from DSD
                    try:
                        scale_int = int(attr_value)
                        series_meta["unit_multiplier"] = (
                            1 if scale_int == 0 else 10**scale_int
                        )
                        # Use DSD-specific codelist if available, else CL_UNIT_MULT
                        if attr_name in attr_codelist_map:
                            scale_codelist = attr_codelist_map[attr_name]
                            series_meta["scale"] = scale_codelist.get(
                                attr_value, f"10^{attr_value}"
                            )
                        elif cl_unit_mult := self.metadata._codelist_cache.get(
                            "CL_UNIT_MULT", {}
                        ):
                            series_meta["scale"] = cl_unit_mult.get(
                                attr_value, f"10^{attr_value}"
                            )
                        else:
                            series_meta["scale"] = f"10^{attr_value}"
                    except ValueError:
                        series_meta["scale"] = attr_value

                elif attr_name == "UNIT":
                    # Handle unit - use proper codelist from DSD, not generic CL_UNIT
                    if attr_name in attr_codelist_map:
                        unit_codelist = attr_codelist_map[attr_name]
                        series_meta["unit"] = unit_codelist.get(attr_value, attr_value)
                    else:
                        # Fallback to generic CL_UNIT only if no DSD-specific codelist
                        cl_unit = self.metadata._codelist_cache.get("CL_UNIT", {})
                        series_meta["unit"] = cl_unit.get(attr_value, attr_value)

                elif (
                    attr_name in translation_maps
                    and attr_value in translation_maps[attr_name]
                ):
                    # Store translated label and preserve code
                    display_value = translation_maps[attr_name][attr_value]
                    series_meta[attr_name] = display_value
                    series_meta[f"{attr_name}_code"] = attr_value
                    # Add to title parts if not excluded
                    if attr_name not in title_exclude_dims:
                        dim_pos = dim_order_map.get(attr_name, 999)
                        title_parts.append((dim_pos, attr_name, display_value))
                elif attr_name not in [
                    "IFS_FLAG",
                    "OVERLAP",
                    "OBS_STATUS",
                    "DECIMALS_DISPLAYED",
                    "COUNTRY_UPDATE_DATE",
                ]:
                    # Dimension not in translation maps - store raw value
                    # Also store with _code suffix for consistency
                    series_meta[attr_name] = attr_value
                    series_meta[f"{attr_name}_code"] = attr_value
                    # Add to title parts if not excluded (use raw code as display)
                    if attr_name not in title_exclude_dims:
                        dim_pos = dim_order_map.get(attr_name, 999)
                        title_parts.append((dim_pos, attr_name, attr_value))

            # Store indicator_codes for series_id building
            if indicator_codes_list:
                series_meta["indicator_codes"] = indicator_codes_list

            # Build title from ALL collected dimension labels
            # Sort by DSD dimension position so title is consistent
            if title_parts:
                sorted_title_parts = sorted(title_parts, key=lambda x: (x[0], x[1]))
                series_meta["title"] = " - ".join(p[2] for p in sorted_title_parts)

            # Apply group-level attributes (UNIT, ACCOUNTING_ENTRY, etc.) from Group elements
            # The group_attributes dict maps indicator codes to their group-level attrs
            if indicator_code and indicator_code in group_attributes:
                group_attrs = group_attributes[indicator_code]
                for attr_id, attr_value in group_attrs.items():
                    if attr_id == "UNIT" and "unit" not in series_meta:
                        # Translate UNIT code
                        if "UNIT" in attr_codelist_map:
                            unit_codelist = attr_codelist_map["UNIT"]
                            series_meta["unit"] = unit_codelist.get(
                                attr_value, attr_value
                            )
                        elif cl_unit := self.metadata._codelist_cache.get("CL_UNIT"):
                            series_meta["unit"] = cl_unit.get(attr_value, attr_value)
                        else:
                            series_meta["unit"] = attr_value
                    elif attr_id == "SCALE" and "scale" not in series_meta:
                        try:
                            scale_int = int(attr_value)
                            series_meta["unit_multiplier"] = (
                                1 if scale_int == 0 else 10**scale_int
                            )
                            if "SCALE" in attr_codelist_map:
                                scale_codelist = attr_codelist_map["SCALE"]
                                series_meta["scale"] = scale_codelist.get(
                                    attr_value, f"10^{attr_value}"
                                )
                            elif cl_unit_mult := self.metadata._codelist_cache.get(
                                "CL_UNIT_MULT"
                            ):
                                series_meta["scale"] = cl_unit_mult.get(
                                    attr_value, f"10^{attr_value}"
                                )
                            else:
                                series_meta["scale"] = f"10^{attr_value}"
                        except ValueError:
                            series_meta["scale"] = attr_value
                    elif attr_id not in series_meta:
                        # Translate using translation maps if available
                        if (
                            attr_id in translation_maps
                            and attr_value in translation_maps[attr_id]
                        ):
                            series_meta[attr_id] = translation_maps[attr_id][attr_value]
                            series_meta[f"{attr_id}_code"] = attr_value
                        else:
                            series_meta[attr_id] = attr_value

            if "unit" not in series_meta:
                # Get CL_UNIT codelist for looking up unit codes
                cl_unit = self.metadata._codelist_cache.get("CL_UNIT", {})
                # First check TYPE_OF_TRANSFORMATION which provides unit-like info
                type_of_transform = series_meta.get("TYPE_OF_TRANSFORMATION")
                if type_of_transform:
                    # TYPE_OF_TRANSFORMATION may contain compound values like
                    # "Period average, Year-over-year (YOY) percent change"
                    # Try to extract just the unit part
                    if type_of_transform in ["Index", "Weight", "Ratio"]:
                        series_meta["unit"] = type_of_transform
                    elif "percent change" in type_of_transform.lower():
                        series_meta["unit"] = "Percent change"
                        if "year-over-year" in type_of_transform.lower():
                            series_meta["scale"] = "Year-over-year"
                        elif "period-over-period" in type_of_transform.lower():
                            series_meta["scale"] = "Period-over-period"
                    elif ", " in type_of_transform:
                        # Try last part after comma (e.g., "Weight, Percent" -> "Percent")
                        last_part = type_of_transform.split(", ")[-1].strip()
                        if last_part in ["Index", "Percent", "Weight", "Ratio"]:
                            series_meta["unit"] = last_part
                        else:
                            series_meta["unit"] = type_of_transform
                    else:
                        series_meta["unit"] = type_of_transform

                # Try extracting unit AND scale from indicator label
                # Label format: "Description, Scale, Unit" e.g.,
                # "Exporter real GDP, Per capita, US dollar"
                indicator_label = series_meta.get("INDICATOR")
                extracted_unit = None
                extracted_scale = None
                if indicator_label:
                    extracted_unit_string = extract_unit_from_label(indicator_label)
                    if extracted_unit_string:
                        extracted_unit, extracted_scale = parse_unit_and_scale(
                            extracted_unit_string
                        )

                # If still no unit, try extracting from indicator code suffix
                # e.g., XQI_IX -> IX -> "Index" (from CL_UNIT)
                # BUT: only if the suffix is actually a unit code, not a dimension code
                # like "ALL" (All entities) or country codes
                if "unit" not in series_meta:
                    ind_code = series_meta.get("INDICATOR_code")
                    if ind_code and "_" in ind_code:
                        parts = ind_code.rsplit("_", 1)
                        if len(parts) == 2:
                            unit_code = parts[1]
                            # Skip common dimension codes that appear as suffixes
                            dimension_codes = {"ALL", "FE", "RFI", "REXFI"}
                            if (
                                unit_code in cl_unit
                                and unit_code not in dimension_codes
                            ):
                                series_meta["unit"] = cl_unit[unit_code]

                if extracted_scale:
                    # Only override if current scale is generic or missing
                    current_scale = series_meta.get("scale")
                    generic_scales = {"Units", "units", None, ""}
                    if current_scale in generic_scales or not current_scale:
                        series_meta["scale"] = extracted_scale

                # If still no unit, use extracted unit from label
                if "unit" not in series_meta and extracted_unit:
                    series_meta["unit"] = extracted_unit

                # If still no unit, try other label sources
                if "unit" not in series_meta:
                    # Try these label sources in order of priority
                    label_sources = [
                        series_meta.get("title"),  # May be overwritten by PRODUCT
                        series_meta.get("PRODUCTION_INDEX"),
                        series_meta.get("INDEX_TYPE"),
                    ]
                    for label in label_sources:
                        if label:
                            extracted_unit_string = extract_unit_from_label(label)
                            if extracted_unit_string:
                                # Parse into separate unit and scale components
                                unit, scale = parse_unit_and_scale(
                                    extracted_unit_string
                                )
                                if unit:
                                    series_meta["unit"] = unit
                                if scale and "scale" not in series_meta:
                                    series_meta["scale"] = scale
                                break

            # Match the input format: dataflow::indicator_code
            if indicator_codes_list:
                # Sort by DSD dimension order for consistency
                sorted_ind_codes = sorted(
                    indicator_codes_list,
                    key=lambda x: (indicator_dimension_order.get(x[0], 999), x[0]),
                )
                combined_codes = "_".join(code for _, code in sorted_ind_codes)
                series_meta["series_id"] = f"{dataflow}::{combined_codes}"
            elif indicator_code:
                # Fallback if no indicator codes list
                series_meta["series_id"] = f"{dataflow}::{indicator_code}"

            # Process observations with multiple namespace approaches
            obs_elements = series.findall("Obs") + series.findall("ss:Obs", namespaces)
            # Remove duplicates
            seen_obs = set()
            unique_obs = []
            for o in obs_elements:
                o_id = id(o)
                if o_id not in seen_obs:
                    seen_obs.add(o_id)
                    unique_obs.append(o)

            derivation_types_in_series: set = set()

            for obs in unique_obs:
                obs_row = series_meta.copy()

                # TIME_PERIOD - try multiple attribute names
                time_period = (
                    obs.attrib.get("TIME_PERIOD")
                    or obs.attrib.get("TIME")
                    or obs.attrib.get("time")
                    or ""
                )

                # Get observation value - SDMX 3.0 XML format
                # Value can be in OBS_VALUE attribute or ObsValue child element
                obs_value = obs.attrib.get("OBS_VALUE") or obs.attrib.get("OBSERVATION")

                # If not in attributes, check child elements
                if obs_value is None:
                    # Try ObsValue element with namespace
                    obs_value_elem = obs.find("ss:ObsValue", namespaces)
                    if obs_value_elem is None:
                        obs_value_elem = obs.find("ObsValue")
                    if obs_value_elem is not None:
                        obs_value = (
                            obs_value_elem.attrib.get("value") or obs_value_elem.text
                        )
                    else:
                        # Search all children for value-like elements
                        for child in obs:
                            local_tag = (
                                child.tag.split("}")[-1]
                                if "}" in child.tag
                                else child.tag
                            )
                            if local_tag.upper() in ("OBSVALUE", "OBS_VALUE", "VALUE"):
                                obs_value = child.attrib.get("value") or child.text
                                if obs_value:
                                    break

                derivation_type = obs.attrib.get("DERIVATION_TYPE")
                obs_row["TIME_PERIOD"] = time_period

                # Extract observation-level attributes (UNIT, SCALE, etc.)
                # These may override series-level attributes for specific observations
                obs_unit = obs.attrib.get("UNIT")
                if obs_unit:
                    # Use proper codelist from DSD, not generic CL_UNIT
                    if "UNIT" in attr_codelist_map:
                        unit_codelist = attr_codelist_map["UNIT"]
                        obs_row["unit"] = unit_codelist.get(obs_unit, obs_unit)
                    else:
                        cl_unit = self.metadata._codelist_cache.get("CL_UNIT", {})
                        obs_row["unit"] = cl_unit.get(obs_unit, obs_unit)

                obs_scale = obs.attrib.get("SCALE")
                if obs_scale:
                    try:
                        scale_int = int(obs_scale)
                        obs_row["unit_multiplier"] = (
                            1 if scale_int == 0 else 10**scale_int
                        )
                        # Use DSD-specific codelist if available
                        if "SCALE" in attr_codelist_map:
                            scale_codelist = attr_codelist_map["SCALE"]
                            obs_row["scale"] = scale_codelist.get(
                                obs_scale, f"10^{obs_scale}"
                            )
                        elif cl_unit_mult := self.metadata._codelist_cache.get(
                            "CL_UNIT_MULT", {}
                        ):
                            obs_row["scale"] = cl_unit_mult.get(
                                obs_scale, f"10^{obs_scale}"
                            )
                        else:
                            obs_row["scale"] = f"10^{obs_scale}"
                    except ValueError:
                        obs_row["scale"] = obs_scale

                # Only add rows with actual values
                if obs_value is not None and obs_value not in {"", "D"}:
                    obs_row["value"] = obs_value

                    if derivation_type:
                        if "CL_DERIVATION_TYPE" in self.metadata._codelist_cache:
                            derivation_type = self.metadata._codelist_cache[
                                "CL_DERIVATION_TYPE"
                            ].get(derivation_type, derivation_type)
                        derivation_types_in_series.add(derivation_type)

                    all_data_rows.append(obs_row)

            if indicator_code and derivation_types_in_series:
                if len(derivation_types_in_series) == 1:
                    all_series_derivation_types[indicator_code] = list(
                        derivation_types_in_series
                    )[0]
                else:
                    all_series_derivation_types[indicator_code] = "; ".join(
                        sorted(derivation_types_in_series)
                    )

        if not all_data_rows:
            # Build a more helpful error message with parameter info
            param_info = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v)
            raise OpenBBError(
                EmptyDataError(
                    f"No data rows found for dataflow '{dataflow}' with parameters: "
                    + f"{param_info}. "
                    + "The IMF constraints API reports this combination as valid, "
                    + "but no actual observations were returned in the data. "
                    + f"URL -> {url}"
                )
            )

        # Create DataFrame and clean up
        df = DataFrame(all_data_rows)
        df = df.rename(columns={"value": "OBS_VALUE"})
        df["OBS_VALUE"] = to_numeric(df["OBS_VALUE"], errors="coerce")

        # Parse TIME_PERIOD into valid date format
        if "TIME_PERIOD" in df.columns:
            df["TIME_PERIOD"] = df["TIME_PERIOD"].apply(parse_time_period)

        # Build metadata
        metadata: dict = {}

        # Get indicator descriptions from cache
        all_indicators_meta = self.metadata.get_indicators_in(dataflow)
        indicator_descriptions_map = {
            item["indicator"]: item["description"] for item in all_indicators_meta
        }

        # Add description column to DataFrame based on indicator code
        # Look for any indicator column to map descriptions
        indicator_col = None
        for col in df.columns:
            if col.endswith("_code") and col.replace("_code", "") in [
                "INDICATOR",
                "BOP_ACCOUNTING_ENTRY",
                "ACCOUNTING_ENTRY",
                "SERIES",
                "ITEM",
            ]:
                indicator_col = col
                break

        if indicator_col:
            df["description"] = df[indicator_col].map(indicator_descriptions_map)
        else:
            df["description"] = ""

        # Add indicator metadata
        for indicator_code in all_unique_indicators:
            # Use dataflow::indicator format for user-facing metadata keys
            full_key = f"{dataflow}::{indicator_code}"
            ind_meta = {
                "description": indicator_descriptions_map.get(indicator_code, ""),
                "indicator": indicator_code,
            }

            # Add derivation type to series metadata if available
            if indicator_code in all_series_derivation_types:
                ind_meta["derivation_type"] = all_series_derivation_types[
                    indicator_code
                ]

            metadata[full_key] = ind_meta

        # Add dataset-level metadata from cached dataflow info
        dataset_attrs = self._extract_dataset_attributes_from_cache(dataflow)

        if dataset_attrs:
            metadata["dataset"] = dataset_attrs

        return {"data": df.to_dict(orient="records"), "metadata": metadata}

    def _extract_dataset_attributes_from_cache(self, dataflow: str) -> dict:
        """Extract dataset-level attributes from cached metadata."""
        dataset_attrs: dict = {}
        dataflow_obj = self.metadata.dataflows.get(dataflow, {})
        dataset_attrs["dataflow_id"] = dataflow
        dataset_attrs["dataflow_name"] = dataflow_obj.get("name", dataflow)
        dataset_attrs["dataflow_description"] = dataflow_obj.get("description", "")

        # Get additional attributes from the cached dataflow object
        for attr_key in [
            "publisher",
            "department",
            "contact_point",
            "keywords",
            "license",
            "suggested_citation",
            "short_source_citation",
            "full_source_citation",
            "publication_date",
            "update_date",
            "methodology_notes",
            "topic_dataset",
            "keywords_dataset",
        ]:
            if attr_val := dataflow_obj.get(attr_key):
                dataset_attrs[attr_key] = attr_val

        return dataset_attrs

    def _build_translation_maps(self, structure: dict, dataflow: str) -> dict:
        """Build dimension translation maps from the response structure values.
        Fallback to metadata.get_dataflow_parameters if a dimension has no inline values.
        Returns a mapping: { dimension_id: { code: label, ... }, ... }
        """
        maps: dict = {}

        # First, get ALL translations from cached dataflow parameters
        try:
            df_params = self.metadata.get_dataflow_parameters(dataflow)
            for dim_id, options in df_params.items():
                if isinstance(options, list) and options:
                    maps[dim_id] = {
                        opt["value"]: opt["label"] for opt in options if "value" in opt
                    }
        except Exception:  # noqa  # pylint: disable=broad-except
            pass

        # Then overlay with any labels from the structure (if they're better than codes)
        for dim_group in ("series", "observation"):
            for dim in structure.get("dimensions", {}).get(dim_group, []):
                dim_id = dim.get("id")

                if not dim_id:
                    continue

                vals = dim.get("values", [])

                if not vals:
                    continue

                # Only update if the structure has actual names (not just codes)
                for v in vals:
                    code = v.get("id")
                    name = v.get("name")
                    # Only use if name is different from code
                    if code and name and name != code:
                        if dim_id not in maps:
                            maps[dim_id] = {}
                        maps[dim_id][code] = name

        return maps

    def _parse_attributes(self, attr_values: list, attr_definitions: list) -> dict:
        """Parse attribute values using their definitions."""
        result: dict = {}

        for i, value in enumerate(attr_values):
            if value is None:
                continue

            if i < len(attr_definitions):
                attr_def = attr_definitions[i]
                attr_id = attr_def.get("id")

                # If value is an index, look it up in the definition's values
                if isinstance(value, int) and "values" in attr_def:
                    values_list = attr_def.get("values", [])
                    if value < len(values_list):
                        actual_value = values_list[value].get("id")
                        result[attr_id] = actual_value
                else:
                    result[attr_id] = value

        return result

    def _get_cached_translations(self, dataflow: str) -> dict:
        """Get translation maps from cached metadata."""
        maps: dict = {}
        # Get dataflow parameters for dimension translations
        # Load ALL dimensions, not just a subset
        dataflow_params = self.metadata.get_dataflow_parameters(dataflow)
        for dim_id, items in dataflow_params.items():
            maps[dim_id] = {item["value"]: item["label"] for item in items}

        return maps

    def _extract_dataset_attributes(
        self, structure: dict, json_data: dict, dataflow: str
    ) -> dict:
        """Extract dataset-level attributes."""
        dataset_attrs: dict = {}
        # Add dataflow info
        dataflow_obj = self.metadata.dataflows.get(dataflow, {})
        dataset_attrs["dataflow_id"] = dataflow
        dataset_attrs["dataflow_name"] = dataflow_obj.get("name", dataflow)
        dataset_attrs["dataflow_description"] = dataflow_obj.get("description", "")
        # Get dataset attributes from the cached dataflow object
        # These are stored in the dataflow metadata, not in the API response
        for attr_key in [
            "publisher",
            "department",
            "contact_point",
            "keywords",
            "license",
            "suggested_citation",
            "short_source_citation",
            "full_source_citation",
            "publication_date",
            "update_date",
            "methodology_notes",
            "topic_dataset",
            "keywords_dataset",
        ]:
            if attr_key in dataflow_obj:
                dataset_attrs[attr_key] = dataflow_obj.get(attr_key)

        # Extract attributes from structure response (for UPDATE_DATE, PUBLICATION_DATE, etc.)``
        if "attributes" in structure and "dataSet" in structure["attributes"]:
            dataset_attributes = []
            if "dataSets" in json_data and json_data["dataSets"]:
                dataset_attributes = json_data["dataSets"][0].get("attributes", [])

            # If no attributes in the response, return what we have from cache
            if not dataset_attributes:
                return dataset_attrs

            attr_defs = structure["attributes"]["dataSet"]

            # Iterate through both definitions and values together by index
            for i, attr_def in enumerate(attr_defs):
                attr_id = attr_def.get("id")

                if attr_id not in [
                    "CONTACT_POINT",
                    "PUBLISHER",
                    "DEPARTMENT",
                    "LICENSE",
                    "SUGGESTED_CITATION",
                    "SHORT_SOURCE_CITATION",
                    "FULL_SOURCE_CITATION",
                    "PUBLICATION_DATE",
                    "UPDATE_DATE",
                    "METHODOLOGY_NOTES",
                    "TOPIC_DATASET",
                    "KEYWORDS_DATASET",
                ]:
                    continue

                attr_value = (
                    dataset_attributes[i] if i < len(dataset_attributes) else None
                )

                if attr_value is not None and attr_value != [None]:
                    if attr_id == "TOPIC_DATASET":
                        topic_codes = []
                        if isinstance(attr_value, int) and "values" in attr_def:
                            values_list = attr_def.get("values", [])
                            if attr_value < len(values_list):
                                topic_val = values_list[attr_value]
                                if isinstance(topic_val, dict):
                                    if "ids" in topic_val:
                                        topic_codes.extend(topic_val.get("ids", []))
                                    elif "id" in topic_val:
                                        topic_codes.append(topic_val.get("id"))
                                else:
                                    topic_codes.append(topic_val)
                        elif isinstance(attr_value, list):
                            for val in attr_value:
                                if isinstance(val, int) and "values" in attr_def:
                                    values_list = attr_def.get("values", [])
                                    if val < len(values_list):
                                        topic_val = values_list[val]
                                        if isinstance(topic_val, dict):
                                            if "ids" in topic_val:
                                                topic_codes.extend(
                                                    topic_val.get("ids", [])
                                                )
                                            elif "id" in topic_val:
                                                topic_codes.append(topic_val.get("id"))
                                        else:
                                            topic_codes.append(topic_val)
                                elif isinstance(val, str):
                                    topic_codes.append(val)

                        # Translate topic codes to names using cached codelist
                        if topic_codes and "CL_TOPIC" in self.metadata._codelist_cache:
                            topic_names = []
                            for code in topic_codes:
                                topic_name = self.metadata._codelist_cache[
                                    "CL_TOPIC"
                                ].get(code, code)
                                topic_names.append(topic_name)
                            dataset_attrs["topics"] = topic_names
                        elif topic_codes:
                            dataset_attrs["topics"] = topic_codes

                    elif attr_id == "KEYWORDS_DATASET":
                        keywords = self._extract_attribute_value(attr_value, attr_def)
                        if keywords:
                            dataset_attrs["keywords"] = keywords
                    elif attr_id == "UPDATE_DATE":
                        date_value = self._extract_attribute_value(attr_value, attr_def)
                        if date_value:
                            try:
                                if isinstance(date_value, str) and "." in date_value:
                                    parts = date_value.split(".")
                                    if len(parts) == 2:
                                        fractional = parts[1][:6].ljust(6, "0")
                                        date_value = f"{parts[0]}.{fractional}Z"
                                dataset_attrs["last_updated"] = date_value
                            except (  # noqa  # pylint: disable=broad-exception-caught
                                Exception
                            ):
                                dataset_attrs["last_updated"] = date_value
                    elif attr_id == "PUBLICATION_DATE":
                        pub_date = self._extract_attribute_value(attr_value, attr_def)
                        if pub_date:
                            dataset_attrs["publication_date"] = pub_date
                    else:
                        final_value = self._extract_attribute_value(
                            attr_value, attr_def
                        )
                        if final_value:
                            dataset_attrs[attr_id.lower()] = final_value

        return dataset_attrs

    def _extract_attribute_value(self, attr_value, attr_def):
        """Extract the actual value from an attribute."""
        if isinstance(attr_value, int):
            # Value is an index into the values array
            if "values" in attr_def and attr_value < len(attr_def["values"]):
                value_obj = attr_def["values"][attr_value]
                if isinstance(value_obj, dict):
                    return (
                        value_obj.get("en")
                        or value_obj.get("name")
                        or value_obj.get("id")
                    )
                return value_obj
        elif isinstance(attr_value, list) and attr_value:
            first_val = attr_value[0]
            if (
                isinstance(first_val, int)
                and "values" in attr_def
                and first_val < len(attr_def["values"])
            ):
                value_obj = attr_def["values"][first_val]
                if isinstance(value_obj, dict):
                    return (
                        value_obj.get("en")
                        or value_obj.get("name")
                        or value_obj.get("id")
                    )
                return value_obj
            if isinstance(first_val, dict):
                return first_val.get("en") or first_val.get("name") or first_val
            return first_val
        elif isinstance(attr_value, dict):
            return attr_value.get("en") or attr_value.get("name") or attr_value

        return attr_value

    def _extract_indicator_metadata(
        self, dimension_group_attrs: dict, structure: dict
    ) -> dict:
        """Extract indicator metadata from dimensionGroupAttributes."""
        indicator_metadata: dict = {}

        # Get the dimensionGroup attribute definitions from structure
        dim_group_defs = structure.get("attributes", {}).get("dimensionGroup", [])

        # Create index maps for each attribute type
        attr_index_map: dict = {}
        for i, attr_def in enumerate(dim_group_defs):
            attr_index_map[attr_def.get("id")] = i

        indicator_dim = None
        indicator_dim_position = None
        series_dims = structure.get("dimensions", {}).get("series", [])

        # List of possible indicator dimension names
        indicator_candidates = [
            "INDICATOR",
            "COICOP_1999",
            "PRODUCTION_INDEX",
            "ACTIVITY",
            "PRODUCT",
            "SERIES",
            "ITEM",
        ]

        for i, dim in enumerate(series_dims):
            dim_id = dim.get("id")
            if dim_id in indicator_candidates or "INDICATOR" in dim_id:
                indicator_dim = dim
                indicator_dim_position = i
                break

        if not indicator_dim or indicator_dim_position is None:
            return indicator_metadata

        for group_key, attr_values in dimension_group_attrs.items():
            # Parse the group key to get the indicator index
            # The key format is like ":0:::" where positions correspond to series dimensions
            key_cleaned = group_key.strip(":")
            key_parts = key_cleaned.split(":") if key_cleaned else []

            # Ensure we have enough parts
            if len(key_parts) > indicator_dim_position:
                indicator_idx_str = key_parts[indicator_dim_position]
            else:
                continue

            if not indicator_idx_str:
                continue

            try:
                indicator_idx = int(indicator_idx_str)
            except ValueError:
                continue

            if indicator_idx >= len(indicator_dim.get("values", [])):
                continue

            indicator_code = indicator_dim["values"][indicator_idx].get("id")
            # Extract attribute values
            metadata_entry: dict = {}

            # Parse each attribute value
            for attr_id, attr_idx in attr_index_map.items():
                if attr_idx < len(attr_values):
                    value = attr_values[attr_idx]

                    if attr_id == "SERIES_NAME" and value:
                        # Extract series name directly from the list
                        if isinstance(value, list) and value:
                            metadata_entry["series_name"] = (
                                value[0] if isinstance(value[0], str) else ""
                            )
                    elif attr_id == "TRADE_FLOW" and value is not None:
                        # Get trade flow code and translate using cached codelist
                        if isinstance(value, int):
                            trade_flow_values = dim_group_defs[attr_idx].get(
                                "values", []
                            )
                            if value < len(trade_flow_values):
                                trade_flow_code = trade_flow_values[value].get("id")
                                # Translate using CL_TRADE_FLOW from cache
                                if (
                                    trade_flow_code
                                    and "CL_TRADE_FLOW" in self.metadata._codelist_cache
                                ):
                                    metadata_entry["trade_flow"] = (
                                        self.metadata._codelist_cache[
                                            "CL_TRADE_FLOW"
                                        ].get(trade_flow_code, trade_flow_code)
                                    )
                                elif trade_flow_code:
                                    metadata_entry["trade_flow"] = trade_flow_code
                    elif attr_id == "VALUATION" and value is not None:
                        # Get valuation code and translate if codelist exists
                        if isinstance(value, int):
                            valuation_values = dim_group_defs[attr_idx].get(
                                "values", []
                            )
                            if value < len(valuation_values):
                                valuation_code = valuation_values[value].get("id")
                                # Try to translate using cached codelist
                                if (
                                    valuation_code
                                    and "CL_VALUATION" in self.metadata._codelist_cache
                                ):
                                    metadata_entry["valuation"] = (
                                        self.metadata._codelist_cache[
                                            "CL_VALUATION"
                                        ].get(valuation_code, valuation_code)
                                    )
                                elif valuation_code:
                                    metadata_entry["valuation"] = valuation_code
                    elif attr_id == "UNIT" and value is not None:
                        if isinstance(value, int):
                            unit_values = dim_group_defs[attr_idx].get("values", [])
                            if value < len(unit_values):
                                unit_code = unit_values[value].get("id")
                                # Skip translation for special aggregate codes that
                                # conflict with currency codes
                                special_aggregate_codes = {"ALL", "W0", "W1", "W2"}
                                if unit_code in special_aggregate_codes:
                                    metadata_entry["unit"] = unit_code
                                elif (
                                    unit_code
                                    and "CL_UNIT" in self.metadata._codelist_cache
                                ):
                                    translated_unit = self.metadata._codelist_cache[
                                        "CL_UNIT"
                                    ].get(unit_code, unit_code)
                                    metadata_entry["unit"] = translated_unit
                                else:
                                    metadata_entry["unit"] = unit_code
                    elif attr_id == "TOPIC" and value is not None:
                        # Extract topics - handle both integer indices and direct values
                        topic_codes: list = []

                        # Value is an integer index into the topic values array
                        if isinstance(value, int):
                            topic_values = dim_group_defs[attr_idx].get("values", [])
                            if value < len(topic_values):
                                topic_val = topic_values[value]
                                if isinstance(topic_val, dict):
                                    # Could be {'id': 'F10_I'} or {'ids': ['L81', 'F10_I', 'F10_E']}
                                    if "id" in topic_val:
                                        topic_codes.append(topic_val["id"])
                                    elif "ids" in topic_val:
                                        topic_codes.extend(topic_val["ids"])

                        # Translate topic codes to names using cached codelist
                        topics: list = []
                        if topic_codes and "CL_TOPIC" in self.metadata._codelist_cache:
                            for code in topic_codes:
                                topic_name = self.metadata._codelist_cache[
                                    "CL_TOPIC"
                                ].get(code, code)
                                topics.append(topic_name)
                        elif topic_codes:
                            topics = topic_codes

                        metadata_entry["topic"] = topics
                    elif (
                        attr_id == "KEY_INDICATOR"
                        and value
                        and isinstance(value, list)
                        and value
                    ):
                        metadata_entry["key_indicator"] = (
                            value[0] == "true" if isinstance(value[0], str) else False
                        )

            indicator_metadata[indicator_code] = metadata_entry

        return indicator_metadata

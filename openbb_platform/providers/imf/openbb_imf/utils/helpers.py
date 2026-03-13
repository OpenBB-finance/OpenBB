"""IMF Helper Utilities."""

# pylint: disable=R0912,W0212,R0914,R0915,R0916,R1702,W0718
# flake8: noqa: PLR0912

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError


def normalize_country_label(label: str) -> str:
    """Normalize country label to lower_snake_case.

    Examples
    --------
    >>> _normalize_country_label("United States")
    'united_states'
    >>> _normalize_country_label("Armenia, Republic of")
    'armenia'
    >>> _normalize_country_label("Euro Area (EA)")
    'euro_area'
    >>> _normalize_country_label("Guinea-Bissau")
    'guinea_bissau'
    """
    # pylint: disable=import-outside-toplevel
    import re

    # Remove all parenthetical content (handles nested parens by repeating)
    prev_label = None
    while prev_label != label:
        prev_label = label
        label = re.sub(r"\s*\([^()]*\)", "", label)
    # Remove everything after comma (handles ", Republic of", ", The", etc.)
    label = label.split(",")[0].strip()
    # Replace hyphens and spaces with underscores, convert to lowercase
    return label.replace("-", "_").replace(" ", "_").lower()


def resolve_country_code(country: str, metadata) -> str:
    """
    Resolve a country name or code to an ISO3 country code.

    Uses the CL_COUNTRY codelist to resolve names like "Japan" to "JPN".
    Returns the input unchanged if it's already an ISO3 code or can't be resolved.
    """
    country_upper = country.upper().strip()
    country_lower = country.lower().strip()

    # Check if it's already a valid code
    if "CL_COUNTRY" in metadata._codelist_cache:
        codes = metadata._codelist_cache["CL_COUNTRY"]
        if country_upper in codes:
            return country_upper

        # Try to resolve by name
        for code, name in codes.items():
            if name.lower() == country_lower:
                return code

    return country_upper  # Return as-is (uppercase)


def _parse_compound_code(
    code: str, code_to_dimension: dict[str, str]
) -> tuple[list[tuple[str, str]], list[str]]:
    """
    Parse a compound code like 'S13_G1_G23_T' into dimension matches.

    Uses greedy matching to find longest combinations first.
    ALL parts must match a dimension, otherwise returns unmatched parts.

    Returns tuple of:
        - list of (dimension_id, matched_code) tuples
        - list of unmatched parts (empty if all matched)
    """
    parts = code.split("_")
    matched_parts: list[tuple[str, str]] = []
    unmatched_parts: list[str] = []

    # Try to match longest combinations first (greedy matching)
    i = 0
    while i < len(parts):
        matched = False
        # Try longest possible combination first
        for j in range(len(parts), i, -1):
            combined = "_".join(parts[i:j])
            if combined in code_to_dimension:
                dim_id = code_to_dimension[combined]
                # Don't match same dimension twice
                if not any(m[0] == dim_id for m in matched_parts):
                    matched_parts.append((dim_id, combined))
                    i = j
                    matched = True
                    break
        if not matched:
            # Track unmatched part
            unmatched_parts.append(parts[i])
            i += 1

    return matched_parts, unmatched_parts


def _build_dimension_lookups(
    dataflow: str, metadata
) -> tuple[dict[str, str], dict[str, set[str]], list[str]]:
    """
    Build lookups for mapping codes to dimensions.

    Returns (code_to_dimension, codes_by_dimension, dimension_order) tuple.
    - code_to_dimension: maps any valid code to its dimension ID (for parsing)
    - codes_by_dimension: maps dimension ID to valid individual codes (for validation messages)
    - dimension_order: list of dimension IDs in their proper order from DSD
    """
    # pylint: disable=import-outside-toplevel
    from collections import defaultdict

    code_to_dimension: dict[str, str] = {}
    codes_by_dimension: dict[str, set[str]] = defaultdict(set)
    dimension_order: list[str] = []

    # Get ALL dimension codes from parameters API (authoritative source)
    # This provides the actual valid values for each dimension
    try:
        all_params = metadata.get_dataflow_parameters(dataflow)
        # Exclude time-related dimensions and country/area dimensions from indicator lookup
        # Country is handled separately via the 'country' parameter
        exclude_dims = {"FREQUENCY", "TIME_PERIOD", "COUNTRY", "REF_AREA"}
        for dim_id, values in all_params.items():
            if dim_id in exclude_dims:
                continue
            for v in values:
                code = v.get("value")
                if code:
                    # Add to codes_by_dimension (authoritative source for validation)
                    codes_by_dimension[dim_id].add(code)
                    # Add to code_to_dimension for matching
                    if code not in code_to_dimension:
                        code_to_dimension[code] = dim_id
    except Exception:  # noqa
        pass  # Continue with indicator-only lookup if params unavailable

    # Get dimension order from DSD
    # Keep COUNTRY/REF_AREA in order (they define the first segment position)
    # Exclude trailing dimensions that are always separate parameters
    try:
        df_obj = metadata.dataflows.get(dataflow, {})
        dsd_id = df_obj.get("structureRef", {}).get("id")
        if dsd_id and dsd_id in metadata.datastructures:
            dsd = metadata.datastructures[dsd_id]
            # Only exclude trailing parameter dimensions
            trailing_dims = {
                "FREQUENCY",
                "TIME_PERIOD",
                "TYPE_OF_TRANSFORMATION",
                "TRANSFORMATION",
            }
            for dim in dsd.get("dimensions", []):
                dim_id = dim.get("id", "")
                if (
                    dim_id
                    and dim_id.upper() not in trailing_dims
                    and "TRANSFORM" not in dim_id.upper()
                ):
                    dimension_order.append(dim_id)
    except Exception:  # noqa
        pass

    return code_to_dimension, dict(codes_by_dimension), dimension_order


def detect_indicator_dimensions(
    dataflow: str, indicator_codes: list[str], metadata
) -> dict[str, list[str]]:
    """
    Detect which dimension each indicator code belongs to.

    Different dataflows use different dimension names for indicators:
    - INDICATOR (most common)
    - BOP_ACCOUNTING_ENTRY (Balance of Payments)
    - SERIES (some datasets)
    - ITEM (some datasets)
    etc.

    Supports compound codes like 'HICP_CP01' which are split into multiple
    dimensions (e.g., INDEX_TYPE=HICP, COICOP_1999=CP01).

    Also supports compound codes with non-indicator dimensions like 'S13_G1_G23_T'
    which combines SECTOR + GFS_GRP + INDICATOR.

    Returns a dict mapping dimension_id -> list of indicator codes.

    Raises
    ------
    OpenBBError
        If any indicator code is not valid for the dataflow.
    """
    # pylint: disable=import-outside-toplevel
    from collections import defaultdict

    dimension_codes: dict[str, list[str]] = defaultdict(list)

    try:
        code_to_dimension, codes_by_dimension, dimension_order = (
            _build_dimension_lookups(dataflow, metadata)
        )

        invalid_codes: list[tuple[str, list[str]]] = []  # (code, unmatched_parts)
        for code in indicator_codes:
            if code == "*":
                # Handle wildcard - prefer INDICATOR dimension if available
                if "INDICATOR" in codes_by_dimension:
                    dimension_codes["INDICATOR"].append(code)
                elif code_to_dimension:
                    primary_dim = next(iter(code_to_dimension.values()))
                    dimension_codes[primary_dim].append(code)
                else:
                    dimension_codes["INDICATOR"].append(code)
            elif code in code_to_dimension:
                dimension_codes[code_to_dimension[code]].append(code)
            else:
                # Try to parse compound codes
                matched_parts, unmatched = _parse_compound_code(code, code_to_dimension)
                if matched_parts and not unmatched:
                    # All parts matched - valid compound code
                    for dim_id, code_part in matched_parts:
                        if code_part not in dimension_codes[dim_id]:
                            dimension_codes[dim_id].append(code_part)
                else:
                    # Either no matches or some parts didn't match
                    invalid_codes.append((code, unmatched))

        if invalid_codes:
            # Build detailed error message using dimension order
            error_parts: list[str] = []

            # Country-like dimensions to exclude unless explicitly matched
            country_dims = {"COUNTRY", "REF_AREA"}

            for code, unmatched in invalid_codes:
                if unmatched:
                    # First pass: identify all segments and their matches
                    parts = code.split("_")
                    segments: list[tuple[str, str | None]] = (
                        []
                    )  # (segment, dim_id or None)

                    i = 0
                    while i < len(parts):
                        # Try greedy matching (longest first)
                        matched = False
                        for j in range(len(parts), i, -1):
                            combined = "_".join(parts[i:j])
                            if combined in code_to_dimension:
                                segments.append((combined, code_to_dimension[combined]))
                                i = j
                                matched = True
                                break
                        if not matched:
                            segments.append((parts[i], None))
                            i += 1

                    # Check if any segment matched a country dimension
                    has_country_match = any(
                        dim_id in country_dims for _, dim_id in segments if dim_id
                    )

                    # Build effective dimension order - exclude country if not matched
                    effective_dim_order = (
                        dimension_order
                        if has_country_match
                        else [d for d in dimension_order if d not in country_dims]
                    )

                    # Find the first matched dimension to anchor our position
                    first_matched_idx: Any = None
                    first_matched_dim_pos: Any = None
                    for idx, (seg, dim_id) in enumerate(segments):  # type: ignore
                        if dim_id and dim_id in effective_dim_order:
                            first_matched_idx = idx
                            first_matched_dim_pos = effective_dim_order.index(dim_id)
                            break

                    # Build error messages
                    segment_errors: list = []
                    for idx, (seg, dim_id) in enumerate(segments):  # type: ignore
                        if dim_id is None:
                            # Calculate expected dimension based on position relative to first match
                            if (
                                first_matched_idx is not None
                                and first_matched_dim_pos is not None
                            ):
                                expected_pos = first_matched_dim_pos - (
                                    first_matched_idx - idx
                                )
                            else:
                                expected_pos = idx

                            if 0 <= expected_pos < len(effective_dim_order):
                                expected_dim = effective_dim_order[expected_pos]
                                sample = sorted(
                                    codes_by_dimension.get(expected_dim, set())
                                )[:5]
                                segment_errors.append(
                                    f"'{seg}' is invalid for {expected_dim} (valid: {', '.join(sample)})"
                                )
                            else:
                                segment_errors.append(f"'{seg}' is unrecognized")

                    error_parts.append(f"'{code}': {'; '.join(segment_errors)}")
                else:
                    error_parts.append(f"'{code}'")

            raise OpenBBError(
                f"Invalid indicator code(s) for dataflow '{dataflow}': "
                f"{'; '.join(error_parts)}. "
                f"Use `obb.economy.available_indicators(provider='imf', dataflows='{dataflow}')` to see all valid codes."
            )

    except OpenBBError:
        raise
    except Exception:
        # Fallback: put all codes in INDICATOR dimension (can't validate)
        dimension_codes["INDICATOR"] = indicator_codes

    return dict(dimension_codes)


def detect_transform_dimension(
    dataflow: str,
) -> tuple[str | None, str | None, dict[str, str], dict[str, str]]:
    """
    Detect transformation and unit dimensions for a dataflow.

    Dynamically finds dimensions containing 'TRANSFORM' or 'UNIT' in their names.

    Returns:
        tuple of (transform_dim, unit_dim, transform_lookup, unit_lookup) where:
        - transform_dim: name of transform dimension (or None)
        - unit_dim: name of unit dimension (or None)
        - transform_lookup: maps user-friendly names (index, yoy, period) to IMF codes
        - unit_lookup: maps user-friendly names (usd, eur, index, local) to IMF codes
    """
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.metadata import ImfMetadata

    transform_dim: str | None = None
    unit_dim: str | None = None
    transform_lookup: dict[str, str] = {}
    unit_lookup: dict[str, str] = {}

    try:
        m = ImfMetadata()
        params = m.get_dataflow_parameters(dataflow)

        for dim, values in params.items():
            dim_upper = dim.upper()

            # Handle TRANSFORM dimension
            if "TRANSFORM" in dim_upper:
                transform_dim = dim
                for v in values:
                    code = v.get("value", "")
                    label = v.get("label", "").lower()

                    # Prefer simpler codes (shorter, no prefix like SRP_, WGT, SA_)
                    is_simple = (
                        not code.startswith("SRP_")
                        and not code.startswith("WGT")
                        and not code.startswith("SA_")
                    )

                    # Index: just "Index" without change/percent
                    if (
                        label == "index"
                        or (
                            "index" in label
                            and "change" not in label
                            and "percent" not in label
                        )
                    ) and ("index" not in transform_lookup or is_simple):
                        transform_lookup["index"] = code

                    # YOY: year-over-year or year ago
                    if (
                        "year-over-year" in label
                        or "yoy" in label
                        or "year ago" in label
                    ) and ("yoy" not in transform_lookup or is_simple):
                        transform_lookup["yoy"] = code

                    # Period: period-over-period (not year-over-year)
                    if (
                        "period-over-period" in label
                        or (
                            "period" in label
                            and "change" in label
                            and "year" not in label
                        )
                    ) and ("period" not in transform_lookup or is_simple):
                        transform_lookup["period"] = code

                    if ("percent of gdp" in label or "% of gdp" in label) and (
                        "percent_gdp" not in transform_lookup or is_simple
                    ):
                        transform_lookup["percent_gdp"] = code

                    # Currency / Domestic currency (for GFS dataflows)
                    if ("domestic currency" in label or label == "currency") and (
                        "currency" not in transform_lookup or is_simple
                    ):
                        transform_lookup["currency"] = code

                    # Also allow direct code access (case-insensitive)
                    transform_lookup[code.lower()] = code

            # Handle UNIT dimension
            elif dim_upper == "UNIT":
                unit_dim = dim
                for v in values:
                    code = v.get("value", "")
                    label = v.get("label", "").lower()

                    # Map common unit names
                    if "us dollar" in label or label == "usd":
                        unit_lookup["usd"] = code
                    if "euro" in label or label == "eur":
                        unit_lookup["eur"] = code
                    if label == "index" or "index" in label:
                        unit_lookup["index"] = code
                    if "local" in label or "national" in label or "domestic" in label:
                        unit_lookup["local"] = code
                    if "percent" in label or "%" in label:
                        unit_lookup["percent"] = code

                    # Also allow direct code access (case-insensitive)
                    unit_lookup[code.lower()] = code

    except (KeyError, ValueError):
        pass

    return transform_dim, unit_dim, transform_lookup, unit_lookup


def parse_time_period(time_str: str) -> str:
    """Convert IMF time period formats to valid date strings (period ending).

    Examples:
        '2025-M03' -> '2025-03-31'
        '2025-Q1' -> '2025-03-31'
        '2025' -> '2025-12-31'
    """
    # pylint: disable=import-outside-toplevel
    import calendar
    from datetime import datetime

    if not time_str:
        return time_str

    try:
        # Handle monthly format (YYYY-MXX)
        if "-M" in time_str:
            parts = time_str.split("-M")
            if len(parts) == 2:
                year = int(parts[0])
                month = int(parts[1])

                # Get the last day of the month using calendar module
                last_day = calendar.monthrange(year, month)[1]

                # Create date object and format it
                date_obj = datetime(year, month, last_day)
                return date_obj.strftime("%Y-%m-%d")

        # Handle quarterly format (YYYY-QX)
        elif "-Q" in time_str:
            parts = time_str.split("-Q")
            if len(parts) == 2:
                year = int(parts[0])
                quarter = int(parts[1])

                # Map quarters to their last month
                quarter_last_month = {1: 3, 2: 6, 3: 9, 4: 12}
                month = quarter_last_month.get(quarter, 12)

                # Get the last day of the quarter's last month
                last_day = calendar.monthrange(year, month)[1]

                # Create date object and format it
                date_obj = datetime(year, month, last_day)
                return date_obj.strftime("%Y-%m-%d")

        # Handle yearly format (YYYY)
        elif len(time_str) == 4 and time_str.isdigit():
            year = int(time_str)
            # Last day of the year is always December 31
            date_obj = datetime(year, 12, 31)
            return date_obj.strftime("%Y-%m-%d")

        # Return as-is if it's already in a valid format or unrecognized
        return time_str

    except (ValueError, KeyError):
        # If parsing fails, return the original string
        return time_str


def parse_agency_from_urn(code_urn: str) -> str | None:
    """
    Parse agency ID from hierarchicalCode's code URN.

    Examples
    --------
    >>> parse_agency_from_urn("urn:sdmx:org.sdmx.infomodel.codelist.Code=ISORA:CL_RAFIT_LABELS(1.0+.0).CL_TOPIC_1")
    'ISORA'
    >>> parse_agency_from_urn("urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP_INDICATOR(10.0+.0).CAB")
    'IMF.STA'
    """
    if not code_urn or "=" not in code_urn or ":" not in code_urn:
        return None
    try:
        # Extract everything after the "=" and before the last ":"
        # Example: "ISORA:CL_RAFIT_LABELS(1.0+.0).CL_TOPIC_1"
        after_equals = code_urn.split("=")[-1]
        # Split by ":" to get agency (first part) and codelist info (second part)
        parts = after_equals.split(":")
        if len(parts) >= 2:
            return parts[0]
        return None
    except Exception:
        return None


def parse_indicator_code_from_urn(code_urn: str) -> str | None:
    """
    Parse indicator code from hierarchicalCode's code URN.

    Examples
    --------
    >>> parse_indicator_code_from_urn(
    ...     "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_FSIBSIS_INDICATOR(4.0+.0).INTINC"
    ... )
    'INTINC'
    """
    if not code_urn or "." not in code_urn:
        return None
    return code_urn.split(".")[-1]


def parse_codelist_id_from_urn(code_urn: str) -> str | None:
    """
    Parse codelist ID from hierarchicalCode's code URN.

    Examples
    --------
    >>> parse_codelist_id_from_urn("urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP_INDICATOR(10.0+.0).CAB")
    'CL_BOP_INDICATOR'
    """
    if not code_urn or ":" not in code_urn or "(" not in code_urn:
        return None
    try:
        # Extract everything after the last colon
        after_colon = code_urn.split(":")[-1]
        # Extract everything before the opening parenthesis
        codelist_id = after_colon.split("(")[0]
        return codelist_id
    except Exception:
        return None


def parse_search_query(query: str) -> list[list[str]]:
    """
    Parse a search query string into OR-groups of AND-terms.

    Supports:
    - Quoted phrases: "exact phrase"
    - OR operator: term1 | term2
    - AND operator (implicit or +): term1 term2, term1+term2
    - Stop words are filtered out (of, the, a, an, is, are, in, on, for, with, and, or)

    Examples
    --------
    >>> parse_search_query('inflation | "consumer price"')
    [['inflation'], ['consumer price']]
    >>> parse_search_query('gdp growth')
    [['gdp', 'growth']]
    """
    # pylint: disable=import-outside-toplevel
    import string as string_module

    STOP_WORDS = {  # pylint: disable=C0103
        "of",
        "the",
        "a",
        "an",
        "is",
        "are",
        "in",
        "on",
        "for",
        "with",
        "and",
        "or",
    }
    or_groups: list = []
    parts_by_or = [p.strip() for p in query.split("|")]

    for or_part in parts_by_or:
        if not or_part:
            continue

        current_and_group: list = []
        in_quote = False
        current_term: list = []

        # Add a space at the end to ensure the last term is processed
        for char in or_part + " ":
            if char == '"':
                if in_quote:
                    # End of a quoted term
                    if current_term:
                        term = "".join(current_term).lower()
                        current_and_group.append(term)
                        current_term = []
                    in_quote = False
                else:
                    # Start of a quoted term
                    if current_term:  # process term before quote
                        term = (
                            "".join(current_term)
                            .lower()
                            .strip(string_module.punctuation)
                        )
                        if term and term not in STOP_WORDS:
                            current_and_group.append(term)
                        current_term = []
                    in_quote = True
            elif (char == "+" or char.isspace()) and not in_quote:
                # End of a non-quoted term
                if current_term:
                    term = (
                        "".join(current_term).lower().strip(string_module.punctuation)
                    )
                    if term and term not in STOP_WORDS:
                        current_and_group.append(term)
                    current_term = []
            else:
                current_term.append(char)

        if current_and_group:
            or_groups.append(current_and_group)

    return or_groups


def build_time_period_params(
    constraints_response: dict | None,
) -> tuple[list[dict], str | None]:
    """
    Build time period parameters from a constraints API response.

    Extracts start date, end date, and series count from annotations.

    Parameters
    ----------
    constraints_response : dict | None
        The response from get_available_constraints

    Returns
    -------
    tuple[list[dict], str | None]
        A tuple of (options list, series_count) where options contains
        start/end date dicts with 'label' and 'value' keys.
    """
    if not constraints_response:
        return [], None

    full_response = constraints_response.get("full_response", {})
    content_constraints = full_response.get("data", {}).get("contentConstraints", [])
    annotations = (
        content_constraints[0].get("annotations", []) if content_constraints else []
    )

    start = end = series_count = None
    for annotation in annotations:
        ann_id = annotation.get("id")
        if ann_id == "time_period_start":
            start = annotation.get("title")
        elif ann_id == "time_period_end":
            end = annotation.get("title")
        elif ann_id == "series_count":
            series_count = annotation.get("title")

    options: list[dict] = []
    if start:
        options.append({"label": f"Start Date: {start}", "value": start})
    if end:
        options.append({"label": f"End Date: {end}", "value": end})

    return options, series_count


def parse_codelist_urn(urn: str) -> str | None:
    """
    Parse codelist ID from owningCodelistUrn.

    Examples
    --------
    >>> parse_codelist_urn(
    ...     "urn:sdmx:com.epam.quanthub.sdmxplus.infomodel.Glossary=IMF.STA:CL_FSIBSIS_INDICATOR(4.0+.0)"
    ... )
    'CL_FSIBSIS_INDICATOR'
    """
    if not urn or "=" not in urn:
        return None

    try:
        parts = urn.split("=")[-1]
        codelist_with_version = parts.split(":")[-1]
        codelist_id = codelist_with_version.split("(")[0]
        return codelist_id
    except Exception:
        return None


def extract_all_codelists_from_hierarchy(hierarchy: dict) -> set[str]:
    """
    Recursively extract ALL codelist IDs from a hierarchy's hierarchicalCodes.

    This ensures that hierarchies containing multiple codelists (e.g., labels,
    table levels, AND indicator codelists) are properly indexed for reverse lookup.

    Parameters
    ----------
    hierarchy : dict
        The hierarchy object containing hierarchicalCodes.

    Returns
    -------
    set[str]
        Set of all codelist IDs found in the hierarchy.
    """
    codelists: set[str] = set()

    def scan_codes(codes: list) -> None:
        for code in codes:
            code_urn = code.get("code", "")
            if code_urn:
                codelist_id = parse_codelist_id_from_urn(code_urn)
                if codelist_id:
                    codelists.add(codelist_id)
            # Recurse into nested hierarchicalCodes
            nested = code.get("hierarchicalCodes", [])
            if nested:
                scan_codes(nested)

    hcodes = hierarchy.get("hierarchicalCodes", [])
    if hcodes and isinstance(hcodes, list):
        scan_codes(hcodes)

    return codelists


def build_hierarchy_to_codelist_map(hierarchies: dict) -> dict[str, str]:
    """
    Build mapping from hierarchy ID to codelist ID.

    Parameters
    ----------
    hierarchies : dict
        Dictionary of hierarchy_id -> hierarchy data.

    Returns
    -------
    dict[str, str]
        Mapping from hierarchy ID to its primary codelist ID.
    """
    mapping: dict[str, str] = {}
    for hierarchy_id, hierarchy in hierarchies.items():
        codelist_id = None

        # Method 1: Check owningCodelistUrn annotation
        annotations = hierarchy.get("annotations", [])
        for annotation in annotations:
            if annotation.get("id") == "owningCodelistUrn":
                urn = annotation.get("text", "")
                codelist_id = parse_codelist_urn(urn)
                if codelist_id:
                    break

        # Method 2: Infer from first hierarchicalCode's code URN
        # Handles hierarchies like H_QGFS_* that don't have owningCodelistUrn
        if not codelist_id:
            hcodes = hierarchy.get("hierarchicalCodes", [])
            if hcodes and isinstance(hcodes, list) and hcodes:
                first_code = hcodes[0]
                code_urn = first_code.get("code", "")
                if code_urn:
                    codelist_id = parse_codelist_id_from_urn(code_urn)

        if codelist_id:
            mapping[hierarchy_id] = codelist_id

    return mapping


def build_codelist_to_hierarchies_map(hierarchies: dict) -> dict[str, list[str]]:
    """
    Build reverse mapping from codelist ID to list of hierarchy IDs.

    Unlike build_hierarchy_to_codelist_map (which maps to the primary codelist),
    this function indexes ALL codelists contained in each hierarchy. This ensures
    that hierarchies with nested codelists (e.g., H_FSIC_INDICATOR containing
    CL_FSI_LABELS, CL_FSIC_INDICATOR_LABELS, AND CL_FSIC_INDICATOR) are found
    when looking up any of their contained codelists.

    Parameters
    ----------
    hierarchies : dict
        Dictionary of hierarchy_id -> hierarchy data.

    Returns
    -------
    dict[str, list[str]]
        Mapping from codelist ID to list of hierarchy IDs containing it.
    """
    mapping: dict[str, list[str]] = {}
    for hierarchy_id, hierarchy in hierarchies.items():
        # Extract ALL codelists from this hierarchy (not just the first one)
        all_codelists = extract_all_codelists_from_hierarchy(hierarchy)
        for codelist_id in all_codelists:
            if codelist_id not in mapping:
                mapping[codelist_id] = []
            if hierarchy_id not in mapping[codelist_id]:
                mapping[codelist_id].append(hierarchy_id)
    return mapping


def translate_error_message(error_msg: str) -> str:
    """Translate IMF dimension codes to user-friendly parameter names in error messages.

    Maps internal IMF dimension names like COUNTRY, FREQUENCY, INDICATOR
    to user-facing parameter names like country, frequency, symbol/indicator.
    Also translates common IMF code values to user-friendly equivalents.
    """
    # Dimension code to parameter name mappings
    dim_to_param = {
        "COUNTRY": "country",
        "REF_AREA": "country",
        "JURISDICTION": "country",
        "COUNTERPART_AREA": "counterpart_country",
        "FREQUENCY": "frequency",
        "INDICATOR": "indicator",
        "CLASSIFICATION": "indicator",
        "SERIES": "indicator",
        "ITEM": "indicator",
        "SECTOR": "sector",
        "BOP_ACCOUNTING_ENTRY": "accounting_entry",
        "ACCOUNTING_ENTRY": "accounting_entry",
        "TYPE_OF_TRANSFORMATION": "transform",
        "PRICE_TYPE": "price_type",
        "S_ADJUSTMENT": "seasonal_adjustment",
        "UNIT_MEASURE": "unit",
        "UNIT_MULT": "unit_multiplier",
        "TIME_PERIOD": "time_period",
    }

    # Frequency value mappings
    frequency_map = {
        "'A'": "'annual'",
        "'Q'": "'quarter'",
        "'M'": "'month'",
        '"A"': '"annual"',
        '"Q"': '"quarter"',
        '"M"': '"month"',
    }

    # Apply dimension translations
    for dim_code, param_name in dim_to_param.items():
        error_msg = error_msg.replace(f"'{dim_code}'", f"'{param_name}'")
        error_msg = error_msg.replace(f'"{dim_code}"', f'"{param_name}"')
        # Also handle "dimension 'X'" pattern without quotes around dimension
        error_msg = error_msg.replace(
            f"dimension '{dim_code}'", f"'{param_name}' parameter"
        )
        # Handle dimension X: pattern
        error_msg = error_msg.replace(f"{dim_code} codes", f"{param_name} codes")

    # Apply frequency value translations
    for api_val, user_val in frequency_map.items():
        error_msg = error_msg.replace(api_val, user_val)

    return error_msg

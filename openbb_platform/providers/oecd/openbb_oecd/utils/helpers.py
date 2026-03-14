"""OECD helper functions.

Compatibility layer that re-exports utilities from the new infrastructure
(query_builder and metadata).  All data fetching goes through
OecdQueryBuilder.fetch_data().
"""

# pylint: disable=R0916, W0212

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from datetime import date
from typing import TYPE_CHECKING, Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_oecd.utils.query_builder import parse_time_period

if TYPE_CHECKING:
    from openbb_oecd.utils.metadata import OecdMetadata


def oecd_date_to_python_date(input_date: str | int) -> date | None:
    """Convert an SDMX time-period string to a Python date.

    Parameters
    ----------
    input_date : str | int
        SDMX time-period string (e.g. "2024", "2024-Q3").

    Returns
    -------
    date | None
        Parsed date, or None when *input_date* is empty or
        cannot be parsed.
    """
    raw = str(input_date).strip() if input_date else ""
    if not raw:
        return None
    s = parse_time_period(raw)
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        try:
            return date.fromisoformat(s[:10])
        except (ValueError, TypeError):
            return None


# Cleanup mapping for verbose/ugly OECD labels -> concise names.
# Applied after ASCII normalization.
_LABEL_OVERRIDES: dict[str, str] = {
    "china_people_s_republic_of": "china",
    "czech_republic": "czechia",
    "korea_republic_of": "korea",
    "european_union_27_countries_from_01_02_2020": "eu27",
    "european_union_15_countries": "eu15",
    "european_union_22_countries_in_oecd": "eu22_oecd",
    "euro_area_evolving_composition": "euro_area",
    "oecd_excluding_the_euro_area": "oecd_non_euro_area",
    "major_five_asia_economies": "asia5",
    "major_four_european_countries": "europe4",
    "dynamic_asian_economies": "dae",
    "other_major_oil_producers": "other_major_oil",
    "rest_of_the_world": "rest_of_world",
}


def normalize_country_label(label: str) -> str:
    """Normalize a country label to ASCII lower_snake_case.

    Examples
    --------
    >>> normalize_country_label("United States")
    'united_states'
    >>> normalize_country_label("China (People's Republic of)")
    'china'
    """
    # Decompose Unicode chars, then drop combining marks (accents)
    s = unicodedata.normalize("NFKD", label)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.strip().lower()
    # Keep only ASCII letters, digits, and whitespace
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return _LABEL_OVERRIDES.get(s, s)


def parse_search_query(query: str) -> list[list[str]]:
    """Parse a search query into AND-groups of OR-terms.

    Supports + (AND) and | (OR) operators and double-quoted phrases.

    Examples
    --------
    >>> parse_search_query('gdp "per capita" | income')
    [['gdp'], ['per capita', 'income']]
    >>> parse_search_query('consumer + price')
    [['consumer'], ['price']]
    """
    tokens: list[str] = []
    for match in re.finditer(r'"([^"]+)"|(\S+)', query):
        tokens.append(match.group(1) or match.group(2))

    groups: list[list[str]] = [[]]
    for token in tokens:
        low = token.lower()
        if low == "+":
            groups.append([])
        elif low == "|":
            continue  # next token added to current group
        else:
            groups[-1].append(token.lower())

    return [g for g in groups if g]


# Dimensions to exclude from compound-code matching — they are handled
# separately via dedicated parameters (country, frequency).
_EXCLUDE_DIMS = frozenset(
    {
        "FREQUENCY",
        "FREQ",
        "TIME_PERIOD",
        "REF_AREA",
        "COUNTERPART_AREA",
        "JURISDICTION",
        "COUNTRY",
        "AREA",
    }
)


def _parse_compound_code(
    code: str,
    code_to_dimension: dict[str, str],
) -> tuple[list[tuple[str, str]], list[str]]:
    """Parse a compound code like ``CPI_CP01_N`` into dimension matches.

    Uses greedy matching to find the longest combination first.

    Returns
    -------
    tuple
        ``(matched_parts, unmatched_parts)`` where *matched_parts* is a
        list of ``(dimension_id, matched_code)`` tuples.
    """
    parts = code.split("_")
    matched_parts: list[tuple[str, str]] = []
    unmatched_parts: list[str] = []

    i = 0
    while i < len(parts):
        matched = False
        # Try longest possible combination first (greedy).
        for j in range(len(parts), i, -1):
            combined = "_".join(parts[i:j])
            if combined in code_to_dimension:
                dim_id = code_to_dimension[combined]
                # Don't match the same dimension twice.
                if not any(m[0] == dim_id for m in matched_parts):
                    matched_parts.append((dim_id, combined))
                    i = j
                    matched = True
                    break
        if not matched:
            unmatched_parts.append(parts[i])
            i += 1

    return matched_parts, unmatched_parts


def _build_dimension_lookups(
    dataflow: str,
    metadata: OecdMetadata | None = None,
) -> tuple[dict[str, str], dict[str, set[str]], list[str]]:
    """Build lookups for mapping codes to dimensions.

    Returns
    -------
    tuple
        ``(code_to_dimension, codes_by_dimension, dimension_order)``

        - *code_to_dimension*: maps any valid code to its dimension ID
        - *codes_by_dimension*: maps dimension ID to its set of valid codes
        - *dimension_order*: list of dimension IDs in DSD position order
          (excluding country/frequency/time dimensions)
    """
    # pylint: disable=import-outside-toplevel
    from openbb_oecd.utils.metadata import OecdMetadata

    if metadata is None:
        metadata = OecdMetadata()

    code_to_dimension: dict[str, str] = {}
    codes_by_dimension: dict[str, set[str]] = defaultdict(set)
    dimension_order: list[str] = []

    try:
        all_params = metadata.get_dataflow_parameters(dataflow)

        for dim_id, values in all_params.items():
            if dim_id.upper() in _EXCLUDE_DIMS:
                continue
            for v in values:
                code = v.get("value")
                if code:
                    codes_by_dimension[dim_id].add(code)
                    if code not in code_to_dimension:
                        code_to_dimension[code] = dim_id
    except Exception:  # noqa: BLE001, S110
        pass

    # Build dimension order from DSD (excluding country/freq/time/transform).
    try:
        full_id = metadata._resolve_dataflow_id(dataflow)
        metadata._ensure_structure(full_id)
        dsd = metadata.datastructures.get(full_id, {})

        trailing_dims = {
            "FREQUENCY",
            "FREQ",
            "TIME_PERIOD",
            "TRANSFORMATION",
            "UNIT_MEASURE",
            "ADJUSTMENT",
        }
        for dim in sorted(dsd.get("dimensions", []), key=lambda d: d["position"]):
            dim_id = dim.get("id", "")
            if (
                dim_id
                and dim_id.upper() not in trailing_dims
                and dim_id.upper() not in _EXCLUDE_DIMS
                and "TRANSFORM" not in dim_id.upper()
            ):
                dimension_order.append(dim_id)
    except Exception:  # noqa: BLE001, S110
        pass

    return code_to_dimension, dict(codes_by_dimension), dimension_order


def detect_indicator_dimensions(
    dataflow: str,
    indicator_codes: list[str],
    metadata: OecdMetadata | None = None,
) -> dict[str, list[str]]:
    """Detect which dimension(s) each indicator code belongs to.

    Supports compound codes that span multiple dimensions, decomposing
    them via greedy matching against all DSD dimension codelists.

    Parameters
    ----------
    dataflow : str
        OECD dataflow ID.
    indicator_codes : list[str]
        One or more indicator codes (may be compound, e.g. ``"CPI_CP01_N"``).
    metadata : OecdMetadata, optional
        Metadata singleton.  Created lazily if not provided.

    Returns
    -------
    dict[str, list[str]]
        ``{dimension_id: [code, ...]}``.

    Raises
    ------
    OpenBBError
        If any indicator code cannot be resolved for the dataflow.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_oecd.utils.metadata import OecdMetadata

    if metadata is None:
        metadata = OecdMetadata()

    dimension_codes: dict[str, list[str]] = defaultdict(list)

    try:
        code_to_dimension, codes_by_dimension, dimension_order = (
            _build_dimension_lookups(dataflow, metadata)
        )

        # Determine a reasonable primary dimension for wildcards.
        primary_dim = _guess_primary_dimension(codes_by_dimension)

        invalid_codes: list[tuple[str, list[str]]] = []
        for code in indicator_codes:
            if code == "*":
                dimension_codes[primary_dim].append(code)
            elif code in code_to_dimension:
                dim_id = code_to_dimension[code]
                dimension_codes[dim_id].append(code)
            else:
                # Try compound-code decomposition.
                matched_parts, unmatched = _parse_compound_code(code, code_to_dimension)
                if matched_parts and not unmatched:
                    for dim_id, code_part in matched_parts:
                        if code_part not in dimension_codes[dim_id]:
                            dimension_codes[dim_id].append(code_part)
                else:
                    invalid_codes.append((code, unmatched))

        if invalid_codes:
            _raise_invalid_codes_error(
                dataflow,
                invalid_codes,
                code_to_dimension,
                codes_by_dimension,
                dimension_order,
            )

    except OpenBBError:
        raise
    except Exception:  # noqa: BLE001
        # Fallback: put all codes in a generic INDICATOR dimension.
        dimension_codes["INDICATOR"] = indicator_codes

    return dict(dimension_codes)


def _guess_primary_dimension(
    codes_by_dimension: dict[str, set[str]],
) -> str:
    """Return the most likely primary indicator dimension name."""
    # pylint: disable=import-outside-toplevel
    from openbb_oecd.utils.metadata import _INDICATOR_DIMENSION_CANDIDATES

    for candidate in _INDICATOR_DIMENSION_CANDIDATES:
        if candidate in codes_by_dimension:
            return candidate
    # Fallback: first dimension with codes, or generic "INDICATOR".
    if codes_by_dimension:
        return next(iter(codes_by_dimension))
    return "INDICATOR"


def _raise_invalid_codes_error(
    dataflow: str,
    invalid_codes: list[tuple[str, list[str]]],
    code_to_dimension: dict[str, str],
    codes_by_dimension: dict[str, set[str]],
    dimension_order: list[str],
) -> None:
    """Build and raise a detailed error for invalid indicator codes."""
    country_dims = {"COUNTRY", "REF_AREA"}
    error_parts: list[str] = []

    for code, unmatched in invalid_codes:
        if not unmatched:
            error_parts.append(f"'{code}'")
            continue

        parts = code.split("_")
        segments: list[tuple[str, str | None]] = []

        i = 0
        while i < len(parts):
            found = False
            for j in range(len(parts), i, -1):
                combined = "_".join(parts[i:j])
                if combined in code_to_dimension:
                    segments.append((combined, code_to_dimension[combined]))
                    i = j
                    found = True
                    break
            if not found:
                segments.append((parts[i], None))
                i += 1

        has_country = any(dim_id in country_dims for _, dim_id in segments if dim_id)
        effective_order = (
            dimension_order
            if has_country
            else [d for d in dimension_order if d not in country_dims]
        )

        first_matched_idx: Any = None
        first_matched_pos: Any = None
        for idx, (_, dim_id) in enumerate(segments):
            if dim_id and dim_id in effective_order:
                first_matched_idx = idx
                first_matched_pos = effective_order.index(dim_id)
                break

        segment_errors: list[str] = []
        for idx, (seg, dim_id) in enumerate(segments):
            if dim_id is not None:
                continue
            if first_matched_idx is not None and first_matched_pos is not None:
                expected_pos = first_matched_pos - (first_matched_idx - idx)
            else:
                expected_pos = idx

            if 0 <= expected_pos < len(effective_order):
                expected_dim = effective_order[expected_pos]
                sample = sorted(codes_by_dimension.get(expected_dim, set()))[:5]
                segment_errors.append(
                    f"'{seg}' is invalid for {expected_dim} (valid: {', '.join(sample)})"
                )
            else:
                segment_errors.append(f"'{seg}' is unrecognized")

        error_parts.append(f"'{code}': {'; '.join(segment_errors)}")

    raise OpenBBError(
        f"Invalid indicator code(s) for dataflow '{dataflow}': "
        f"{'; '.join(error_parts)}. "
        f"Use `obb.economy.available_indicators(provider='oecd', dataflows='{dataflow}')` "
        f"to see all valid codes."
    )


def detect_transform_dimension(
    dataflow: str,
    metadata: OecdMetadata | None = None,
) -> tuple[str | None, str | None, dict[str, str], dict[str, str]]:
    """Detect transformation and unit dimensions for a dataflow.

    Dynamically finds dimensions containing ``TRANSFORM`` or ``UNIT`` in
    their names and builds a user-friendly lookup mapping.

    Parameters
    ----------
    dataflow : str
        OECD dataflow ID.
    metadata : OecdMetadata, optional
        Metadata singleton.

    Returns
    -------
    tuple
        ``(transform_dim, unit_dim, transform_lookup, unit_lookup)``
        where lookups map friendly names to SDMX codes.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_oecd.utils.metadata import OecdMetadata

    if metadata is None:
        metadata = OecdMetadata()

    transform_dim: str | None = None
    unit_dim: str | None = None
    transform_lookup: dict[str, str] = {}
    unit_lookup: dict[str, str] = {}

    try:
        params = metadata.get_dataflow_parameters(dataflow)

        for dim, values in params.items():
            dim_upper = dim.upper()

            if "TRANSFORM" in dim_upper or dim_upper == "ADJUSTMENT":
                transform_dim = dim
                for v in values:
                    code = v.get("value", "")
                    label = v.get("label", "").lower()

                    is_simple = (
                        not code.startswith("SRP_")
                        and not code.startswith("WGT")
                        and not code.startswith("SA_")
                    )

                    if (
                        label == "index"
                        or (
                            "index" in label
                            and "change" not in label
                            and "percent" not in label
                        )
                    ) and ("index" not in transform_lookup or is_simple):
                        transform_lookup["index"] = code

                    if (
                        "year-over-year" in label
                        or "yoy" in label
                        or "year ago" in label
                    ) and ("yoy" not in transform_lookup or is_simple):
                        transform_lookup["yoy"] = code

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

                    if ("domestic currency" in label or label == "currency") and (
                        "currency" not in transform_lookup or is_simple
                    ):
                        transform_lookup["currency"] = code

                    # Direct code access (case-insensitive).
                    transform_lookup[code.lower()] = code

            elif dim_upper in ("UNIT_MEASURE", "UNIT"):
                unit_dim = dim
                for v in values:
                    code = v.get("value", "")
                    label = v.get("label", "").lower()

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

                    unit_lookup[code.lower()] = code

    except (KeyError, ValueError):
        pass

    return transform_dim, unit_dim, transform_lookup, unit_lookup


def resolve_country_code(
    country: str,
    metadata: OecdMetadata | None = None,
    dataflow: str | None = None,
) -> str:
    """Resolve a single country name or code to an ISO country code.

    Parameters
    ----------
    country : str
        Country name or code (e.g. ``"Japan"``, ``"JPN"``).
    metadata : OecdMetadata, optional
        Metadata singleton.
    dataflow : str, optional
        Dataflow whose country codelist to search.  If omitted, returns
        the upper-cased input.

    Returns
    -------
    str
        Resolved country code, or upper-cased input if resolution fails.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_oecd.utils.metadata import OecdMetadata

    if metadata is None:
        metadata = OecdMetadata()

    if not dataflow:
        return country.upper().strip()

    try:
        resolved = metadata.resolve_country_codes(dataflow, country)
        return resolved[0] if resolved else country.upper().strip()
    except Exception:  # noqa: BLE001
        return country.upper().strip()

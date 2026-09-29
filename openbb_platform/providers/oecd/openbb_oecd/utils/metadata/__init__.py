"""OECD SDMX metadata package.

Re-exports all public symbols so existing imports continue to work:

    from openbb_oecd.utils.metadata import OecdMetadata, _TABLE_GROUP_CANDIDATES, ...
"""

from openbb_oecd.utils.metadata._constants import (
    _COUNTRY_DIMENSION_CANDIDATES,
    _DATA_ACCEPT_CSV,
    _DATA_ACCEPT_CSV_LABELS,
    _INDICATOR_DIMENSION_CANDIDATES,
    _NON_INDICATOR_DIMENSIONS,
    _SHIPPED_CACHE_DIR,
    _SHIPPED_CACHE_FILE,
    _STRUCTURE_ACCEPT,
    _TABLE_GROUP_CANDIDATES,
    BASE_URL,
)
from openbb_oecd.utils.metadata._core import OecdMetadata, OECDMetadataDependency
from openbb_oecd.utils.metadata._helpers import (
    _build_code_tree,
    _extract_codelist_id_from_urn,
    _extract_concept_id_from_urn,
    _get_user_cache_file,
    _make_request,
    _matches_query,
    _normalize_label,
    _parse_sdmx_json_codelists,
    _parse_search_query,
    _term_matches,
)

__all__ = [
    "BASE_URL",
    "OecdMetadata",
    "OECDMetadataDependency",
    "_COUNTRY_DIMENSION_CANDIDATES",
    "_DATA_ACCEPT_CSV",
    "_DATA_ACCEPT_CSV_LABELS",
    "_INDICATOR_DIMENSION_CANDIDATES",
    "_NON_INDICATOR_DIMENSIONS",
    "_SHIPPED_CACHE_DIR",
    "_SHIPPED_CACHE_FILE",
    "_STRUCTURE_ACCEPT",
    "_TABLE_GROUP_CANDIDATES",
    "_build_code_tree",
    "_extract_codelist_id_from_urn",
    "_extract_concept_id_from_urn",
    "_get_user_cache_file",
    "_make_request",
    "_matches_query",
    "_normalize_label",
    "_parse_sdmx_json_codelists",
    "_parse_search_query",
    "_term_matches",
]

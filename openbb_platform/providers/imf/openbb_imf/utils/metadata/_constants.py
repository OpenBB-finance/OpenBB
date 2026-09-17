"""IMF SDMX metadata constants."""

from __future__ import annotations

from pathlib import Path

BASE_URL = "https://api.imf.org/external/sdmx/3.0"

_STRUCTURE_ACCEPT = "application/json"
_USER_AGENT = "Open Data Platform - IMF Metadata Utility"

_SHIPPED_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
_SHIPPED_CACHE_FILE = _SHIPPED_CACHE_DIR / "imf_cache.json.xz"

INDICATOR_DIMENSION_CANDIDATES: tuple[str, ...] = (
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
)

INDICATOR_DIMENSION_SUBSTRINGS: tuple[str, ...] = (
    "INDICATOR",
    "ACCOUNTING_ENTRY",
    "ENTRY",
)

COUNTRY_DIMENSION_CANDIDATES: frozenset[str] = frozenset(
    {"JURISDICTION", "REF_AREA", "COUNTRY", "AREA"}
)

COUNTRY_CONCEPT_CANDIDATES: frozenset[str] = frozenset({"COUNTRY", "REF_AREA"})

DEPTH_OVERRIDE_DATAFLOWS: frozenset[str] = frozenset({"BOP", "BOP_AGG", "IIP", "IIPCC"})

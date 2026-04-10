"""Module-level constants for OECD SDMX metadata."""

from pathlib import Path

BASE_URL = "https://sdmx.oecd.org/public/rest/v2"
_STRUCTURE_ACCEPT = "application/vnd.sdmx.structure+json; version=1.0; charset=utf-8"
_DATA_ACCEPT_CSV = "application/vnd.sdmx.data+csv; charset=utf-8"
_DATA_ACCEPT_CSV_LABELS = "application/vnd.sdmx.data+csv; charset=utf-8; labels=both"
_SHIPPED_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
_SHIPPED_CACHE_FILE = _SHIPPED_CACHE_DIR / "oecd_cache.json.xz"

_INDICATOR_DIMENSION_CANDIDATES = (
    "MEASURE",
    "INDICATOR",
    "SUBJECT",
    "TRANSACTION",
    "ACTIVITY",
    "PRODUCT",
    "SERIES",
    "ITEM",
    "ACCOUNTING_ENTRY",
    "SECTOR",
)
_COUNTRY_DIMENSION_CANDIDATES = (
    "REF_AREA",
    "COUNTERPART_AREA",
    "JURISDICTION",
    "COUNTRY",
    "AREA",
)
_TABLE_GROUP_CANDIDATES = (
    "TABLE_IDENTIFIER",
    "CHAPTER",
)
_NON_INDICATOR_DIMENSIONS = frozenset(
    {
        "FREQ",
        "ADJUSTMENT",
        "TRANSFORMATION",
        "UNIT_MEASURE",
        "UNIT_MULT",
        "CURRENCY_DENOM",
        "CURRENCY",
        "VALUATION",
        "PRICE_BASE",
        "CONSOLIDATION",
        "MATURITY",
        "METHODOLOGY",
        "TABLE_IDENTIFIER",
        "TIME_PERIOD",
        "COUNTERPART_AREA",
        "DEBT_BREAKDOWN",
    }
)

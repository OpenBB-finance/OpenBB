"""Constants for the ECB SDMX metadata layer."""

from __future__ import annotations

from pathlib import Path

BASE_URL = "https://data-api.ecb.europa.eu/service"
AGENCY = "ECB"

# Structure (metadata) is SDMX-ML 2.1 only — JSON is rejected (HTTP 406).
STRUCTURE_HEADERS = {
    "Accept": "application/xml",
    "User-Agent": "OpenBB Platform - ECB",
}

# The shipped, build-time metadata cache (gitignored; materialized by
# ``generate_cache.py`` via the Hatchling build hook).
SHIPPED_CACHE_FILE = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "ecb_cache.json.xz"
)

# SDMX-ML 2.1 namespaces (shared by structure responses).
NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# Cap on how many codelist values are inlined into a dimension-discovery
# response, to keep payloads bounded for very large codelists.
MAX_DIMENSION_VALUES = 3000

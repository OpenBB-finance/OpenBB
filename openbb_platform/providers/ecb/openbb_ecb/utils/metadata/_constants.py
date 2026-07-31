"""Constants for the ECB SDMX metadata layer."""

from __future__ import annotations

from pathlib import Path

BASE_URL = "https://data-api.ecb.europa.eu/service"
AGENCY = "ECB"

STRUCTURE_HEADERS = {
    "Accept": "application/xml",
    "User-Agent": "OpenBB Platform - ECB",
}

SHIPPED_CACHE_FILE = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "ecb_cache.json.xz"
)

NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

MAX_DIMENSION_VALUES = 3000

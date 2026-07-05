"""Module-level constants for the metadata subsystem."""

from __future__ import annotations

from pathlib import Path

BOC_VALET_BASE_URL = "https://www.bankofcanada.ca/valet"
STATSCAN_HOMEPAGE_JSON_URL = (
    "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
)
STATSCAN_SDMX_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/sdmx"
STATSCAN_REST_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"

_SHIPPED_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
_SHIPPED_CACHE_FILE = _SHIPPED_CACHE_DIR / "government_ca_cache.json.xz"


def _user_cache_dir() -> Path:
    """Return the user-writable cache directory for this extension."""
    import os

    base = os.environ.get(
        "OPENBB_GOVERNMENT_CA_CACHE_DIR",
        str(Path.home() / ".cache" / "openbb" / "government_ca"),
    )
    return Path(base)


def _USER_CACHE_FILE() -> Path:  # noqa: N802 - expose as a constant-like symbol
    """Return the user-writable cache file path (created on first write)."""
    return _user_cache_dir() / "government_ca_cache.json.gz"

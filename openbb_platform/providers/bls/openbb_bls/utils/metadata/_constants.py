"""Cache-asset paths and stable runtime constants."""

from pathlib import Path

_SHIPPED_CACHE_FILE = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "bls_cache.zip"
)

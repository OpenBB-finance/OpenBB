"""Module-level constants for the metadata subsystem.

Mirrors the layout of ``openbb_oecd.utils.metadata._constants`` but
scoped to the two upstream APIs this extension reads (BoC Valet +
StatsCan). Keeping the URLs here means the cache generator
(Fase 2/3), the fetchers (Fase 4/5), and the metadata singleton all
share one source of truth.
"""

from __future__ import annotations

from pathlib import Path

# Upstream API base URLs (re-exported from utils/constants so both
# layers can import from a single place if needed).
BOC_VALET_BASE_URL = "https://www.bankofcanada.ca/valet"
STATSCAN_HOMEPAGE_JSON_URL = (
    "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
)
STATSCAN_SDMX_BASE_URL = "https://www150.statcan.gc.ca/n1/dai-quo/ssi/asp/sdmx"

# Cache file locations. The shipped cache is bundled in the wheel/sdist;
# the user cache is an opt-in override that lives under the user's
# platformdirs-style config dir. We don't pull in platformdirs as a
# dependency — we use ``~/.cache/openbb/government_ca/`` to match the
# convention already in use by ``openbb-oecd``.
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

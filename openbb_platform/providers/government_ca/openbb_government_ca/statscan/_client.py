"""StatsCan runtime HTTP client with diskcache TTL.

Caches WDS REST responses on disk with a per-call TTL keyed by the
release schedule of the underlying series. StatsCan publishes new
data every business day at 8:30 EST, so the default TTLs are:

- daily series: 12 hours (covers the next business-day release)
- monthly series: 7 days
- quarterly series: 30 days
- annual series: 90 days
- cube metadata: 24 hours (changes rarely)

The cache lives at ``~/.cache/openbb/government_ca/statscan_cache/``.
Each entry is a JSON file with ``{value, expires_at}`` so we don't
need a third-party ``diskcache`` dependency.
"""

from __future__ import annotations

import contextlib
import json
import os
import time
from pathlib import Path
from typing import Any

from openbb_government_ca.utils._http import NetworkError, http_get_json
from openbb_government_ca.utils.metadata import STATSCAN_REST_BASE_URL

_DEFAULT_CACHE_DIR = (
    Path.home() / ".cache" / "openbb" / "government_ca" / "statscan_cache"
)

_TTL_BY_FREQUENCY: dict[str, int] = {
    "daily": 12 * 3600,
    "weekly": 3 * 24 * 3600,
    "monthly": 7 * 24 * 3600,
    "quarterly": 30 * 24 * 3600,
    "annual": 90 * 24 * 3600,
    "metadata": 24 * 3600,
}

_DEFAULT_TTL = 12 * 3600


def _cache_dir() -> Path:
    """Return the diskcache directory (overridable via env var)."""
    base = os.environ.get(
        "OPENBB_GOVERNMENT_CA_STATSCAN_CACHE_DIR",
        str(_DEFAULT_CACHE_DIR),
    )
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _cache_key(url: str) -> str:
    """Hash *url* into a filesystem-safe filename."""
    import hashlib

    return hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json"


def _cache_get(url: str) -> tuple[Any, bool]:
    """Return ``(value, hit)`` from the diskcache.

    ``hit`` is ``True`` only when the entry is fresh (within TTL). The
    stale value is still returned (as the first element of the tuple)
    so callers can fall back to it on network errors.
    """
    path = _cache_dir() / _cache_key(url)
    if not path.exists():
        return (None, False)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (None, False)
    expires_at = raw.get("expires_at", 0)
    if time.time() > expires_at:
        return (raw.get("value"), False)
    return (raw.get("value"), True)


def _cache_set(url: str, value: Any, ttl_seconds: int) -> None:
    """Write *value* to the diskcache with a TTL."""
    path = _cache_dir() / _cache_key(url)
    payload = {"value": value, "expires_at": time.time() + ttl_seconds}
    with contextlib.suppress(OSError):
        path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def ttl_for_frequency(frequency_code: str | None) -> int:
    """Return the diskcache TTL (seconds) for a StatsCan frequency code.

    StatsCan frequency codes (per the WDS user guide code set):
    - ``1`` = daily
    - ``2`` = weekly
    - ``6`` = monthly
    - ``7`` = quarterly
    - ``9`` = annual
    """
    if not frequency_code:
        return _DEFAULT_TTL
    mapping = {
        "1": "daily",
        "2": "weekly",
        "6": "monthly",
        "7": "quarterly",
        "9": "annual",
    }
    return _TTL_BY_FREQUENCY.get(mapping.get(frequency_code, ""), _DEFAULT_TTL)


class StatsCanClient:
    """HTTP client for the StatsCan WDS REST API with diskcache TTL."""

    def __init__(self, base_url: str = STATSCAN_REST_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def _get(
        self,
        path_or_url: str,
        *,
        params: dict[str, Any] | None = None,
        ttl_seconds: int,
        timeout: float = 30.0,
    ) -> Any:
        """GET with diskcache; ``path_or_url`` may be relative or absolute."""
        url = (
            path_or_url
            if path_or_url.startswith("http")
            else f"{self.base_url}/{path_or_url.lstrip('/')}"
        )
        cache_url = url
        if params:
            import urllib.parse

            cache_url = f"{url}?{urllib.parse.urlencode(sorted(params.items()))}"

        cached, hit = _cache_get(cache_url)
        if hit:
            return cached

        try:
            value = http_get_json(url, params=params, timeout=timeout)
        except NetworkError:
            if cached is not None:
                return cached
            raise

        _cache_set(cache_url, value, ttl_seconds)
        return value

    def get_cube_metadata(self, pid: str) -> list[dict[str, Any]]:
        """Return the metadata for a cube (PID).

        Response is a list of one dict; we return it as-is so callers
        can access ``dimension``, ``series``, ``cansimId``, etc.
        """
        payload = self._get(
            "getCubeMetadata",
            params={"productId": pid},
            ttl_seconds=_TTL_BY_FREQUENCY["metadata"],
        )
        if not isinstance(payload, list):
            return []
        return payload

    def get_full_cube_list_lite(self) -> list[dict[str, Any]]:
        """Return the lite cube list (all cubes with PID + title + frequency)."""
        payload = self._get(
            "getAllCubesListLite",
            ttl_seconds=_TTL_BY_FREQUENCY["metadata"],
            timeout=60.0,
        )
        if not isinstance(payload, list):
            return []
        return payload

    def get_data_from_vectors_and_latest_n_periods(
        self,
        vector_ids: list[str],
        n_periods: int,
    ) -> list[dict[str, Any]]:
        """Fetch the latest *n_periods* observations for each vector ID."""
        if not vector_ids:
            return []
        params = [("vectorIds", str(vid).lstrip("Vv")) for vid in vector_ids]
        params.append(("endPeriod", str(n_periods)))
        url = f"{self.base_url}/getDataFromVectorsAndLatestNPeriods?" + "&".join(
            f"{k}={v}" for k, v in params
        )
        payload = self._get(
            url,
            ttl_seconds=_DEFAULT_TTL,
            timeout=30.0,
        )
        if not isinstance(payload, list):
            return []
        return payload

    def get_data_from_vector_by_reference_period_range(
        self,
        vector_id: str,
        start_ref_period: str,
        end_ref_period: str,
        *,
        frequency_code: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch observations for a single vector between two reference periods."""
        vid = str(vector_id).lstrip("Vv")
        params = {
            "vectorId": vid,
            "startRefPeriod": start_ref_period,
            "endReferencePeriod": end_ref_period,
        }
        payload = self._get(
            "getDataFromVectorByReferencePeriodRange",
            params=params,
            ttl_seconds=ttl_for_frequency(frequency_code),
            timeout=30.0,
        )
        if not isinstance(payload, list):
            return []
        return payload

    def get_full_table_download_sdmx(self, pid: str) -> bytes:
        """Download a full cube table in SDMX-ML format.

        Returns raw bytes; SDMX is XML, not JSON, so we bypass the
        JSON cache layer and stream the response directly. The caller
        is responsible for parsing the SDMX-ML.
        """
        import requests

        url = f"{self.base_url}/getFullTableDownloadSDMX/{pid}"
        response = requests.get(url, timeout=120.0)
        response.raise_for_status()
        return response.content

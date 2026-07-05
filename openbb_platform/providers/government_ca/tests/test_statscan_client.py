"""Tests for ``openbb_government_ca.statscan._client``.

Covers the diskcache TTL behavior, fallback to stale cache on
network errors, frequency-code-to-TTL mapping, and the per-call
helper methods (cube metadata, full cube list, vector data).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from openbb_government_ca.statscan import _client
from openbb_government_ca.statscan._client import (
    StatsCanClient,
    _cache_get,
    _cache_key,
    _cache_set,
    ttl_for_frequency,
)


@pytest.fixture
def isolated_cache_dir(tmp_path, monkeypatch):
    """Redirect the diskcache to a temp dir for the duration of the test."""
    monkeypatch.setenv("OPENBB_GOVERNMENT_CA_STATSCAN_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(_client, "_DEFAULT_CACHE_DIR", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# ttl_for_frequency
# ---------------------------------------------------------------------------
class TestTtlForFrequency:
    """``ttl_for_frequency`` maps StatsCan frequency codes to TTLs."""

    def test_daily(self):
        assert ttl_for_frequency("1") == 12 * 3600

    def test_weekly(self):
        assert ttl_for_frequency("2") == 3 * 24 * 3600

    def test_monthly(self):
        assert ttl_for_frequency("6") == 7 * 24 * 3600

    def test_quarterly(self):
        assert ttl_for_frequency("7") == 30 * 24 * 3600

    def test_annual(self):
        assert ttl_for_frequency("9") == 90 * 24 * 3600

    def test_unknown_code_falls_back_to_default(self):
        assert ttl_for_frequency("999") == 12 * 3600

    def test_none_code_falls_back_to_default(self):
        assert ttl_for_frequency(None) == 12 * 3600


# ---------------------------------------------------------------------------
# Cache primitives
# ---------------------------------------------------------------------------
class TestCachePrimitives:
    """``_cache_get`` / ``_cache_set`` round-trip and expiry."""

    def test_cache_key_is_stable(self):
        assert _cache_key("https://example.com") == _cache_key("https://example.com")

    def test_cache_key_differs_for_different_urls(self):
        assert _cache_key("https://a.com") != _cache_key("https://b.com")

    def test_set_then_get_round_trip(self, isolated_cache_dir):
        _cache_set("https://example.com", {"data": 42}, ttl_seconds=60)
        value, hit = _cache_get("https://example.com")
        assert hit is True
        assert value == {"data": 42}

    def test_get_returns_miss_when_no_entry(self, isolated_cache_dir):
        value, hit = _cache_get("https://not-set.com")
        assert hit is False
        assert value is None

    def test_expired_entry_returns_miss(self, isolated_cache_dir):
        _cache_set("https://example.com", {"data": 1}, ttl_seconds=-1)
        value, hit = _cache_get("https://example.com")
        # Stale value is returned (for fallback); hit is False because TTL expired.
        assert hit is False
        assert value == {"data": 1}

    def test_malformed_cache_file_returns_miss(self, isolated_cache_dir):
        path = isolated_cache_dir / _cache_key("https://example.com")
        path.write_text("not valid json", encoding="utf-8")
        value, hit = _cache_get("https://example.com")
        assert hit is False
        assert value is None


# ---------------------------------------------------------------------------
# StatsCanClient — caching behavior
# ---------------------------------------------------------------------------
class TestStatsCanClientCaching:
    """``StatsCanClient._get`` uses the diskcache and avoids repeat calls."""

    def test_get_caches_response(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"hello": "world"},
        ) as mock_http:
            r1 = client._get("endpoint", ttl_seconds=60)
            r2 = client._get("endpoint", ttl_seconds=60)
            assert r1 == {"hello": "world"}
            assert r2 == {"hello": "world"}
            assert mock_http.call_count == 1  # second call was cached

    def test_get_with_params_caches_differently_than_without(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"data": 1},
        ):
            client._get("endpoint", params={"a": "1"}, ttl_seconds=60)
            client._get("endpoint", params={"a": "2"}, ttl_seconds=60)
            client._get("endpoint", params={"a": "1"}, ttl_seconds=60)
        # Two unique URLs → two HTTP calls. Third is a cache hit.

    def test_get_falls_back_to_stale_cache_on_network_error(self, isolated_cache_dir):
        from openbb_government_ca.utils._http import NetworkError

        client = StatsCanClient("https://api.example.com")
        url = "https://api.example.com/endpoint"

        # Populate the cache with an EXPIRED entry so that ``_cache_get``
        # reports ``hit=False`` but still returns the stale value.
        _cache_set(url, {"cached": True}, ttl_seconds=-1)

        # Now make the HTTP call raise — the stale cache should be returned.
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            side_effect=NetworkError(url, "boom"),
        ):
            result = client._get("endpoint", ttl_seconds=60)
        assert result == {"cached": True}

    def test_get_raises_when_no_cache_and_network_error(self, isolated_cache_dir):
        from openbb_government_ca.utils._http import NetworkError

        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            side_effect=NetworkError("https://api.example.com/missing", "boom"),
        ):
            with pytest.raises(NetworkError):
                client._get("missing", ttl_seconds=60)

    def test_get_with_absolute_url_does_not_prepend_base(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        absolute = "https://other.example.com/data"
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"ok": True},
        ) as mock_http:
            client._get(absolute, ttl_seconds=60)
            mock_http.assert_called_once_with(absolute, params=None, timeout=30.0)


# ---------------------------------------------------------------------------
# StatsCanClient — wrapper methods
# ---------------------------------------------------------------------------
class TestStatsCanClientMethods:
    """``get_cube_metadata`` / ``get_full_cube_list_lite`` / etc."""

    def test_get_cube_metadata_returns_list(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value=[{"productId": "10100139"}],
        ):
            result = client.get_cube_metadata("10100139")
        assert result == [{"productId": "10100139"}]

    def test_get_cube_metadata_returns_empty_on_non_list(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"unexpected": "shape"},
        ):
            result = client.get_cube_metadata("10100139")
        assert result == []

    def test_get_full_cube_list_lite_returns_list(self, isolated_cache_dir):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value=[{"productId": "1"}, {"productId": "2"}],
        ):
            result = client.get_full_cube_list_lite()
        assert len(result) == 2

    def test_get_full_cube_list_lite_returns_empty_on_non_list(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value=None,
        ):
            result = client.get_full_cube_list_lite()
        assert result == []

    def test_get_data_from_vectors_and_latest_n_periods_returns_list(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value=[{"vectorDataPoint": []}],
        ):
            result = client.get_data_from_vectors_and_latest_n_periods(
                ["V1", "V2"], n_periods=12
            )
        assert len(result) == 1

    def test_get_data_from_vectors_returns_empty_for_empty_input(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch("openbb_government_ca.statscan._client.http_get_json") as mock_http:
            result = client.get_data_from_vectors_and_latest_n_periods([], 12)
        assert result == []
        assert mock_http.call_count == 0

    def test_get_data_from_vectors_returns_empty_on_non_list_payload(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"unexpected": "shape"},
        ):
            result = client.get_data_from_vectors_and_latest_n_periods(
                ["V1"], n_periods=12
            )
        assert result == []

    def test_get_data_from_vector_by_reference_period_range_returns_list(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value=[{"refPer": "2024-01"}],
        ):
            result = client.get_data_from_vector_by_reference_period_range(
                "V1", "2024-01", "2024-12"
            )
        assert len(result) == 1

    def test_get_data_from_vector_by_reference_period_range_returns_empty_on_non_list(
        self, isolated_cache_dir
    ):
        client = StatsCanClient("https://api.example.com")
        with patch(
            "openbb_government_ca.statscan._client.http_get_json",
            return_value={"unexpected": True},
        ):
            result = client.get_data_from_vector_by_reference_period_range(
                "V1", "2024-01", "2024-12"
            )
        assert result == []

    def test_get_full_table_download_sdmx_returns_bytes(self, isolated_cache_dir):

        client = StatsCanClient("https://api.example.com")
        # The ``requests`` module is imported inside the method, so we
        # patch it at the source.
        with patch("requests.get") as mock_get:
            mock_get.return_value.content = b"<xml>sdmx</xml>"
            mock_get.return_value.raise_for_status = lambda: None
            result = client.get_full_table_download_sdmx("10100139")
        assert result == b"<xml>sdmx</xml>"

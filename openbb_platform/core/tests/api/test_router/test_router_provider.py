"""Tests for provider raw API router with auto strategy and response meta."""

from unittest.mock import patch

import pytest
from openbb_core.api.router.provider import (
    ProviderQueryRequest,
    ProviderQueryResponse,
    provider_query,
)


def test_provider_query_auto_fallback_from_wind_to_tushare():
    """Auto mode should fallback when preferred provider fails."""

    with patch(
        "openbb_core.api.router.provider._query_wind",
        side_effect=Exception("wind down"),
    ), patch(
        "openbb_core.api.router.provider._query_tushare",
        return_value=[{"ok": True}],
    ), patch(
        "openbb_core.api.router.provider._load_user_credentials",
        return_value={"tushare_api_key": "token"},
    ):
        req = ProviderQueryRequest(provider="auto", method="daily", kwargs={"ts_code": "000001.SZ"})
        resp = provider_query(req)

    assert isinstance(resp, ProviderQueryResponse)
    assert resp.provider == "tushare"
    assert resp.data == [{"ok": True}]
    assert resp.meta["route"] == "/provider/query"
    assert resp.meta["provider_requested"] == "auto"
    assert resp.meta["provider_used"] == "tushare"
    assert resp.meta["fallback_trace"][0]["provider"] == "wind"
    assert resp.meta["fallback_trace"][0]["status"] == "failed"
    assert resp.meta["fallback_trace"][1]["provider"] == "tushare"
    assert resp.meta["fallback_trace"][1]["status"] == "success"
    assert resp.meta["selection_reason"]["mode"] == "auto"
    assert 0 <= resp.meta["confidence"] <= 1


def test_provider_query_explicit_provider_no_fallback():
    """Explicit provider should not attempt fallback chain."""

    with patch(
        "openbb_core.api.router.provider._query_wind",
        return_value={"Data": [1, 2], "ErrorCode": 0},
    ):
        req = ProviderQueryRequest(provider="wind", method="wss", args=["000001.SZ", "close"])
        resp = provider_query(req)

    assert resp.provider == "wind"
    assert resp.meta["route"] == "/provider/query"
    assert len(resp.meta["fallback_trace"]) == 1
    assert resp.meta["fallback_trace"][0]["provider"] == "wind"
    assert resp.meta["fallback_trace"][0]["status"] == "success"
    assert resp.meta["selection_reason"]["mode"] == "explicit"


@pytest.mark.parametrize(
    "trace,expected_max",
    [
        ([{"provider": "wind", "status": "success", "attempt": 1}], 1.0),
        (
            [
                {"provider": "wind", "status": "failed", "attempt": 1},
                {"provider": "tushare", "status": "success", "attempt": 2},
            ],
            0.85,
        ),
    ],
)
def test_confidence_reflects_fallback_depth(trace, expected_max):
    """Confidence should decay after failures."""
    from openbb_core.api.router.provider import _compute_confidence

    score = _compute_confidence(trace)
    assert 0 <= score <= 1
    assert score <= expected_max

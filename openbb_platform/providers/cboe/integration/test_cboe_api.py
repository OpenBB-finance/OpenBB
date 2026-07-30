"""Cboe API interface integration tests.

The ``headers`` fixture (from ``conftest.py``) starts the OpenBB REST API in a
background thread, so these tests are self-contained.
"""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE = "http://localhost:8000/api/v1/cboe"


def _get(path, params, headers):
    """Issue a GET against a Cboe route and return the response."""
    params = {p: v for p, v in params.items() if v is not None}
    query_str = get_querystring(params, [])

    return requests.get(f"{BASE}/{path}?{query_str}", headers=headers, timeout=60)


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "region": "us"},
        {"provider": "cboe", "region": "eu"},
        {"provider": "cboe", "region": "au"},
    ],
)
@pytest.mark.integration
def test_cboe_index_snapshots(params, headers):
    """Test the index snapshots endpoint across every region."""
    result = _get("index/snapshots", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "symbol": "VIX"},
        {"provider": "cboe", "symbol": "X2C", "start_date": "2024-01-01"},
        {"provider": "cboe", "symbol": "BUK100P", "interval": "1m"},
    ],
)
@pytest.mark.integration
def test_cboe_index_historical(params, headers):
    """Test the index historical endpoint."""
    result = _get("index/historical", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "symbol": "BUK100P"},
        {"provider": "cboe", "symbol": "X2C", "session": "eod"},
        {"provider": "cboe", "symbol": "X2C", "session": "sod"},
    ],
)
@pytest.mark.integration
def test_cboe_index_constituents(params, headers):
    """Test the index constituents endpoint."""
    result = _get("index/constituents", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "query": "uk"},
        {"provider": "cboe", "query": "BUK", "is_symbol": True},
    ],
)
@pytest.mark.integration
def test_cboe_index_search(params, headers):
    """Test the index search endpoint."""
    result = _get("index/search", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{"provider": "cboe"}])
@pytest.mark.integration
def test_cboe_index_available(params, headers):
    """Test the available indices endpoint."""
    result = _get("index/available", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}, {"symbol": "BXM"}])
@pytest.mark.integration
def test_cboe_index_documents(params, headers):
    """Test the index documents endpoint."""
    result = _get("index/documents", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "symbol": "AAPL"},
        {"provider": "cboe", "symbol": "AAPL,MSFT"},
    ],
)
@pytest.mark.integration
def test_cboe_equity_quote(params, headers):
    """Test the equity quote endpoint."""
    result = _get("equity/quote", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "symbol": "AAPL", "start_date": "2024-01-01"},
        {"provider": "cboe", "symbol": "AAPL", "interval": "1m"},
    ],
)
@pytest.mark.integration
def test_cboe_equity_historical(params, headers):
    """Test the equity historical endpoint."""
    result = _get("equity/historical", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{"provider": "cboe", "query": "ETF"}])
@pytest.mark.integration
def test_cboe_equity_search(params, headers):
    """Test the equity search endpoint."""
    result = _get("equity/search", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{"provider": "cboe", "symbol": "SPY"}])
@pytest.mark.integration
def test_cboe_options_chains(params, headers):
    """Test the options chains endpoint."""
    result = _get("options/chains", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"symbol": "SPY"},
        {"symbol": "SPY", "spread_type": "call"},
    ],
)
@pytest.mark.integration
def test_cboe_options_analysis(params, headers):
    """Test the options strategy endpoints."""
    for path in ("options/straddle", "options/strangle", "options/spreads"):
        result = _get(path, {"symbol": params["symbol"]}, headers)

        assert isinstance(result, requests.Response)
        assert result.status_code == 200


@pytest.mark.parametrize("params", [{"symbol": "SPY"}])
@pytest.mark.integration
def test_cboe_options_charts(params, headers):
    """Test the Plotly options chart endpoints."""
    for path in ("options/smile", "options/stats", "options/term_structure"):
        result = _get(path, params, headers)

        assert isinstance(result, requests.Response)
        assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cboe", "symbol": "VX_EOD"},
        {"provider": "cboe", "symbol": "VX_AM"},
    ],
)
@pytest.mark.integration
def test_cboe_futures_curve(params, headers):
    """Test the futures curve endpoint."""
    result = _get("futures/curve", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}, {"final_settlement": True}])
@pytest.mark.integration
def test_cboe_futures_settlement_prices(params, headers):
    """Test the futures settlement prices endpoint."""
    result = _get("futures/settlement_prices", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200

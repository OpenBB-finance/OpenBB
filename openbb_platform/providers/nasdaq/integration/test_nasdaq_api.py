"""Nasdaq API interface integration tests.

The ``headers`` fixture (from ``conftest.py``) starts the OpenBB REST API in a
background thread, so these tests are self-contained. Every route is exercised
against the live Nasdaq endpoints.
"""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE = "http://localhost:8000/api/v1/nasdaq"


def _get(path, params, headers):
    """Issue a GET against a Nasdaq route and return the response."""
    params = {p: v for p, v in params.items() if v is not None}
    query_str = get_querystring(params, [])

    return requests.get(f"{BASE}/{path}?{query_str}", headers=headers, timeout=180)


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity/search", {"query": "apple", "provider": "nasdaq"}),
        ("equity/quote", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/profile", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/historical", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/screener", {"exchange": "nasdaq", "provider": "nasdaq"}),
        ("equity/filings", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/symbol_choices", {}),
        ("equity/filing_years", {}),
    ],
)
@pytest.mark.integration
def test_nasdaq_equity(path, params, headers):
    """Every equity route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity/fundamental/balance", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/fundamental/income", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/fundamental/cash", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity/fundamental/ratios", {"symbol": "AAPL", "provider": "nasdaq"}),
        (
            "equity/fundamental/dividends",
            {"symbol": "AAPL", "provider": "nasdaq"},
        ),
        (
            "equity/fundamental/historical_eps",
            {"symbol": "AAPL", "provider": "nasdaq"},
        ),
    ],
)
@pytest.mark.integration
def test_nasdaq_fundamentals(path, params, headers):
    """Every fundamentals route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        (
            "equity/ownership/insider_trading",
            {"symbol": "AAPL", "provider": "nasdaq"},
        ),
        (
            "equity/ownership/institutional",
            {"symbol": "AAPL", "holder_type": "increased", "provider": "nasdaq"},
        ),
        (
            "equity/ownership/short_interest",
            {"symbol": "AAPL", "provider": "nasdaq"},
        ),
    ],
)
@pytest.mark.integration
def test_nasdaq_ownership(path, params, headers):
    """Every ownership route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity/calendar/earnings", {"provider": "nasdaq"}),
        ("equity/calendar/dividend", {"provider": "nasdaq"}),
        ("equity/calendar/splits", {"provider": "nasdaq"}),
        ("equity/calendar/ipo", {"status": "priced", "provider": "nasdaq"}),
        ("economy/calendar", {"provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_calendars(path, params, headers):
    """Every calendar route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("etf/search", {"provider": "nasdaq"}),
        ("etf/info", {"symbol": "QQQ", "provider": "nasdaq"}),
        ("etf/holdings", {"symbol": "SPY", "provider": "nasdaq"}),
        ("etf/holdings", {"symbol": "PRGFX", "provider": "nasdaq"}),
        ("etf/equity_exposure", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("etf/historical", {"symbol": "QQQ", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_etf(path, params, headers):
    """Every fund route answers, for both ETFs and mutual funds."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("index/search", {"index_type": "us", "provider": "nasdaq"}),
        ("index/snapshots", {"region": "us", "provider": "nasdaq"}),
        ("index/snapshots", {"region": "nordic", "provider": "nasdaq"}),
        ("index/historical", {"symbol": "COMP", "provider": "nasdaq"}),
        (
            "index/historical",
            {"symbol": "COMP", "interval": "1m", "provider": "nasdaq"},
        ),
    ],
)
@pytest.mark.integration
def test_nasdaq_index(path, params, headers):
    """Every index route answers, at both intervals."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("markets/status", {"provider": "nasdaq"}),
        ("markets/movers", {"provider": "nasdaq"}),
        (
            "markets/movers",
            {"asset_class": "etf", "category": "most_advanced", "provider": "nasdaq"},
        ),
        ("markets/quotes", {"symbol": "AAPL,QQQ,OMXS30", "provider": "nasdaq"}),
        ("markets/upcoming", {}),
    ],
)
@pytest.mark.integration
def test_nasdaq_markets(path, params, headers):
    """Every market-wide route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("nordic/screener", {"provider": "nasdaq"}),
        (
            "nordic/screener",
            {"asset_class": "indexes", "provider": "nasdaq"},
        ),
        (
            "nordic/screener",
            {
                "asset_class": "corporate_bonds",
                "market": "sweden",
                "provider": "nasdaq",
            },
        ),
        ("nordic/info", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic/fundamentals", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic/dividends", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic/historical", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic/historical_trades", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic/movers", {"provider": "nasdaq"}),
        ("nordic/news", {"provider": "nasdaq"}),
        ("nordic/derivatives_volume", {}),
        ("nordic/knocked_out", {"state": "buyback", "provider": "nasdaq"}),
        ("nordic/bond_yields", {"provider": "nasdaq"}),
        ("nordic/index_factors", {"provider": "nasdaq"}),
        ("nordic/mortgage_rates", {"provider": "nasdaq"}),
        ("nordic/trading_hours", {"provider": "nasdaq"}),
        ("nordic/holidays", {"year": 2026, "provider": "nasdaq"}),
        ("nordic/symbol_choices", {}),
    ],
)
@pytest.mark.integration
def test_nasdaq_nordic(path, params, headers):
    """Every Nasdaq Nordic route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("options/chains", {"symbol": "AAPL", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_derivatives(path, params, headers):
    """Every derivatives route answers."""
    result = _get(path, params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.integration
def test_nasdaq_apps_json(headers):
    """The bundled dashboard template is served and resolves."""
    result = requests.get(f"{BASE}/apps.json", headers=headers, timeout=60)

    assert result.status_code == 200
    assert result.json()[0]["name"] == "Nasdaq Market Data"

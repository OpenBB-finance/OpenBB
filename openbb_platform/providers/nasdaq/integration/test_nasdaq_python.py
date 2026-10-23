"""Nasdaq Python interface integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb

    return None


def _call(obb, path, params):
    """Call a dotted command path on the Nasdaq namespace."""
    command = obb.nasdaq

    for part in path.split("."):
        command = getattr(command, part)

    return command(**params)


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity.search", {"query": "apple", "provider": "nasdaq"}),
        ("equity.quote", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.profile", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.historical", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.screener", {"exchange": "nasdaq", "provider": "nasdaq"}),
        ("equity.filings", {"symbol": "AAPL", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_equity(path, params, obb):
    """Every equity command returns results."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity.fundamental.balance", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.fundamental.income", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.fundamental.cash", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("equity.fundamental.ratios", {"symbol": "AAPL", "provider": "nasdaq"}),
        (
            "equity.fundamental.historical_eps",
            {"symbol": "AAPL", "provider": "nasdaq"},
        ),
    ],
)
@pytest.mark.integration
def test_nasdaq_fundamentals(path, params, obb):
    """Every fundamentals command returns results."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("etf.info", {"symbol": "QQQ", "provider": "nasdaq"}),
        ("etf.holdings", {"symbol": "SPY", "provider": "nasdaq"}),
        ("etf.holdings", {"symbol": "PRGFX", "provider": "nasdaq"}),
        ("etf.equity_exposure", {"symbol": "AAPL", "provider": "nasdaq"}),
        ("etf.historical", {"symbol": "QQQ", "provider": "nasdaq"}),
        ("etf.search", {"provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_etf(path, params, obb):
    """Every fund command returns results, for ETFs and mutual funds alike."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("index.search", {"index_type": "us", "provider": "nasdaq"}),
        ("index.snapshots", {"region": "us", "provider": "nasdaq"}),
        ("index.snapshots", {"region": "nordic", "provider": "nasdaq"}),
        ("index.historical", {"symbol": "COMP", "provider": "nasdaq"}),
        (
            "index.historical",
            {"symbol": "COMP", "interval": "1m", "provider": "nasdaq"},
        ),
    ],
)
@pytest.mark.integration
def test_nasdaq_index(path, params, obb):
    """Every index command returns results, at both intervals."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("markets.status", {"provider": "nasdaq"}),
        ("markets.movers", {"provider": "nasdaq"}),
        ("markets.quotes", {"symbol": "AAPL,QQQ,OMXS30", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_markets(path, params, obb):
    """Every market-wide command returns results."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("nordic.screener", {"provider": "nasdaq"}),
        ("nordic.screener", {"asset_class": "indexes", "provider": "nasdaq"}),
        ("nordic.info", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic.fundamentals", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic.dividends", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic.historical", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic.historical_trades", {"symbol": "AAK", "provider": "nasdaq"}),
        ("nordic.movers", {"provider": "nasdaq"}),
        ("nordic.news", {"provider": "nasdaq"}),
        ("nordic.knocked_out", {"state": "buyback", "provider": "nasdaq"}),
        ("nordic.bond_yields", {"provider": "nasdaq"}),
        ("nordic.index_factors", {"provider": "nasdaq"}),
        ("nordic.mortgage_rates", {"provider": "nasdaq"}),
        ("nordic.trading_hours", {"provider": "nasdaq"}),
        ("nordic.holidays", {"year": 2026, "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_nordic(path, params, obb):
    """Every Nasdaq Nordic command returns results."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.integration
def test_nasdaq_options_chains(obb):
    """The options chain returns every expiration with greeks and detail."""
    result = obb.nasdaq.options.chains(symbol="AAPL", provider="nasdaq")

    assert isinstance(result, OBBject)
    assert len(result.results.contract_symbol) > 0
    assert any(delta is not None for delta in result.results.delta)


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("equity.calendar.earnings", {"provider": "nasdaq"}),
        ("equity.calendar.dividend", {"provider": "nasdaq"}),
        ("equity.calendar.ipo", {"status": "priced", "provider": "nasdaq"}),
        ("economy.calendar", {"provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_nasdaq_calendars(path, params, obb):
    """Every calendar command returns results."""
    result = _call(obb, path, params)

    assert isinstance(result, OBBject)
    assert len(result.results) > 0

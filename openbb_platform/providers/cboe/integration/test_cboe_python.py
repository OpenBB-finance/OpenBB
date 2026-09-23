"""Cboe Python interface integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    return None


@pytest.mark.parametrize(
    "params", [{"region": "us"}, {"region": "eu"}, {"region": "au"}]
)
@pytest.mark.integration
def test_cboe_index_snapshots(params, obb):
    """Test the index snapshots endpoint across every region."""
    result = obb.cboe.index.snapshots(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"symbol": "VIX"},
        {"symbol": "X2C", "start_date": "2024-01-01"},
        {"symbol": "BUK100P", "interval": "1m"},
    ],
)
@pytest.mark.integration
def test_cboe_index_historical(params, obb):
    """Test the index historical endpoint."""
    result = obb.cboe.index.historical(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"symbol": "BUK100P"},
        {"symbol": "X2C", "session": "eod"},
        {"symbol": "X2C", "session": "sod"},
    ],
)
@pytest.mark.integration
def test_cboe_index_constituents(params, obb):
    """Test the index constituents endpoint."""
    result = obb.cboe.index.constituents(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params", [{"query": "uk"}, {"query": "BUK", "is_symbol": True}]
)
@pytest.mark.integration
def test_cboe_index_search(params, obb):
    """Test the index search endpoint."""
    result = obb.cboe.index.search(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_cboe_index_available(params, obb):
    """Test the available indices endpoint."""
    result = obb.cboe.index.available(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "AAPL"}, {"symbol": "AAPL,MSFT"}])
@pytest.mark.integration
def test_cboe_equity_quote(params, obb):
    """Test the equity quote endpoint."""
    result = obb.cboe.equity.quote(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"symbol": "AAPL", "start_date": "2024-01-01"},
        {"symbol": "AAPL", "interval": "1m"},
    ],
)
@pytest.mark.integration
def test_cboe_equity_historical(params, obb):
    """Test the equity historical endpoint."""
    result = obb.cboe.equity.historical(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"query": "ETF"}])
@pytest.mark.integration
def test_cboe_equity_search(params, obb):
    """Test the equity search endpoint."""
    result = obb.cboe.equity.search(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "SPY"}])
@pytest.mark.integration
def test_cboe_options_chains(params, obb):
    """Test the options chains endpoint."""
    result = obb.cboe.options.chains(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert result.results.expirations


@pytest.mark.parametrize("params", [{"symbol": "SPY"}])
@pytest.mark.integration
def test_cboe_options_strategies(params, obb):
    """Test the options strategy endpoints."""
    for command in (
        obb.cboe.options.straddle,
        obb.cboe.options.strangle,
        obb.cboe.options.spreads,
    ):
        result = command(**params)

        assert result
        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.parametrize("params", [{"symbol": "VX_EOD"}, {"symbol": "VX_AM"}])
@pytest.mark.integration
def test_cboe_futures_curve(params, obb):
    """Test the futures curve endpoint."""
    result = obb.cboe.futures.curve(provider="cboe", **params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}, {"final_settlement": True}])
@pytest.mark.integration
def test_cboe_futures_settlement_prices(params, obb):
    """Test the futures settlement prices endpoint."""
    result = obb.cboe.futures.settlement_prices(**params)

    assert result
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}, {"symbol": "BXM"}])
@pytest.mark.integration
def test_cboe_index_documents(params, obb):
    """Test the index documents endpoint."""
    result = obb.cboe.index.documents(**params)

    assert result
    assert len(result) > 0

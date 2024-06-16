"""Python interface integration tests for the derivatives extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject

# pylint: disable=too-many-lines,redefined-outer-name
# pylint: disable=import-outside-toplevel,inconsistent-return-statements


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "date": "2023-01-25",
                "option_type": None,
                "moneyness": "all",
                "strike_gt": None,
                "strike_lt": None,
                "volume_gt": None,
                "volume_lt": None,
                "oi_gt": None,
                "oi_lt": None,
                "model": "black_scholes",
                "show_extended_price": False,
                "include_related_symbols": False,
            }
        ),
        ({"provider": "cboe", "symbol": "AAPL", "use_cache": False}),
        ({"provider": "tradier", "symbol": "AAPL"}),
        ({"provider": "yfinance", "symbol": "AAPL"}),
        (
            {
                "provider": "tmx",
                "symbol": "SHOP",
                "date": "2022-12-28",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_derivatives_options_chains(params, obb):
    """Test the options chains endpoint."""
    result = obb.derivatives.options.chains(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "provider": "intrinio",
                "start_date": "2023-11-20",
                "end_date": None,
                "min_value": None,
                "max_value": None,
                "trade_type": None,
                "sentiment": "neutral",
                "limit": 1000,
                "source": "delayed",
            }
        )
    ],
)
@pytest.mark.integration
def test_derivatives_options_unusual(params, obb):
    """Test the unusual options endpoint."""
    result = obb.derivatives.options.unusual(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "interval": "1d",
                "symbol": "CL,BZ",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "expiration": "2025-12",
            }
        ),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_historical(params, obb):
    """Test the futures historical endpoint."""
    result = obb.derivatives.futures.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "VX", "provider": "cboe", "date": None}),
        ({"provider": "yfinance", "symbol": "ES", "date": "2023-08-01"}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_curve(params, obb):
    """Test the futures curve endpoint."""
    result = obb.derivatives.futures.curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "intrinio", "date": None, "only_traded": True}),
    ],
)
@pytest.mark.integration
def test_derivatives_options_snapshots(params, obb):
    """Test the options snapshots endpoint."""
    result = obb.derivatives.options.snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

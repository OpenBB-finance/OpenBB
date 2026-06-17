"""Python interface integration tests for the derivatives extension."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=too-many-lines,redefined-outer-name
# pylint: disable=import-outside-toplevel,inconsistent-return-statements

SYNTHETIC_OPTIONS_CHAIN = [
    {
        "expiration": "2030-01-17",
        "strike": 100,
        "option_type": "call",
        "open_interest": 10,
        "volume": 5,
        "delta": 0.6,
        "gamma": 0.02,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 100,
        "option_type": "put",
        "open_interest": 8,
        "volume": 4,
        "delta": -0.4,
        "gamma": 0.03,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 105,
        "option_type": "call",
        "open_interest": 20,
        "volume": 10,
        "delta": 0.4,
        "gamma": 0.01,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 95,
        "option_type": "put",
        "open_interest": 12,
        "volume": 7,
        "delta": -0.25,
        "gamma": 0.015,
        "underlying_price": 100,
        "contract_size": 100,
    },
]


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
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
                "delay": "delayed",
            }
        ),
        ({"provider": "cboe", "symbol": "AAPL", "use_cache": False}),
        ({"provider": "tradier", "symbol": "AAPL"}),
        ({"provider": "yfinance", "symbol": "AAPL"}),
        ({"provider": "deribit", "symbol": "BTC"}),
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
    result = result.results  # type: ignore
    list_msg = "Unexpected data format, expected List"
    oi_msg = "Unexpected keys in total_oi property, expected ['total', 'expiration', 'strike']"
    assert isinstance(result.expirations, list), list_msg  # type: ignore
    assert isinstance(result.strikes, list), list_msg  # type: ignore
    assert isinstance(result.contract_symbol, list), list_msg  # type: ignore
    assert hasattr(result, "total_oi"), "Missing total_oi property"  # type: ignore
    assert isinstance(result.total_oi, dict), "Unexpected property format, expected dictionary."  # type: ignore
    assert list(result.total_oi) == ["total", "expiration", "strike"], oi_msg  # type: ignore
    assert hasattr(result, "dataframe"), "Missing dataframe attribute"  # type: ignore
    assert result.has_iv, "Expected implied volatility data"  # type: ignore
    assert len(getattr(result, "dataframe", [])) == len(result.contract_symbol)  # type: ignore


@pytest.mark.parametrize(
    "params",
    [
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
    ],
)
@pytest.mark.integration
def test_derivatives_options_unusual(params, obb):
    """Test the unusual options endpoint."""
    result = obb.derivatives.options.unusual(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
        (
            {
                "provider": "deribit",
                "interval": "1d",
                "symbol": "BTC,ETH",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "yfinance", "symbol": "ES", "date": None}),
        ({"provider": "cboe", "symbol": "VX", "date": "2024-06-25"}),
        ({"provider": "deribit", "date": None, "symbol": "BTC", "hours_ago": 12}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_curve(params, obb):
    """Test the futures curve endpoint."""
    result = obb.derivatives.futures.curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "intrinio", "date": None, "only_traded": True}),
    ],
)
@pytest.mark.skip(
    reason="This test is skipped because the download is excessively large."
)
def test_derivatives_options_snapshots(params, obb):
    """Test the options snapshots endpoint."""
    result = obb.derivatives.options.snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "deribit"}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_instruments(params, obb):
    """Test the futures instruments endpoint."""
    result = obb.derivatives.futures.instruments(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "deribit", "symbol": "ETH-PERPETUAL"}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_info(params, obb):
    """Test the futures info endpoint."""
    result = obb.derivatives.futures.info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": [],
                "target": "implied_volatility",
                "underlying_price": None,
                "option_type": "otm",
                "dte_min": None,
                "dte_max": None,
                "moneyness": None,
                "strike_min": None,
                "strike_max": None,
                "oi": False,
                "volume": False,
                "theme": "dark",
                "chart_params": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_derivatives_options_surface(params, obb):
    """Test equity price historical."""
    data = obb.derivatives.options.chains("AAPL", provider="cboe")
    params["data"] = data.results
    result = obb.derivatives.options.surface(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.integration
def test_derivatives_options_exposure(obb):
    """Test options exposure aggregation."""
    result = obb.derivatives.options.exposure(
        data=SYNTHETIC_OPTIONS_CHAIN,
        by="strike",
    )

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) == 3

    strike_100 = next(row for row in result.results if row["strike"] == 100)
    assert strike_100["call_open_interest"] == 10
    assert strike_100["put_open_interest"] == 8
    assert strike_100["total_open_interest"] == 18
    assert strike_100["net_gex"] == -400
    assert strike_100["net_dex"] == 28000

    summary = result.extra["summary"]
    assert summary["total_open_interest"] == 50
    assert summary["total_gex"] == 8200
    assert summary["net_gex"] == -200
    assert summary["put_call_ratio_open_interest"] == 0.6667
    assert summary["gamma_wall"] == 105
    assert summary["put_gamma_wall"] == 100

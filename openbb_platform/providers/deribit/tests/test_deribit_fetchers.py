"""Deribit Fetcher Tests."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_core.provider.utils.helpers import run_async
from openbb_deribit.models.futures_curve import DeribitFuturesCurveFetcher
from openbb_deribit.models.futures_historical import DeribitFuturesHistoricalFetcher
from openbb_deribit.models.futures_info import DeribitFuturesInfoFetcher
from openbb_deribit.models.futures_instruments import DeribitFuturesInstrumentsFetcher
from openbb_deribit.models.options_chains import (
    DeribitOptionsChainsData,
    DeribitOptionsChainsFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

MOCK_OPTIONS_DATA = DeribitOptionsChainsData.model_validate(
    {
        "expiration": ["2024-12-07", "2024-12-07"],
        "strike": [84000.0, 84000.0],
        "option_type": ["call", "put"],
        "underlying_symbol": ["SYN.BTC-7DEC24", "SYN.BTC-7DEC24"],
        "underlying_price": [100671.2825, 100671.2825],
        "contract_symbol": ["BTC-7DEC24-84000-C", "BTC-7DEC24-84000-P"],
        "dte": [1, 1],
        "contract_size": [1, 1],
        "open_interest": [1.0, 124.8],
        "volume": [0.1, 151.9],
        "last_trade_price": [None, 20.13],
        "bid": [10.06, 0.05],
        "bid_size": [0.3, 0.0],
        "ask": [0.06, 10.06],
        "ask_size": [0.0, 0.2],
        "mark": [16666.69, 0.0],
        "high": [None, 442.83],
        "low": [None, 10.06],
        "change_percent": [0, -0.6],
        "implied_volatility": [1.3618999999999999, 1.3618999999999999],
        "delta": [0.99997, -3e-05],
        "gamma": [0.0, 0.0],
        "theta": [-0.24909, -0.0263],
        "vega": [0.00366, 0.00366],
        "rho": [0.91572, -3e-05],
        "underlying_spot_price": [100644.24, 100644.24],
        "settlement_price": [14590.44, 14.35],
        "timestamp": [
            "2024-12-06 17:26:36.234000-0500",
            "2024-12-06 17:26:36.234000-0500",
        ],
        "min_price": [13184.4, 10.06],
        "max_price": [20078.53, 1509.66],
        "interest_rate": [0.0, 0.0],
        "bid_iv": [0.0, 0.0],
        "ask_iv": [0.0, 2.1254],
        "volume_notional": [0.0, 7083.24],
    }
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("expired", None),
        ],
    }


@pytest.mark.record_http
def test_get_options_symbols():
    """Test getting the list of options symbols."""
    # pylint: disable=import-outside-toplevel
    from openbb_deribit.utils.helpers import get_options_symbols

    params = {"symbol": "BTC"}

    result = run_async(get_options_symbols, **params)
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) > 0
    for key, value in result.items():
        assert isinstance(value, list)
        assert key.startswith("2")


@pytest.mark.asyncio
async def test_deribit_options_chains_fetcher(credentials=test_credentials):
    """Test Deribit Options Chains Fetcher."""
    params = {"symbol": "BTC"}
    fetcher = DeribitOptionsChainsFetcher()

    with patch(
        "openbb_deribit.models.options_chains.DeribitOptionsChainsFetcher.fetch_data",
        return_value=MagicMock(MOCK_OPTIONS_DATA),
    ):
        result = await fetcher.fetch_data(params, {})
        assert isinstance(result, DeribitOptionsChainsData)


@pytest.mark.record_http
def test_deribit_futures_curve_fetcher(credentials=test_credentials):
    """Test Deribit Futures Curve Fetcher."""
    params = {"symbol": "BTC"}

    fetcher = DeribitFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_deribit_futures_historical_fetcher(credentials=test_credentials):
    """Test Deribit Futures Historical Fetcher."""
    params = {
        "symbol": "BTC-PERPETUAL",
        "start_date": date(2024, 12, 1),
        "end_date": date(2024, 12, 3),
        "interval": "12h",
    }

    fetcher = DeribitFuturesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_deribit_futures_instruments_fetcher(credentials=test_credentials):
    """Test Deribit Futures Instruments Fetcher."""
    params = {}

    fetcher = DeribitFuturesInstrumentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_deribit_futures_info_fetcher(credentials=test_credentials):
    """Test Deribit Futures Info Fetcher."""
    params = {"symbol": "BTC-PERPETUAL"}

    fetcher = DeribitFuturesInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

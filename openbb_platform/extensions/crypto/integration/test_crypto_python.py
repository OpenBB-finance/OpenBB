"""Test crypto extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@parametrize(
    "params",
    [
        ({"query": "asd"}),
        ({"query": "btc", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_crypto_search(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.crypto.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1min",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "timeseries": 1,
            }
        ),
        (
            {
                "interval": "15min",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-03",
                "timeseries": 1,
            }
        ),
        (
            {
                "multiplier": 1,
                "timespan": "minute",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "provider": "polygon",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "multiplier": 1,
                "timespan": "day",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "provider": "polygon",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1day",
                "exchanges": ["POLONIEX", "GDAX"],
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1hour",
                "exchanges": ["POLONIEX", "GDAX"],
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
    ],
)
@pytest.mark.integration
def test_crypto_price_historical(params, obb):
    result = obb.crypto.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

"""Test forex extension."""
import datetime

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        ({}),
        (
            {
                "symbol": "EURUSD",
                "date": datetime.date(2023, 9, 25),
                "search": "USD",
                "active": True,
                "order": "asc",
                "sort": "ticker",
                "limit": 1000,
                "provider": "polygon",
            }
        ),
        (
            {
                "provider": "fmp",
            }
        ),
        (
            {
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_forex_pairs(params, obb):
    result = obb.forex.pairs(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "EURUSD", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "interval": "1min",
                "provider": "fmp",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "intrinio",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
                "symbol": "EURUSD",
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
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "5m",
                "period": "max",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_forex_load(params, obb):
    result = obb.forex.load(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

"""Test forex extension."""
import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "params",
    [
        ({}),
        (
            {
                "symbol": "AAPL",
                "date": datetime.date(2023, 9, 25),
                "search": "TEST_STRING",
                "active": True,
                "order": "asc",
                "sort": "ticker",
                "limit": 1000,
                "provider": "polygon",
            }
        ),
    ],
)
def test_forex_pairs(params):
    result = obb.forex.pairs(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
def test_forex_load(params):
    result = obb.forex.load(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

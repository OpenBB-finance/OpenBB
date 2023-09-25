"""Test crypto extension."""
import datetime

import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "BTCUSD",
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
            }
        ),
        (
            {
                "interval": "1min",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
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
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
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
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
            }
        ),
        (
            {
                "interval": "5m",
                "period": "max",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
            }
        ),
    ],
)
def test_crypto_load(params):
    result = obb.crypto.load(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

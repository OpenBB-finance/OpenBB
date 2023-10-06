import pytest
import requests
from extensions.tests.utils.helpers import get_auth
from openbb_provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    return {"Authorization": get_auth()}


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "BTCUSD", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
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
                "interval": "1day",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
                "interval": "5m",
                "period": "max",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
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
    ],
)
@pytest.mark.integration
def test_crypto_load(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/load?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

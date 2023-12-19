"""Test currency API endpoints."""
import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@parametrize(
    "params",
    [
        (
            {
                "provider": "polygon",
                "symbol": "USDJPY",
                "date": "2023-10-12",
                "search": "",
                "active": True,
                "order": "asc",
                "sort": "currency_name",
                "limit": 100,
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
def test_currency_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1day",
                "provider": "fmp",
            }
        ),
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
        (
            {
                "interval": "1hour",
                "provider": "tiingo",
                "symbol": "EURUSD",
                "start_date": "2023-05-21",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "tiingo",
                "symbol": "EURUSD",
                "start_date": "2023-05-21",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_price_historical(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"provider": "ecb"})],
)
@pytest.mark.integration
def test_currency_reference_rates(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/reference_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

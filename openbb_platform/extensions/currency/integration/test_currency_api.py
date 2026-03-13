"""Test currency API endpoints."""

import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "query": "eur",
            }
        ),
        (
            {
                "provider": "intrinio",
                "query": "eur",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_search(params, headers):
    """Test the currency search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "EURUSD",
                "interval": "1d",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fmp",
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "fmp",
                "symbol": "EURUSD,USDJPY",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-10",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "tiingo",
                "symbol": "EURUSD",
                "start_date": "2023-05-21",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
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
    """Test the currency historical price endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "ecb"}],
)
@pytest.mark.integration
def test_currency_reference_rates(params, headers):
    """Test the currency reference rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/reference_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "base": "USD,XAU",
                "counter_currencies": "EUR,JPY,GBP",
                "quote_type": "indirect",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_snapshots(params, headers):
    """Test the currency snapshots endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

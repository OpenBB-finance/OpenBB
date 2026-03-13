"""API integration tests for the derivatives extension."""

import base64
import json

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=too-many-lines,redefined-outer-name


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
def test_derivatives_options_chains(params, headers):
    """Test the options chains endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/options/chains?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_derivatives_options_unusual(params, headers):
    """Test the unusual options endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/options/unusual?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_derivatives_futures_historical(params, headers):
    """Test the futures historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "ES",
                "date": None,
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "VX_EOD",
                "date": "2024-06-25",
            }
        ),
        ({"provider": "deribit", "date": None, "symbol": "BTC", "hours_ago": 12}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_curve(params, headers):
    """Test the futures curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "intrinio", "date": None, "only_traded": True}),
    ],
)
@pytest.mark.skip(
    reason="This test is skipped because the download is excessively large."
)
def test_derivatives_options_snapshots(params, headers):
    """Test the options snapshots endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/options/snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "deribit"}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_instruments(params, headers):
    """Test the futures instruments endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/instruments?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "deribit", "symbol": "ETH-PERPETUAL"}),
    ],
)
@pytest.mark.integration
def test_derivatives_futures_info(params, headers):
    """Test the futures info endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_derivatives_options_surface(params, headers):
    """Test the options surface endpoint."""
    params = {p: v for p, v in params.items() if v and p != "data"}
    data_url = "http://0.0.0.0:8000/api/v1/derivatives/options/chains?symbol=AAPL&provider=cboe"
    data_response = requests.get(data_url, headers=headers, timeout=10).json()
    data = data_response["results"]
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/options/surface?{query_str}"
    result = requests.post(
        url, headers=headers, timeout=10, data=json.dumps({"data": data})
    )
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

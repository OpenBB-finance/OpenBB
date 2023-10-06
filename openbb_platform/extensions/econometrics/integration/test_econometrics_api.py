import base64
import json
import random

import pytest
import requests
from openbb_core.env import Env
from openbb_provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


def get_data(menu: str, symbol: str, provider: str, headers):
    """Randomly pick a symbol and a provider and get data from the selected menu."""

    url = f"http://0.0.0.0:8000/api/v1/{menu}/load?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=headers, timeout=10)
    return result.json()["results"]


data = {}


def get_stocks_data():
    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "intrinio", "polygon", "yfinance"])  # noqa: S311

    data["stocks_data"] = get_data(
        "stocks", symbol=symbol, provider=provider, headers=headers
    )
    return data["stocks_data"]


def get_crypto_data():
    if "crypto_data" in data:
        return data["crypto_data"]

    # TODO : add more crypto providers and symbols
    symbol = random.choice(["BTC"])  # noqa: S311
    provider = random.choice(["fmp"])  # noqa: S311

    data["crypto_data"] = get_data(
        menu="crypto", symbol=symbol, provider=provider, headers=headers
    )
    return data["crypto_data"]


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data()}),
        ({"data": get_crypto_data()}),
    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/corr?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, headers):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": params.pop("data"),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/ols_summary?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "volume", "x_columns": ["close"]}),
        ({"data": get_crypto_data(), "y_column": "volume", "x_columns": ["close"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_dwat(params, headers):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": params.pop("data"),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/dwat?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_bgot(params, headers):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": params.pop("data"),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/bgot?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "columns": ["close", "volume"],
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "columns": ["close", "volume"],
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_coint(params, headers):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": params.pop("data"),
            "columns": params.pop("columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/coint?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "y_column": "volume",
                "x_column": "close",
                "lag": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "y_column": "volume",
                "x_column": "close",
                "lag": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_granger(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/granger?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "column": "close", "regression": "c"}),
        ({"data": get_crypto_data(), "column": "volume", "regression": "ctt"}),
    ],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/unitroot?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

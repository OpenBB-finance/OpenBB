import json
import random
from typing import Literal

import pytest
import requests
from extensions.tests.utils.helpers import get_auth
from openbb_provider.utils.helpers import get_querystring

data = {}


def get_headers():
    if "headers" in data:
        return data["headers"]

    data["headers"] = {"Authorization": get_auth()}
    return data["headers"]


def request_data(menu: str, symbol: str, provider: str):
    """Randomly pick a symbol and a provider and get data from the selected menu."""

    url = f"http://0.0.0.0:8000/api/v1/{menu}/load?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=get_headers(), timeout=10)
    return result.json()["results"]


def get_stocks_data():
    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "intrinio", "polygon", "yfinance"])  # noqa: S311

    data["stocks_data"] = request_data("stocks", symbol=symbol, provider=provider)
    return data["stocks_data"]


def get_crypto_data():
    if "crypto_data" in data:
        return data["crypto_data"]

    # TODO : add more crypto providers and symbols
    symbol = random.choice(["BTC"])  # noqa: S311
    provider = random.choice(["fmp"])  # noqa: S311

    data["crypto_data"] = request_data(
        menu="crypto",
        symbol=symbol,
        provider=provider,
    )
    return data["crypto_data"]


def get_data(menu: Literal["stocks", "crypto"]):
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": ""}, "stocks"),
        ({"data": ""}, "crypto"),
    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, data_type):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/corr?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "close", "x_columns": ["date"]},
            "stocks",
        ),
        (
            {"data": "", "y_column": "close", "x_columns": ["date"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, data_type):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": get_data(data_type),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/ols_summary?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "stocks",
        ),
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_dwat(params, data_type):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": get_data(data_type),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/dwat?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_bgot(params, data_type):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": get_data(data_type),
            "x_columns": params.pop("x_columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/bgot?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "columns": ["close", "volume"],
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "columns": ["close", "volume"],
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_coint(params, data_type):
    params = {p: v for p, v in params.items() if v}

    body = json.dumps(
        {
            "data": get_data(data_type),
            "columns": params.pop("columns"),
        }
    )

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/coint?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_column": "close",
                "lag": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "y_column": "volume",
                "x_column": "close",
                "lag": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_granger(params, data_type):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/granger?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [({"data": "", "column": "", "regression": ""}, "stocks")],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, data_type):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/unitroot?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

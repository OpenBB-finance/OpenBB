import json
import random
from typing import List

import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
        timeout=5,
    )


def auth_header():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="session")
def headers():
    h = {}
    auth = auth_header()
    h.update(auth)
    return h


def get_random_data(menu: str, symbols: List[str], providers: List[str]):
    symbol = random.choice(symbols)  # noqa: S311
    provider = random.choice(providers)  # noqa: S311

    url = f"http://0.0.0.0:8000/api/v1/{menu}/load?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=auth_header(), timeout=5)
    return result.json()["results"]


symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "GOOG", "FB", "BABA", "TSM", "V"]
providers = ["fmp", "intrinio", "polygon", "yfinance"]
stocks_data = get_random_data("stocks", symbols=symbols, providers=providers)

# TODO : add more crypto providers and symbols
symbols_crypto = ["BTC"]
providers_crypto = ["fmp"]
crypto_data = get_random_data(
    menu="crypto", symbols=symbols_crypto, providers=providers_crypto
)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": stocks_data}),
        ({"data": crypto_data}),
    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/corr?{query_str}"
    result = requests.post(url, headers=headers, timeout=5, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": stocks_data, "y_column": "close", "x_columns": ["date"]}),
        ({"data": crypto_data, "y_column": "close", "x_columns": ["date"]}),
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
    result = requests.post(url, headers=headers, timeout=5, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": stocks_data, "y_column": "volume", "x_columns": ["close"]}),
        ({"data": crypto_data, "y_column": "volume", "x_columns": ["close"]}),
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
    result = requests.post(url, headers=headers, timeout=5, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": stocks_data,
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            }
        ),
        (
            {
                "data": crypto_data,
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
    result = requests.post(url, headers=headers, timeout=5, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": stocks_data,
                "columns": ["close", "volume"],
            }
        ),
        (
            {
                "data": crypto_data,
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
    result = requests.post(url, headers=headers, timeout=5, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": stocks_data,
                "y_column": "volume",
                "x_columns": "close",
                "lag": "",
            }
        ),
        (
            {
                "data": crypto_data,
                "y_column": "volume",
                "x_columns": "close",
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
    result = requests.post(url, headers=headers, timeout=5, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": stocks_data, "column": "close", "regression": "c"}),
        ({"data": crypto_data, "column": "volume", "regression": "ctt"}),
    ],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/unitroot?{query_str}"
    result = requests.post(url, headers=headers, timeout=5, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

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
    result = requests.get(url, headers=headers(), timeout=10)
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
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_normality(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/normality?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_capm(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/capm?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "threshold_start": "",
                "threshold_end": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "threshold_start": "0.1",
                "threshold_end": "1.6",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_om(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/om?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "window": "5"}),
        ({"data": get_crypto_data(), "target": "high", "window": "10"}),
    ],
)
@pytest.mark.integration
def test_qa_kurtosis(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/kurtosis?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "fuller_reg": "c",
                "kpss_reg": "ct",
            }
        ),
        (
            {
                "data": get_stocks_data(),
                "target": "high",
                "fuller_reg": "ct",
                "kpss_reg": "c",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_unitroot(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/unitroot?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "rfr": "", "window": ""}),
        ({"data": get_crypto_data(), "target": "high", "rfr": "0.5", "window": "250"}),
    ],
)
@pytest.mark.integration
def test_qa_sh(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/sh?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "target_return": "",
                "window": "",
                "adjusted": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "close",
                "target_return": "0.5",
                "window": "275",
                "adjusted": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_so(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/so?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "window": "220"}),
    ],
)
@pytest.mark.integration
def test_qa_skew(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/skew?{query_str}"
    result = requests.post(url, headers=headers, timeout=60, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "window": "10",
                "quantile_pct": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "window": "50",
                "quantile_pct": "0.6",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_quantile(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/quantile?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_summary(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/qa/summary?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

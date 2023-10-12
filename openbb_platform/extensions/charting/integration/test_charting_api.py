import base64
import json

import pytest
import requests
from openbb_core.env import Env
from openbb_provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    return get_headers()


data = {}


def get_headers():
    if "headers" in data:
        return data["headers"]

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    data["headers"] = {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
    return data["headers"]


def get_stocks_data():
    if "stocks_data" in data:
        return data["stocks_data"]

    url = "http://0.0.0.0:8000/api/v1/stocks/load?symbol=AAPL&provider=fmp"
    result = requests.get(url, headers=get_headers(), timeout=10)
    data["stocks_data"] = result.json()["results"]

    return data["stocks_data"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_stocks_load(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/load?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 100, "chart": True})],
)
@pytest.mark.integration
def test_chart_stocks_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"provider": "yfinance", "symbols": "AAPL", "limit": 20, "chart": True})],
)
@pytest.mark.integration
def test_chart_stocks_news(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/news?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_adx(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adx?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "date", "length": "30", "scalar": "110", "chart": True})],
)
@pytest.mark.integration
def test_chart_ta_aroon(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/aroon?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_ema(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ema?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_hma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/hma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_macd(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/macd?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_rsi(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/rsi?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_sma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/sma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_wma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/wma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_chart_ta_zlma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_stocks_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/zlma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]

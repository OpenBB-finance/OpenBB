import base64
import json

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
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_stocks_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/multiples?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_stocks_news(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/news?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_adx(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adx?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_aroon(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/aroon?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_ema(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ema?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_hma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/hma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_macd(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/macd?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_rsi(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/rsi?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_sma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/sma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_wma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/wma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]


@pytest.mark.parametrize(
    "params",
    [({"chart": True})],
)
@pytest.mark.integration
def test_chart_ta_zlma(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/zlma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]

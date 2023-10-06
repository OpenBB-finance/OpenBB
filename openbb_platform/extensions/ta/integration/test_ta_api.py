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
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "15",
                "mamode": "rma",
                "drift": "2",
                "offset": "1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_atr(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/atr?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "close_column": "adj_close",
                "period": "125",
                "start_date": "",
                "end_date": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_fib(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fib?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "offset": ""}),
        ({"data": get_crypto_data(), "index": "date", "offset": "1"}),
    ],
)
@pytest.mark.integration
def test_ta_obv(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/obv?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "signal": ""}),
        ({"data": get_crypto_data(), "index": "date", "length": "15", "signal": "2"}),
    ],
)
@pytest.mark.integration
def test_ta_fisher(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fisher?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "fast": "",
                "slow": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "fast": "5",
                "slow": "15",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_adosc(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adosc?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "std": "",
                "mamode": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "std": "3",
                "mamode": "wma",
                "offset": "1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_bbands(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/bbands?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_zlma(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/zlma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "scalar": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "30",
                "scalar": "110",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_aroon(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/aroon?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_sma(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/sma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "target": "high",
                "show_all": "true",
                "asint": "true",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_demark(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/demark?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "anchor": "", "offset": ""}),
        ({"data": get_crypto_data(), "index": "date", "anchor": "W", "offset": "5"}),
    ],
)
@pytest.mark.integration
def test_ta_vwap(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/vwap?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "fast": "",
                "slow": "",
                "signal": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_macd(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/macd?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_hma(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/hma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "lower_length": "",
                "upper_length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "lower_length": "30",
                "upper_length": "40",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_donchian(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/donchian?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "conversion": "",
                "base": "",
                "lagging": "",
                "offset": "",
                "lookahead": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "conversion": "10",
                "base": "30",
                "lagging": "50",
                "offset": "30",
                "lookahead": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ichimoku(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ichimoku?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "target": "", "period": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "target": "close",
                "period": "95",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_clenow(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/clenow?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "offset": ""}),
        ({"data": get_crypto_data(), "index": "date", "offset": "5"}),
    ],
)
@pytest.mark.integration
def test_ta_ad(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ad?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_adx(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adx?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_wma(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/wma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "scalar": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "16",
                "scalar": "0.02",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_cci(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cci?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_rsi(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/rsi?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "fast_k_period": "12",
                "slow_d_period": "2",
                "slow_k_period": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_stoch(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/stoch?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "22",
                "scalar": "24",
                "mamode": "sma",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_kc(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/kc?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": ""}),
        ({"data": get_crypto_data(), "index": "date", "length": "20"}),
    ],
)
@pytest.mark.integration
def test_ta_cg(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cg?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "lower_q": "0.3",
                "upper_q": "0.7",
                "model": "Parkinson",
                "is_crypto": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_cones(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cones?{query_str}"
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
                "index": "date",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ema(params, headers):
    params = {p: v for p, v in params.items() if v}
    data = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ema?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=data)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

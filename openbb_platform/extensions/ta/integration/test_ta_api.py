import base64
import json
import random
from typing import Literal

import pytest
import requests
from openbb_core.env import Env
from openbb_provider.utils.helpers import get_querystring

data = {}


def get_headers():
    """Get headers."""
    if "headers" in data:
        return data["headers"]

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    data["headers"] = {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
    return data["headers"]


def get_data(menu: Literal["stocks", "crypto"]):
    """Get data either from stocks or crypto."""
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


def request_data(menu: str, symbol: str, provider: str):
    """Randomly pick a symbol and a provider and get data from the selected menu."""
    url = f"http://0.0.0.0:8000/api/v1/{menu}/load?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=get_headers(), timeout=10)
    return result.json()["results"]


def get_stocks_data():
    """Get stocks data."""
    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon", "yfinance"])  # noqa: S311

    data["stocks_data"] = request_data("stocks", symbol=symbol, provider=provider)
    return data["stocks_data"]


def get_crypto_data():
    """Get crypto data."""
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


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "15",
                "mamode": "rma",
                "drift": "2",
                "offset": "1",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_atr(params, data_type):
    """Test ta atr."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/atr?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=15, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "close_column": "close",
                "period": "125",
                "start_date": "",
                "end_date": "",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_fib(params, data_type):
    """Test ta fib."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fib?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "offset": "1"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_obv(params, data_type):
    """Test ta obv."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/obv?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "signal": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "15", "signal": "2"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_fisher(params, data_type):
    """Test ta fisher."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fisher?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "fast": "",
                "slow": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "fast": "5",
                "slow": "15",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_adosc(params, data_type):
    """Test ta adosc."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adosc?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "std": "",
                "mamode": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "std": "3",
                "mamode": "wma",
                "offset": "1",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_bbands(params, data_type):
    """Test ta bbands."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/bbands?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_zlma(params, data_type):
    """Test ta zlma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/zlma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "length": "30",
                "scalar": "110",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_aroon(params, data_type):
    """Test ta aroon."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/aroon?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_sma(params, data_type):
    """Test ta sma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/sma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "target": "high",
                "show_all": "true",
                "asint": "true",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_demark(params, data_type):
    """Test ta demark."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/demark?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "anchor": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "anchor": "W", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_vwap(params, data_type):
    """Test ta vwap."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/vwap?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "fast": "",
                "slow": "",
                "signal": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_macd(params, data_type):
    """Test ta macd."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/macd?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_hma(params, data_type):
    """Test ta hma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/hma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_length": "",
                "upper_length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "lower_length": "30",
                "upper_length": "40",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_donchian(params, data_type):
    """Test ta donchian."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/donchian?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "conversion": "",
                "base": "",
                "lagging": "",
                "offset": "",
                "lookahead": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "conversion": "10",
                "base": "30",
                "lagging": "50",
                "offset": "30",
                "lookahead": "true",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_ichimoku(params, data_type):
    """Test ta ichimoku."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ichimoku?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "date", "target": "close", "period": "10"}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "target": "close",
                "period": "95",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_clenow(params, data_type):
    """Test ta clenow."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/clenow?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=15, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_ad(params, data_type):
    """Test ta ad."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ad?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_adx(params, data_type):
    """Test ta adx."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adx?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_wma(params, data_type):
    """Test ta wma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/wma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "length": "16",
                "scalar": "0.02",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_cci(params, data_type):
    """Test ta cci."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cci?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_rsi(params, data_type):
    """Test ta rsi."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/rsi?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "fast_k_period": "12",
                "slow_d_period": "2",
                "slow_k_period": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_stoch(params, data_type):
    """Test ta stoch."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/stoch?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "22",
                "scalar": "24",
                "mamode": "sma",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_kc(params, data_type):
    """Test ta kc."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/kc?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "20"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_cg(params, data_type):
    """Test ta cg."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cg?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "lower_q": "0.3",
                "upper_q": "0.7",
                "model": "Parkinson",
                "is_crypto": "true",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_cones(params, data_type):
    """Test ta cones."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cones?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "index": "date",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_ema(params, data_type):
    """Test ta ema."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ema?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

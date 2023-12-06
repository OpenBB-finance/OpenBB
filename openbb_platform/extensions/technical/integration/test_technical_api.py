import base64
import json
import random
from typing import Literal

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

data: dict = {}


def get_headers():
    """Get headers."""
    if "headers" in data:
        return data["headers"]

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    data["headers"] = {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
    return data["headers"]


def get_data(menu: Literal["equity", "crypto"]):
    """Get data either from stocks or crypto."""
    funcs = {"equity": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


def request_data(menu: str, symbol: str, provider: str):
    """Randomly pick a symbol and a provider and get data from the selected menu."""
    url = f"http://0.0.0.0:8000/api/v1/{menu}/price/historical?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=get_headers(), timeout=10)
    return result.json()["results"]


def get_stocks_data():
    """Get stocks data."""
    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon", "yfinance"])  # noqa: S311

    data["stocks_data"] = request_data("equity", symbol=symbol, provider=provider)
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


@parametrize(
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
            "equity",
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
def test_technical_atr(params, data_type):
    """Test ta atr."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/atr?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=15, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_fib(params, data_type):
    """Test ta fib."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/fib?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "equity"),
        ({"data": "", "index": "date", "offset": "1"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_obv(params, data_type):
    """Test ta obv."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/obv?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "signal": ""}, "equity"),
        ({"data": "", "index": "date", "length": "15", "signal": "2"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_fisher(params, data_type):
    """Test ta fisher."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/fisher?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_adosc(params, data_type):
    """Test ta adosc."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/adosc?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_bbands(params, data_type):
    """Test ta bbands."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/bbands?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_zlma(params, data_type):
    """Test ta zlma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/zlma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "equity"),
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
def test_technical_aroon(params, data_type):
    """Test ta aroon."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/aroon?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_sma(params, data_type):
    """Test ta sma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/sma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_demark(params, data_type):
    """Test ta demark."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/demark?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "anchor": "", "offset": ""}, "equity"),
        ({"data": "", "index": "date", "anchor": "W", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_vwap(params, data_type):
    """Test ta vwap."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/vwap?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_macd(params, data_type):
    """Test ta macd."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/macd?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_hma(params, data_type):
    """Test ta hma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/hma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_donchian(params, data_type):
    """Test ta donchian."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/donchian?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_ichimoku(params, data_type):
    """Test ta ichimoku."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/ichimoku?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "date", "target": "close", "period": "10"}, "equity"),
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
def test_technical_clenow(params, data_type):
    """Test ta clenow."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/clenow?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=15, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "equity"),
        ({"data": "", "index": "date", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_ad(params, data_type):
    """Test ta ad."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/ad?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_adx(params, data_type):
    """Test ta adx."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/adx?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_wma(params, data_type):
    """Test ta wma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/wma?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "equity"),
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
def test_technical_cci(params, data_type):
    """Test ta cci."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/cci?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_rsi(params, data_type):
    """Test ta rsi."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/rsi?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_stoch(params, data_type):
    """Test ta stoch."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/stoch?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_kc(params, data_type):
    """Test ta kc."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/kc?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": ""}, "equity"),
        ({"data": "", "index": "date", "length": "20"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_cg(params, data_type):
    """Test ta cg."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/cg?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
                "trading_periods": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "index": "date",
                "lower_q": "0.3",
                "upper_q": "0.7",
                "model": "Parkinson",
                "is_crypto": "True",
                "trading_periods": "",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_cones(params, data_type):
    """Test ta cones."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/cones?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
            "equity",
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
def test_technical_ema(params, data_type):
    """Test ta ema."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/ema?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

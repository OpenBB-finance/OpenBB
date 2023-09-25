import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
        timeout=5,
    )


@pytest.fixture(scope="session")
def headers():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
            }
        )
    ],
)
def test_ta_atr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/atr?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
            }
        )
    ],
)
def test_ta_fib(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fib?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "offset": ""})],
)
def test_ta_obv(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/obv?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "length": "", "signal": ""})],
)
def test_ta_fisher(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/fisher?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "fast": "", "slow": "", "offset": ""})],
)
def test_ta_adosc(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adosc?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
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
            }
        )
    ],
)
def test_ta_bbands(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/bbands?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "length": "", "offset": ""})],
)
def test_ta_zlma(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/zlma?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "length": "", "scalar": ""})],
)
def test_ta_aroon(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/aroon?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "length": "", "offset": ""})],
)
def test_ta_sma(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/sma?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
            }
        )
    ],
)
def test_ta_demark(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/demark?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "anchor": "", "offset": ""})],
)
def test_ta_vwap(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/vwap?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "fast": "", "slow": "", "signal": ""})],
)
def test_ta_macd(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/macd?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "length": "", "offset": ""})],
)
def test_ta_hma(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/hma?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "lower_length": "", "upper_length": "", "offset": ""})],
)
def test_ta_donchian(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/donchian?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
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
            }
        )
    ],
)
def test_ta_ichimoku(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ichimoku?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "target": "", "period": ""})],
)
def test_ta_clenow(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/clenow?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "offset": ""})],
)
def test_ta_ad(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ad?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "length": "", "scalar": "", "drift": ""})],
)
def test_ta_adx(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/adx?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "length": "", "offset": ""})],
)
def test_ta_wma(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/wma?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "length": "", "scalar": ""})],
)
def test_ta_cci(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cci?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            }
        )
    ],
)
def test_ta_rsi(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/rsi?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
            }
        )
    ],
)
def test_ta_stoch(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/stoch?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
            }
        )
    ],
)
def test_ta_kc(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/kc?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "index": "", "length": ""})],
)
def test_ta_cg(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cg?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
            }
        )
    ],
)
def test_ta_cones(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/cones?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "target": "", "index": "", "length": "", "offset": ""})],
)
def test_ta_ema(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/ta/ema?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

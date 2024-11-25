"""Integration tests for charting API."""

import base64
import json

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    """Headers fixture."""
    return get_headers()


# pylint:disable=redefined-outer-name

data: dict = {}


def get_headers():
    """Get headers for requests."""
    if "headers" in data:
        return data["headers"]

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    data["headers"] = {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
    return data["headers"]


def get_equity_data():
    """Get equity data."""
    if "stocks_data" in data:
        return data["stocks_data"]

    url = "http://0.0.0.0:8000/api/v1/equity/price/historical?symbol=AAPL&provider=fmp"
    result = requests.get(url, headers=get_headers(), timeout=10)
    data["stocks_data"] = result.json()["results"]

    return data["stocks_data"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "AAPL",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_equity_price_historical(params, headers):
    """Test chart equity price historical.."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "USDGBP",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_currency_price_historical(params, headers):
    """Test chart currency price historical."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/currency/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "QQQ",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_etf_historical(params, headers):
    """Test chart etf historical."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "NDX",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_index_price_historical(params, headers):
    """Test chart index price historical."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/index/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_crypto_price_historical(params, headers):
    """Test chart crypto price historical."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_adx(params, headers):
    """Test chart ta adx."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/adx?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [({"data": "", "index": "date", "length": "30", "scalar": "110", "chart": True})],
)
@pytest.mark.integration
def test_charting_technical_aroon(params, headers):
    """Test chart ta aroon."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/aroon?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_ema(params, headers):
    """Test chart ta ema."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/ema?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_hma(params, headers):
    """Test chart ta hma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/hma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_macd(params, headers):
    """Test chart ta macd."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/macd?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_rsi(params, headers):
    """Test chart ta rsi."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/rsi?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_sma(params, headers):
    """Test chart ta sma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/sma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_wma(params, headers):
    """Test chart ta wma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/wma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
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
def test_charting_technical_zlma(params, headers):
    """Test chart ta zlma."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/zlma?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "model": "yang_zhang",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_technical_cones(params, headers):
    """Test chart ta cones."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_equity_data())

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/technical/cones?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": None,
                "symbol": "DGS10",
                "transform": "pc1",
                "chart": True,
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_economy_fred_series(params, headers):
    """Test chart ta cones."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_series?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "study": "price",
                "benchmark": "SPY",
                "long_period": 252,
                "short_period": 21,
                "window": 21,
                "trading_periods": 252,
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_technical_relative_rotation(params):
    params = {p: v for p, v in params.items() if v}
    data_params = dict(
        symbol="AAPL,MSFT,GOOGL,AMZN,SPY",
        provider="yfinance",
        start_date="2022-01-01",
        end_date="2024-01-01",
    )
    data_query_str = get_querystring(data_params, [])
    data_url = f"http://0.0.0.0:8000/api/v1/equity/price/historical?{data_query_str}"
    data_result = requests.get(data_url, headers=get_headers(), timeout=10).json()[
        "results"
    ]
    body = json.dumps({"data": data_result})
    query_str = get_querystring(params, ["data"])
    url = f"http://0.0.0.0:8000/api/v1/technical/relative_rotation?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": None,
                "symbol": "XRT,XLB,XLI,XLH,XLC,XLY,XLU,XLK",
                "chart": True,
                "provider": "finviz",
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_equity_price_performance(params, headers):
    """Test chart equity price performance."""
    params = {p: v for p, v in params.items() if v}
    body = (
        json.dumps(
            {"extra_params": {"chart_params": {"limit": 4, "orientation": "h"}}}
        ),
    )
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": None,
                "symbol": "XRT,XLB,XLI,XLH,XLC,XLY,XLU,XLK",
                "chart": True,
                "provider": "intrinio",
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_etf_price_performance(params, headers):
    """Test chart equity price performance."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"orientation": "v"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/price_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": None,
                "symbol": "XRT",
                "chart": True,
                "provider": "fmp",
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_etf_holdings(params, headers):
    """Test chart etf holdings."""
    params = {p: v for p, v in params.items() if v}
    body = (
        json.dumps(
            {"extra_params": {"chart_params": {"orientation": "v", "limit": 10}}}
        ),
    )
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "econdb",
                "country": "united_kingdom",
                "date": None,
                "chart": True,
            }
        ),
        (
            {
                "provider": "fred",
                "date": "2023-05-10,2024-05-10",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_fixedincome_government_yield_curve(params, headers):
    """Test chart fixedincome government yield curve."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"title": "test chart"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/government/yield_curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "ES",
                "start_date": "2022-01-01",
                "end_date": "2022-02-01",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_derivatives_futures_historical(params, headers):
    """Test chart derivatives futures historical."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"title": "test chart"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "yfinance",
                "symbol": "ES",
                "date": None,
                "chart": True,
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "VX",
                "date": "2024-06-25",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_derivatives_futures_curve(params, headers):
    """Test chart derivatives futures curve."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"title": "test chart"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/derivatives/futures/curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_equity_historical_market_cap(params, headers):
    """Test chart equity historical market cap."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"title": "test chart"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/historical_market_cap?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "symbol": "APUS49D74714,APUS49D74715,APUS49D74716",
                "start_date": "2014-01-01",
                "end_date": "2024-07-01",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_charting_economy_survey_bls_series(params, headers):
    """Test chart economy survey bls series."""
    params = {p: v for p, v in params.items() if v}
    body = (json.dumps({"extra_params": {"chart_params": {"title": "test chart"}}}),)
    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/bls_series?{query_str}"
    result = requests.get(url, headers=headers, timeout=10, json=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "method": "pearson",
                "chart": True,
            }
        )
    ],
)
@pytest.mark.integration
def test_charting_econometrics_correlation_matrix(params, headers):
    """Test chart econometrics correlation matrix."""
    # pylint:disable=import-outside-toplevel
    from pandas import DataFrame

    url = "http://0.0.0.0:8000/api/v1/equity/price/historical?symbol=AAPL,MSFT,GOOG&provider=yfinance"
    result = requests.get(url, headers=headers, timeout=10)
    df = DataFrame(result.json()["results"])
    df = df.pivot(index="date", columns="symbol", values="close").reset_index()
    body = df.to_dict(orient="records")

    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/correlation_matrix?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=json.dumps(body))

    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    chart = result.json()["chart"]
    fig = chart.pop("fig", {})

    assert chart
    assert not fig
    assert list(chart.keys()) == ["content", "format"]

import base64

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


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
        (
            {
                "symbol": "MISL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_historical(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_info(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_sectors(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/sectors?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "date": "2023-01-01",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "SPY",
                "date": "2023-04-20",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "MISL",
                "date": "2023-04-20",
                "cik": "0001329377",
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_holdings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "SPY,VOO,QQQ,IWM,IWN,GOVT,JNK", "provider": "fmp"})],
)
@pytest.mark.integration
def test_etf_price_performance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/price_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10, "provider": "wsj"})],
)
@pytest.mark.integration
def test_etf_disc_gainers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/gainers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10, "provider": "wsj"})],
)
@pytest.mark.integration
def test_etf_disc_losers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/losers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "IOO"}), ({"symbol": "MISL"})],
)
@pytest.mark.integration
def test_etf_holdings_date(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/etf/holdings_date?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10, "provider": "wsj"})],
)
@pytest.mark.integration
def test_etf_disc_active(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/active?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

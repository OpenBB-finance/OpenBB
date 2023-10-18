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
    [({"index": "dowjones", "provider": "fmp"})],
)
@pytest.mark.integration
def test_economy_const(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/const?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "countries": "spain",
                "units": "growth_same",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            }
        ),
        (
            {
                "countries": ["portugal", "spain"],
                "units": "growth_same",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_cpi(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cpi?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fmp",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "cboe",
                "symbol": "AAVE100",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "cboe",
                "symbol": "AAVE100",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1min",
                "provider": "fmp",
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "timeseries": 1,
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "timeseries": 1,
            }
        ),
        (
            {
                "timespan": "minute",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "multiplier": 1,
                "provider": "polygon",
                "symbol": "NDX",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "timespan": "day",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "multiplier": 1,
                "provider": "polygon",
                "symbol": "NDX",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "prepost": True,
                "rounding": True,
                "provider": "yfinance",
                "symbol": "DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_index(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/index?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "cboe",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "cboe",
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "cboe",
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_european_index(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/european_index?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "BUKBUS", "provider": "cboe"})],
)
@pytest.mark.integration
def test_economy_european_index_constituents(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/european_index_constituents?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"europe": True, "provider": "cboe"}),
        ({"provider": "fmp"}),
        ({"provider": "yfinance"}),
    ],
)
@pytest.mark.integration
def test_economy_available_indices(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/available_indices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "fmp"})],
)
@pytest.mark.integration
def test_economy_risk(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/risk?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "D", "symbol": True, "provider": "cboe"}),
        (
            {
                "europe": True,
                "provider": "cboe",
                "query": "A",
                "symbol": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_index_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/index_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "cboe", "region": "US"})],
)
@pytest.mark.integration
def test_economy_index_snapshots(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/index_snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"query": "grain", "provider": "quandl"})],
)
@pytest.mark.integration
def test_economy_cot_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cot_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "code": "13874P",
                "data_type": "FO",  # cspell: disable-line
                "legacy_format": True,
                "report_type": "ALL",
                "measure": "CR",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": "diff",
                "provider": "quandl",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_cot(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cot?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "series_name": "PE Ratio by Month",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "collapse": "monthly",
                "transform": "diff",
                "provider": "quandl",
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_sp500_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/sp500_multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "$GDP",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
                "provider": "intrinio",
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_fred_index(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_index?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "units": "usd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "oecd",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "usd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpnom(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdpnom?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "units": "yoy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "oecd",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "yoy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpreal(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdpreal?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
                "provider": "oecd",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpforecast(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdpforecast?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "tradingeconomics",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "country": "portugal",
                "group": "gdp",
                "importance": "Low",
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_econcal(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/econcal?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

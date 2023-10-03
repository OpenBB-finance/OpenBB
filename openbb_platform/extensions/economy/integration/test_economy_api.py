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
    [({"index": "dowjones"})],
)
@pytest.mark.integration
def test_economy_const(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/const?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "countries": ["portugal", "spain"],
                "units": "growth_same",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_cpi(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cpi?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "DJI", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
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
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
                "interval": "1m",
                "period": "max",
                "prepost": True,
                "rounding": True,
                "provider": "yfinance",
                "symbol": "DJI",
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
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "BUKBUS", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
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
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "BUKBUS"})],
)
@pytest.mark.integration
def test_economy_european_index_constituents(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/european_index_constituents?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({}), ({"europe": True, "provider": "cboe"})],
)
@pytest.mark.integration
def test_economy_available_indices(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/available_indices?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({})],
)
@pytest.mark.integration
def test_economy_risk(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/risk?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "DJ", "symbol": True}),
        (
            {
                "europe": True,
                "provider": "cboe",
                "query": "DJ",
                "symbol": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_index_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/index_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"region": "US"})],
)
@pytest.mark.integration
def test_economy_index_snapshots(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/index_snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"query": "grain"})],
)
@pytest.mark.integration
def test_economy_cot_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cot_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({}),
        (
            {
                "code": "13874P",
                "data_type": "FO",
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
    result = requests.get(url, headers=headers, timeout=5)
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
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_sp500_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/sp500_multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
            }
        )
    ],
)
@pytest.mark.integration
def test_economy_fred_index(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_index?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

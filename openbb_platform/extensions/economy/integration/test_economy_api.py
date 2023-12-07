import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        (
            {
                "provider": "nasdaq",
                "start_date": "2023-10-24",
                "end_date": "2023-11-03",
                "country": "united_states,japan",
            }
        ),
        (
            {
                "provider": "tradingeconomics",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "country": "mexico,sweden",
                "importance": "Low",
                "group": "gdp",
            }
        ),
        (
            {
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_calendar(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/calendar?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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


@parametrize(
    "params",
    [({"provider": "fmp"})],
)
@pytest.mark.integration
def test_economy_risk_premium(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/risk_premium?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
def test_economy_gdp_forecast(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/forecast?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
def test_economy_gdp_nominal(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/nominal?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
def test_economy_gdp_real(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/real?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "report_type": "summary",
                "frequency": "monthly",
                "country": None,
                "provider": "ecb",
            }
        ),
        (
            {
                "report_type": "direct_investment",
                "frequency": "monthly",
                "country": None,
                "provider": "ecb",
            }
        ),
        (
            {
                "report_type": "main",
                "frequency": "quarterly",
                "country": "united_states",
                "provider": "ecb",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_balance_of_payments(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/balance_of_payments?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "query": None,
                "is_release": False,
                "release_id": 15,
                "offset": 0,
                "limit": 1000,
                "filter_variable": "frequency",
                "filter_value": "Monthly",
                "tag_names": "nsa",
                "exclude_tag_names": None,
                "provider": "fred",
            }
        ),
        (
            {
                "query": "GDP",
                "is_release": True,
                "release_id": None,
                "offset": 0,
                "limit": 1000,
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "provider": "fred",
            }
        ),
        (
            {
                "query": None,
                "is_release": False,
                "release_id": None,
                "offset": None,
                "limit": None,
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "SP500",
                "start_date": None,
                "end_date": None,
                "limit": 10000,
                "frequency": "q",
                "aggregation_method": "eop",
                "transform": "chg",
                "provider": "fred",
            }
        ),
        (
            {
                "symbol": "FEDFUNDS",
                "start_date": None,
                "end_date": None,
                "limit": 10000,
                "all_pages": True,
                "provider": "intrinio",
                "sleep": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_series(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_series?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

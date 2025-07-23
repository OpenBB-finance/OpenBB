"""Test Fama-French API endpoints."""

import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "region": "america",
                "factor": "momentum",
                "frequency": "monthly",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_factors(params, headers):
    """Test the Fama-French factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/famafrench/factors?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "portfolio": "5_industry_portfolios",
                "measure": "equal",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_us_portfolio_returns(params, headers):
    """Test the US portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/famafrench/us_portfolio_returns?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "portfolio": "developed_ex_us_6_portfolios_me_op",
                "measure": "equal",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_regional_portfolio_returns(params, headers):
    """Test the regional portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/famafrench/regional_portfolio_returns?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "country": "japan",
                "measure": "ratios",
                "frequency": None,
                "start_date": None,
                "end_date": None,
                "dividends": True,
                "all_data_items_required": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_country_portfolio_returns(params, headers):
    """Test the country portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/famafrench/country_portfolio_returns?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "index": "asia_pacific",
                "measure": "local",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
                "dividends": True,
                "all_data_items_required": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_international_index_returns(params, headers):
    """Test the international index returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/famafrench/international_index_returns?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "breakpoint_type": "op",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_breakpoints(params, headers):
    """Test Fama-French breakpoints endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/famafrench/breakpoints?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "region": "america",
                "factor": "Momentum",
                "is_portfolio": None,
                "portfolio": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_factor_choices(params, headers):
    """Test Fama-French available factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/famafrench/factor_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

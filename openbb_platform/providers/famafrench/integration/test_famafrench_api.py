"""Fama-French API interface integration tests.

The ``headers`` fixture (from ``conftest.py``) starts the OpenBB REST API in a
background thread, so these tests are self-contained.
"""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {
            "provider": "famafrench",
            "region": "europe",
            "factor": "5_factors",
            "frequency": "monthly",
        },
    ],
)
@pytest.mark.integration
def test_famafrench_factors(params, headers):
    """Test the famafrench factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/famafrench/factors?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {
            "provider": "famafrench",
            "portfolio": "portfolios_formed_on_me",
            "measure": "equal",
            "frequency": "annual",
        },
    ],
)
@pytest.mark.integration
def test_famafrench_us_portfolio_returns(params, headers):
    """Test the famafrench us_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/famafrench/us_portfolio_returns?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {"provider": "famafrench", "measure": "equal", "frequency": "annual"},
    ],
)
@pytest.mark.integration
def test_famafrench_regional_portfolio_returns(params, headers):
    """Test the famafrench regional_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        "http://localhost:8000/api/v1/famafrench/regional_portfolio_returns"
        f"?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {
            "provider": "famafrench",
            "country": "japan",
            "measure": "local",
            "frequency": "annual",
        },
    ],
)
@pytest.mark.integration
def test_famafrench_country_portfolio_returns(params, headers):
    """Test the famafrench country_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://localhost:8000/api/v1/famafrench/country_portfolio_returns?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {"provider": "famafrench", "index": "europe_ex_uk", "frequency": "annual"},
    ],
)
@pytest.mark.integration
def test_famafrench_international_index_returns(params, headers):
    """Test the famafrench international_index_returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        "http://localhost:8000/api/v1/famafrench/international_index_returns"
        f"?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "famafrench"},
        {
            "provider": "famafrench",
            "breakpoint_type": "op",
            "start_date": "1998-01-01",
        },
    ],
)
@pytest.mark.integration
def test_famafrench_breakpoints(params, headers):
    """Test the famafrench breakpoints endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/famafrench/breakpoints?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

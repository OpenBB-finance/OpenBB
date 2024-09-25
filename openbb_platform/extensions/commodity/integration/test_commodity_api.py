"""Test Commodity API endpoints."""

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
                "asset": "gold",
                "start_date": None,
                "end_date": None,
                "collapse": None,
                "transform": None,
                "provider": "nasdaq",
            }
        ),
        (
            {
                "asset": "silver",
                "start_date": "1990-01-01",
                "end_date": "2023-01-01",
                "collapse": "monthly",
                "transform": "diff",
                "provider": "nasdaq",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_lbma_fixing(params, headers):
    """Test the LBMA fixing endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/commodity/lbma_fixing?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "category": "balance_sheet",
                "table": "stocks",
                "start_date": None,
                "end_date": None,
                "provider": "eia",
                "use_cache": True,
            }
        ),
        (
            {
                "category": "weekly_estimates",
                "table": "crude_production",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "provider": "eia",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_petroleum_status_report(params, headers):
    """Test the Petroleum Status Report endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/commodity/petroleum_status_report?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

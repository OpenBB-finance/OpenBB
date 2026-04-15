"""Integration tests for the regulators API."""

# pylint: disable=redefined-outer-name

import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


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
                "query": "grain",
                "report_type": "legacy",
                "futures_only": False,
                "category": None,
                "subcategory": None,
                "code": None,
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_cftc_cot_search(params, headers):
    """Test the CFTC COT search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/cftc/cot_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "code": "045601",
                "report_type": "legacy",
                "start_date": None,
                "end_date": None,
                "limit": 1,
                "futures_only": False,
                "measure": "all",
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_cftc_cot(params, headers):
    """Test the CFTC COT endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/cftc/cot?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({}),
    ],
)
@pytest.mark.integration
def test_cftc_get_cot_choices(params, headers):
    """Test the CFTC get_cot_choices endpoint."""
    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/cftc/get_cot_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

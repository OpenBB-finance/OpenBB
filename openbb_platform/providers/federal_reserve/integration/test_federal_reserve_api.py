"""Test Federal Reserve API."""

# pylint: disable=too-many-lines,redefined-outer-name

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


@pytest.mark.integration
def test_federal_reserve_fomc_documents_download(headers):
    """Test the federal reserve fomc documents download endpoint."""
    params = {
        "url": [
            "https://www.federalreserve.gov/monetarypolicy/files/BeigeBook_20230118.pdf"
        ]
    }

    url = "http://localhost:8000/api/v1/federal_reserve/fomc_documents_download"
    result = requests.post(url, headers=headers, timeout=10, json=params)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "year": 2022,
            "document_type": "minutes",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_choices(headers, params):
    """Test the federal reserve fomc documents choices endpoint."""
    url = (
        "http://localhost:8000/api/v1/federal_reserve/fomc_documents_choices?"
        + get_querystring(params, [])
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

"""Test Government API."""

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


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
            }
        ),
        (
            {
                "provider": "congress_gov",
                "limit": 5,
                "offset": 0,
                "sort_by": "desc",
                "congress": None,
                "bill_type": None,
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bills(params, headers):
    """Test the government congress bills endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/bills?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "bill_url": "119/hr/1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_info(params, headers):
    """Test the government congress bill info endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/bill_info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "bill_url": "https://api.congress.gov/v3/bill/119/s/1947?format=json",
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_text_urls(params, headers):
    """Test the government congress bill text URLs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/bill_text_urls?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "urls": [
                    "https://www.congress.gov/119/bills/hr1/BILLS-119hr1eh.pdf",
                ],
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_text(params, headers):
    """Test the government congress bill text endpoint."""
    params = {p: v for p, v in params.items() if v}
    urls = params.pop("urls", [])

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/bill_text?{query_str}"
    result = requests.post(url, headers=headers, json=f"'{urls}'", timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "congress": 119,
                "limit": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendments(params, headers):
    """Test the government congress amendments endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/amendments?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text_urls(params, headers):
    """Test the government congress amendment text URLs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/amendment_text_urls?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_info(params, headers):
    """Test the government congress amendment info endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/amendment_info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "urls": [
                    "https://www.congress.gov/119/crec/2026/03/21/172/52/CREC-2026-03-21-pt1-PgS1484-6.pdf",
                ],
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text(params, headers):
    """Test the government congress amendment text endpoint."""
    params = {p: v for p, v in params.items() if v}
    urls = params.pop("urls", [])

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/amendment_text?{query_str}"
    result = requests.post(url, headers=headers, json=f"'{urls}'", timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_info(params, headers):
    """Test the government congress committee info endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/committee_info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
                "doc_type": "report",
                "congress": 119,
                "limit": 5,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_documents(params, headers):
    """Test the government congress committee documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/committee_documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "congress": None,
                "committee": None,
                "subcommittees": None,
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_choices(params, headers):
    """Test the government congress committee choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/committee_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
                "subcommittee": None,
                "doc_type": "report",
                "congress": 119,
                "is_workspace": False,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_document_urls(params, headers):
    """Test the government congress committee document URLs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/uscongress/committee_document_urls?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

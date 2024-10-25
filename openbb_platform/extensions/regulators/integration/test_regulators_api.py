"""Integration tests for the regulators API."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
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


@parametrize(
    "params",
    [
        ({"symbol": "TSLA", "provider": "sec", "use_cache": None}),
        ({"symbol": "SQQQ", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_cik_map(params, headers):
    """Test the SEC CIK map endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/cik_map?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "berkshire hathaway", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_institutions_search(params, headers):
    """Test the SEC institutions search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/institutions_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "2022", "provider": "sec", "url": "", "use_cache": None}),
        (
            {
                "query": "",
                "provider": "sec",
                "url": "https://xbrl.fasb.org/us-gaap/2014/entire/",
                "use_cache": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_schema_files(params, headers):
    """Test the SEC schema files endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/schema_files?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "0000909832", "provider": "sec", "use_cache": None}),
        ({"query": "0001067983", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_symbol_map(params, headers):
    """Test the SEC symbol map endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/symbol_map?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_rss_litigation(params, headers):
    """Test the SEC RSS litigation endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/rss_litigation?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"query": "oil", "use_cache": False, "provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_sic_search(params, headers):
    """Test the SEC SIC search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/sec/sic_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "grain", "provider": "cftc"}),
    ],
)
@pytest.mark.integration
def test_regulators_cftc_cot_search(params, headers):
    """Test the CFTC COT search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/cftc/cot_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "id": "045601",
                "report_type": "legacy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "futures_only": False,
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_cftc_cot(params, headers):
    """Test the CFTC COT endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/regulators/cftc/cot?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

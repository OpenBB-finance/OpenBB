"""Integration tests for the SEC API."""

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
        ({"symbol": "TSLA", "provider": "sec", "use_cache": None}),
        ({"symbol": "SQQQ", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_sec_cik_map(params, headers):
    """Test the SEC CIK map endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/cik_map?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "berkshire hathaway", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_sec_institutions_search(params, headers):
    """Test the SEC institutions search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/institutions_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "sec"}),
        (
            {
                "provider": "sec",
                "taxonomy": "us-gaap",
                "year": 2024,
                "component": "soi",
                "category": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_schema_files(params, headers):
    """Test the SEC schema files endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/schema_files?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "0000909832", "provider": "sec", "use_cache": None}),
        ({"query": "0001067983", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_sec_symbol_map(params, headers):
    """Test the SEC symbol map endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/symbol_map?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "sec"}],
)
@pytest.mark.integration
def test_sec_rss_litigation(params, headers):
    """Test the SEC RSS litigation endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/rss_litigation?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"query": "oil", "use_cache": False, "provider": "sec"}],
)
@pytest.mark.integration
def test_sec_sic_search(params, headers):
    """Test the SEC SIC search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/sic_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "url": "https://www.sec.gov/Archives/edgar/data/21344/000155278124000634/",
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_filing_headers(params, headers):
    """Test the SEC Filing headers endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/filing_headers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "url": "https://www.sec.gov/Archives/edgar/data/1990353/000110465925015513/tm256977d7_ex99-1.htm",
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_htm_file(params, headers):
    """Test the SEC HTM File endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/htm_file?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "calendar_year": 2023, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_disclosures(params, headers):
    """Test the SEC disclosures endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/disclosures?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "calendar_year": 2023, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_risk_factors(params, headers):
    """Test the SEC risk factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/risk_factors?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "calendar_year": 2023, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_company_overview(params, headers):
    """Test the SEC company overview endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/company_overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "statement_type": "balance",
                "provider": "sec",
            }
        )
    ],
)
@pytest.mark.integration
def test_sec_financial_statements(params, headers):
    """Test the SEC as-filed financial statements endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/financial_statements?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "calendar_year": 2023, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_segment_revenue(params, headers):
    """Test the SEC segment and geographic revenue endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/segment_revenue?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "calendar_year": 2023, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_legal_proceedings(params, headers):
    """Test the SEC legal proceedings endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/legal_proceedings?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"query": "climate change", "form_type": "8-K", "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_full_text_search(params, headers):
    """Test the SEC full-text search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/full_text_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "XLK", "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_nport_fund_metrics(params, headers):
    """Test the SEC NPORT fund metrics endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/nport_fund_metrics?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_beneficial_ownership(params, headers):
    """Test the SEC beneficial ownership endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/beneficial_ownership?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_management_profiles(params, headers):
    """Test the SEC management profiles endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/management_profiles?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_executive_compensation(params, headers):
    """Test the SEC executive compensation endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/executive_compensation?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"})],
)
@pytest.mark.integration
def test_sec_pay_versus_performance(params, headers):
    """Test the SEC pay versus performance endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/sec/pay_versus_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

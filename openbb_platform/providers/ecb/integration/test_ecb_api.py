"""ECB extension integration tests (REST API).

These assert real data, not just a 200.
"""

import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

_BSI_TABLE = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


def _results(name, params, headers):
    """GET an ECB endpoint, assert a 200, and return its results payload."""
    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/ecb/{name}?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200, (
        f"{name} -> {result.status_code}: {result.text[:200]}"
    )
    body = result.json()
    return body.get("results", body) if isinstance(body, dict) else body


def _assert_rows(name, params, headers):
    """Assert the endpoint returns a non-empty list of rows (actual data)."""
    rows = _results(name, params, headers)
    assert isinstance(rows, list) and len(rows) > 0, f"{name} returned no data"
    return rows


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_dataflows(params, headers):
    """Test ecb list_dataflows endpoint."""
    _assert_rows("list_dataflows", params, headers)


@pytest.mark.parametrize("params", [{}, {"query": "interest rate"}])
@pytest.mark.integration
def test_ecb_search_dataflows(params, headers):
    """Test ecb search_dataflows endpoint (no query lists all)."""
    _assert_rows("search_dataflows", params, headers)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_topics(params, headers):
    """Test ecb list_topics endpoint."""
    _assert_rows("list_topics", params, headers)


@pytest.mark.parametrize("params", [{"topic_id": "07"}])
@pytest.mark.integration
def test_ecb_topic_dataflows(params, headers):
    """Test ecb topic_dataflows endpoint (renderable dataflow rows)."""
    rows = _assert_rows("topic_dataflows", params, headers)
    assert all(isinstance(r, dict) and "value" in r for r in rows)


@pytest.mark.parametrize("params", [{"dataflow": "EXR"}])
@pytest.mark.integration
def test_ecb_get_dataflow_dimensions(params, headers):
    """Test ecb get_dataflow_dimensions endpoint."""
    _assert_rows("get_dataflow_dimensions", params, headers)


@pytest.mark.parametrize("params", [{"dataflow_id": "EXR", "dimension_id": "CURRENCY"}])
@pytest.mark.integration
def test_ecb_dimension_choices(params, headers):
    """Test ecb dimension_choices endpoint."""
    _assert_rows("dimension_choices", params, headers)


@pytest.mark.parametrize("params", [{"dataflow": "EXR"}])
@pytest.mark.integration
def test_ecb_indicator_frequencies(params, headers):
    """Test ecb indicator_frequencies dropdown endpoint."""
    _assert_rows("indicator_frequencies", params, headers)


@pytest.mark.parametrize("params", [{"dataflow": "EXR"}])
@pytest.mark.integration
def test_ecb_indicator_areas(params, headers):
    """Test ecb indicator_areas dropdown endpoint."""
    _assert_rows("indicator_areas", params, headers)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_list_tables(params, headers):
    """Test ecb list_tables endpoint."""
    _assert_rows("list_tables", params, headers)


@pytest.mark.parametrize("params", [{"dataflow_id": "BSI"}])
@pytest.mark.integration
def test_ecb_list_table_choices(params, headers):
    """Test ecb list_table_choices endpoint."""
    _assert_rows("list_table_choices", params, headers)


@pytest.mark.parametrize("params", [{"table_id": _BSI_TABLE}])
@pytest.mark.integration
def test_ecb_presentation_table_frequencies(params, headers):
    """Test ecb presentation_table_frequencies dropdown endpoint."""
    _assert_rows("presentation_table_frequencies", params, headers)


@pytest.mark.parametrize("params", [{"table_id": _BSI_TABLE}])
@pytest.mark.integration
def test_ecb_presentation_table_areas(params, headers):
    """Test ecb presentation_table_areas dropdown endpoint."""
    _assert_rows("presentation_table_areas", params, headers)


@pytest.mark.parametrize(
    "params",
    [{"table_id": _BSI_TABLE, "frequency": "M", "reference_area": "U2", "limit": 4}],
)
@pytest.mark.integration
def test_ecb_presentation_table(params, headers):
    """Test ecb presentation_table — indented title rows with period columns."""
    rows = _assert_rows("presentation_table", params, headers)
    assert all("title" in r for r in rows)
    assert any(v is not None for r in rows for k, v in r.items() if k != "title"), (
        "no cell values resolved"
    )


@pytest.mark.parametrize(
    "params",
    [{"dataflow": "EXR", "frequency": "A", "reference_area": "USD", "limit": 5}],
)
@pytest.mark.integration
def test_ecb_available_indicators(params, headers):
    """Test ecb available_indicators endpoint."""
    rows = _assert_rows("available_indicators", params, headers)
    assert rows[0]["symbol"].startswith("EXR::")


@pytest.mark.parametrize("params", [{"symbol": "EXR::A.USD.EUR.SP00.A"}])
@pytest.mark.integration
def test_ecb_indicators(params, headers):
    """Test ecb indicators endpoint."""
    _assert_rows("indicators", params, headers)


@pytest.mark.parametrize("params", [{"symbol": "EURUSD"}])
@pytest.mark.integration
def test_ecb_exchange_rates(params, headers):
    """Test ecb exchange_rates endpoint."""
    _assert_rows("exchange_rates", params, headers)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_reference_rates(params, headers):
    """Test ecb reference_rates endpoint."""
    assert _results("reference_rates", params, headers)


@pytest.mark.parametrize("params", [{"interest_rate_type": "deposit"}])
@pytest.mark.integration
def test_ecb_key_interest_rates(params, headers):
    """Test ecb key_interest_rates endpoint."""
    _assert_rows("key_interest_rates", params, headers)


@pytest.mark.parametrize(
    "params", [{"start_date": "2024-06-01", "end_date": "2024-06-30"}]
)
@pytest.mark.integration
def test_ecb_euro_short_term_rate(params, headers):
    """Test ecb euro_short_term_rate endpoint."""
    _assert_rows("euro_short_term_rate", params, headers)


@pytest.mark.parametrize("params", [{"symbol": "household_loans_for_house_purchase"}])
@pytest.mark.integration
def test_ecb_mfi_interest_rates(params, headers):
    """Test ecb mfi_interest_rates endpoint."""
    _assert_rows("mfi_interest_rates", params, headers)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_yield_curve(params, headers):
    """Test ecb yield_curve endpoint."""
    _assert_rows("yield_curve", params, headers)


@pytest.mark.parametrize("params", [{"report_type": "main"}])
@pytest.mark.integration
def test_ecb_balance_of_payments(params, headers):
    """Test ecb balance_of_payments endpoint."""
    _assert_rows("balance_of_payments", params, headers)


@pytest.mark.parametrize("params", [{"category": "blog", "limit": 3}])
@pytest.mark.integration
def test_ecb_releases(params, headers):
    """Test ecb releases endpoint — newsfeed rows carry a markdown body."""
    rows = _assert_rows("releases", params, headers)
    assert any(r.get("body") for r in rows), "no article body fetched"


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_ecb_calendar(params, headers):
    """Test ecb calendar endpoint (best-effort scrape)."""
    assert isinstance(_results("calendar", params, headers), list)


@pytest.mark.parametrize("params", [{"currency": "EUR", "limit": 25}])
@pytest.mark.integration
def test_ecb_eligible_assets(params, headers):
    """Test ecb eligible_assets endpoint."""
    _assert_rows("eligible_assets", params, headers)

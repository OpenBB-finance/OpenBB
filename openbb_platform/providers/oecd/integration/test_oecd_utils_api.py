"""Test OECD Utils API endpoints."""

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


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_oecd_utils_list_topic_choices(params, headers):
    """Test oecd_utils_list_topic_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_topic_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
        },
        {
            "topic": "ECO",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_subtopic_choices(params, headers):
    """Test oecd_utils_list_subtopic_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_subtopic_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
        },
        {
            "topic": "ECO",
            "subtopic": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_dataflows(params, headers):
    """Test oecd_utils_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_dataflows?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_oecd_utils_list_dataflow_choices(params, headers):
    """Test oecd_utils_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_dataflow_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "query": None,
        },
        {
            "query": "health",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_topics(params, headers):
    """Test oecd_utils_list_topics endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_topics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_id": "DF_PRICES_ALL",
            "output_format": "json",
        },
        {
            "dataflow_id": "DF_PRICES_ALL",
            "output_format": "markdown",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_get_dataflow_parameters(params, headers):
    """Test oecd_utils_get_dataflow_parameters endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/get_dataflow_parameters?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "query": None,
            "topic": None,
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": "GDP",
            "topic": None,
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": None,
            "topic": "HEA",
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": None,
            "topic": None,
            "subtopic": None,
            "dataflow_id": "DF_PRICES_ALL",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_tables(params, headers):
    """Test oecd_utils_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_tables?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "table_id": "DF_PRICES_ALL",
        },
        {
            "table_id": "DF_T725R_Q",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_get_table_detail(params, headers):
    """Test oecd_utils_get_table_detail endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/get_table_detail?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
        },
        {
            "topic": "ECO",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_table_choices(params, headers):
    """Test oecd_utils_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/list_table_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": None,
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": "true",
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": "USA",
            "frequency": "true",
            "transform": None,
            "dimension_values": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_indicator_choices(params, headers):
    """Test oecd_utils_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/indicator_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
            "table": None,
            "country": None,
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_presentation_table_choices(params, headers):
    """Test oecd_utils_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/presentation_table_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "table": "DF_QNA::T0101",
            "country": "USA",
            "dimension": "unit_measure",
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_presentation_table_dim_choices(params, headers):
    """Test oecd_utils_presentation_table_dim_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/presentation_table_dim_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
            "table": "DF_PRICES_ALL",
            "country": "USA",
            "frequency": "M",
            "unit_measure": None,
            "adjustment": None,
            "transformation": None,
            "dimension_values": None,
            "limit": 2,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_presentation_table(params, headers):
    """Test oecd_utils_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/oecd_utils/presentation_table?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

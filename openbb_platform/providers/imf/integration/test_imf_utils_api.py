"""Test IMF Utils API endpoints."""

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
        {
            "output_format": "json",
        }
    ],
)
@pytest.mark.integration
def test_imf_utils_list_dataflows(params, headers):
    """Test imf_utils_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/list_dataflows?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_id": "CPI",
            "output_format": "json",
        },
    ],
)
@pytest.mark.integration
def test_imf_utils_get_dataflow_dimensions(params, headers):
    """Test imf_utils_get_dataflow_dimensions endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/get_dataflow_dimensions?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_port_id_choices(params, headers):
    """Test imf_utils_list_port_id_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/list_port_id_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_tables(params, headers):
    """Test imf_utils_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/list_tables?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_table_choices(params, headers):
    """Test imf_utils_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/list_table_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_dataflow_choices(params, headers):
    """Test imf_utils_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/list_dataflow_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_group": None,
            "table": None,
            "country": None,
            "frequency": None,
        },
        {
            "dataflow_group": "cpi",
            "table": None,
            "country": None,
            "frequency": None,
        },
        {
            "dataflow_group": "cpi",
            "table": "cpi",
            "country": None,
            "frequency": None,
        },
        {
            "dataflow_group": "cpi",
            "table": "cpi",
            "country": "JPN",
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
def test_imf_utils_presentation_table_choices(params, headers):
    """Test imf_utils_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/presentation_table_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "symbol": "CPI::CPI__T",
            "country": None,
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "CPI::CPI__T",
            "country": "JPN",
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
    ],
)
@pytest.mark.integration
def test_imf_utils_indicator_choices(params, headers):
    """Test imf_utils_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/indicator_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_group": "cpi",
            "table": "cpi",
            "country": "JPN",
            "frequency": "A",
            "dimension_values": None,
            "limit": 1,
            "raw": True,
        }
    ],
)
@pytest.mark.integration
def test_imf_utils_presentation_table(params, headers):
    """Test imf_utils_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/imf_utils/presentation_table?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

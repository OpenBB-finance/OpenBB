"""Test IMF Utils API endpoints."""

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
        {
            "output_format": "json",
        }
    ],
)
@pytest.mark.integration
def test_imf_list_dataflows(params, headers):
    """Test imf_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_dataflows?{query_str}"
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
def test_imf_get_dataflow_dimensions(params, headers):
    """Test imf_get_dataflow_dimensions endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/get_dataflow_dimensions?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_port_id_choices(params, headers):
    """Test imf_portwatch_list_port_id_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/list_port_id_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_tables(params, headers):
    """Test imf_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_tables?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_table_choices(params, headers):
    """Test imf_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_table_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_dataflow_choices(params, headers):
    """Test imf_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_dataflow_choices?{query_str}"
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
def test_imf_presentation_table_choices(params, headers):
    """Test imf_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/presentation_table_choices?{query_str}"
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
def test_imf_indicator_choices(params, headers):
    """Test imf_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/indicator_choices?{query_str}"
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
def test_imf_presentation_table(params, headers):
    """Test imf_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/presentation_table?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_bop_country_choices(params, headers):
    """Test imf_list_bop_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_bop_country_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_cpi_country_choices(params, headers):
    """Test imf_list_cpi_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/list_cpi_country_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_country_choices(params, headers):
    """Test imf_portwatch_list_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/list_country_choices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_tradenow_region_choices(params, headers):
    """Test imf_portwatch_list_tradenow_region_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        "http://localhost:8000/api/v1/imf/portwatch/list_tradenow_region_choices"
        f"?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_container_port_choices(params, headers):
    """Test imf_portwatch_list_container_port_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        "http://localhost:8000/api/v1/imf/portwatch/list_container_port_choices"
        f"?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_disruption_event_choices(params, headers):
    """Test imf_portwatch_list_disruption_event_choices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        "http://localhost:8000/api/v1/imf/portwatch/list_disruption_event_choices"
        f"?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"country_code": "USA", "metric": "portcalls", "provider": "imf"}],
)
@pytest.mark.integration
def test_imf_portwatch_country_activity(params, headers):
    """Test imf_portwatch_country_activity endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/country_activity?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"code": "USA", "metric": "trade_value", "provider": "imf"}],
)
@pytest.mark.integration
def test_imf_portwatch_monthly_trade(params, headers):
    """Test imf_portwatch_monthly_trade endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/monthly_trade?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"metric": "portcalls", "provider": "imf"}],
)
@pytest.mark.integration
def test_imf_portwatch_container_metrics(params, headers):
    """Test imf_portwatch_container_metrics endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/container_metrics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{"provider": "imf"}])
@pytest.mark.integration
def test_imf_portwatch_disruption_events(params, headers):
    """Test imf_portwatch_disruption_events endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/disruption_events?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize("params", [{"provider": "imf"}])
@pytest.mark.integration
def test_imf_portwatch_disruptions_map(params, headers):
    """Test imf_portwatch_disruptions_map endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/disruptions_map?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"event_id": "LATEST", "provider": "imf"}],
)
@pytest.mark.integration
def test_imf_portwatch_disruption_sankey(params, headers):
    """Test imf_portwatch_disruption_sankey endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://localhost:8000/api/v1/imf/portwatch/disruption_sankey?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

"""Test the JODI API endpoints."""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE_URL = "http://localhost:8000/api/v1/jodi"


def run(path: str, params: dict, headers) -> None:
    """Run one endpoint and make the common assertions."""
    params = {p: v for p, v in params.items() if v is not None}
    query_str = get_querystring(params, [])
    result = requests.get(
        f"{BASE_URL}/{path}?{query_str}", headers=headers, timeout=600
    )
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": None,
                "product": None,
                "unit": None,
                "start_date": None,
                "end_date": None,
                "provider": "jodi",
                "use_cache": True,
            }
        ),
        (
            {
                "country": "india",
                "product": "gasoline",
                "unit": "ktons",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_balance(params, headers):
    """Test the oil balance endpoint."""
    run("oil/balance", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "saudi_arabia,iraq,united_states",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_production(params, headers):
    """Test the oil production endpoint."""
    run("oil/production", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,china,india",
                "product": "gasoline",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_demand(params, headers):
    """Test the oil demand endpoint."""
    run("oil/demand", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "japan",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_demand_by_product(params, headers):
    """Test the oil demand by product endpoint."""
    run("oil/demand_by_product", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "china,india,south_korea",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_imports(params, headers):
    """Test the oil imports endpoint."""
    run("oil/imports", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "saudi_arabia,united_arab_emirates",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_exports(params, headers):
    """Test the oil exports endpoint."""
    run("oil/exports", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,japan",
                "product": "crude_oil",
                "unit": "kbbl",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_stocks(params, headers):
    """Test the oil stocks endpoint."""
    run("oil/stocks", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": None,
                "unit": None,
                "start_date": None,
                "end_date": None,
                "provider": "jodi",
                "use_cache": True,
            }
        ),
        (
            {
                "country": "norway",
                "unit": "tj",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_balance(params, headers):
    """Test the gas balance endpoint."""
    run("gas/balance", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,qatar,norway",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_production(params, headers):
    """Test the gas production endpoint."""
    run("gas/production", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "germany,france,italy",
                "measure": "observed",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_demand(params, headers):
    """Test the gas demand endpoint."""
    run("gas/demand", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "japan,china,south_korea",
                "flow": "lng",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_imports(params, headers):
    """Test the gas imports endpoint."""
    run("gas/imports", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,qatar,australia",
                "flow": "lng",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_exports(params, headers):
    """Test the gas exports endpoint."""
    run("gas/exports", params, headers)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "germany,france,netherlands",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_stocks(params, headers):
    """Test the gas stocks endpoint."""
    run("gas/stocks", params, headers)

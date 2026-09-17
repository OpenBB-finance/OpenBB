"""Test the BLS provider router — REST API."""

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
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_average_prices(params, headers):
    """Test the BLS cpi average prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/average_prices?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_by_category(params, headers):
    """Test the BLS cpi by category endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/by_category?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_by_category_line(params, headers):
    """Test the BLS cpi by category line endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/by_category_line?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_by_metro(params, headers):
    """Test the BLS cpi by metro endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/by_metro?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_by_region(params, headers):
    """Test the BLS cpi by region endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/by_region?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "archived",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_documents(params, headers):
    """Test the BLS cpi documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "year": 2024,
                "table": 2,
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_relative_importance(params, headers):
    """Test the BLS cpi relative importance endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/relative_importance?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "year": 2024,
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_seasonal_factors(params, headers):
    """Test the BLS cpi seasonal factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/seasonal_factors?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "table": "c-cpi-u",
            }
        ),
        (
            {
                "provider": "bls",
                "table": "historical-cpi-u-index",
            }
        ),
        (
            {
                "provider": "bls",
                "table": "cpi-u-us",
                "date": "2024-06-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_supplemental_tables(params, headers):
    """Test the BLS cpi supplemental tables endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/supplemental_tables?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t1_expenditure_category(params, headers):
    """Test the BLS cpi t1 expenditure category endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t1_expenditure_category?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t2_detailed_expenditure(params, headers):
    """Test the BLS cpi t2 detailed expenditure endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t2_detailed_expenditure?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t3_special_aggregates(params, headers):
    """Test the BLS cpi t3 special aggregates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t3_special_aggregates?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t4_selected_areas(params, headers):
    """Test the BLS cpi t4 selected areas endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t4_selected_areas?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t5_chained_vs_cpiu(params, headers):
    """Test the BLS cpi t5 chained vs cpiu endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t5_chained_vs_cpiu?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t6_1m_analysis(params, headers):
    """Test the BLS cpi t6 1m analysis endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t6_1m_analysis?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_cpi_t7_12m_analysis(params, headers):
    """Test the BLS cpi t7 12m analysis endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/cpi/t7_12m_analysis?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_average_weekly_hours_production(params, headers):
    """Test the BLS employment situation average weekly hours production endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/average_weekly_hours_production?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_civilian_employment(params, headers):
    """Test the BLS employment situation civilian employment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/civilian_employment?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_civilian_unemployment(params, headers):
    """Test the BLS employment situation civilian unemployment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/civilian_unemployment?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_civilian_unemployment_rate(params, headers):
    """Test the BLS employment situation civilian unemployment rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/civilian_unemployment_rate?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "ci_table": "A",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_confidence_intervals(params, headers):
    """Test the BLS employment situation confidence intervals endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/confidence_intervals?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "archived",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_documents(params, headers):
    """Test the BLS employment situation documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_duration_of_unemployment(params, headers):
    """Test the BLS employment situation duration of unemployment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/duration_of_unemployment?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_and_hourly_earnings_by_industry(
    params, headers
):
    """Test the BLS employment situation employment and hourly earnings by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_and_hourly_earnings_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_and_weekly_earnings_by_industry(
    params, headers
):
    """Test the BLS employment situation employment and weekly earnings by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_and_weekly_earnings_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_by_industry_monthly_changes(
    params, headers
):
    """Test the BLS employment situation employment by industry monthly changes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_by_industry_monthly_changes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_change_by_industry_ci(params, headers):
    """Test the BLS employment situation employment change by industry ci endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_change_by_industry_ci?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_levels_by_industry(params, headers):
    """Test the BLS employment situation employment levels by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_levels_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_employment_population_ratio(params, headers):
    """Test the BLS employment situation employment population ratio endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/employment_population_ratio?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_labor_force_participation_rate(params, headers):
    """Test the BLS employment situation labor force participation rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/labor_force_participation_rate?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_labor_underutilization(params, headers):
    """Test the BLS employment situation labor underutilization endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/labor_underutilization?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_long_term_unemployed_share(params, headers):
    """Test the BLS employment situation long term unemployed share endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/long_term_unemployed_share?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_not_in_labor_force_indicators(params, headers):
    """Test the BLS employment situation not in labor force indicators endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/not_in_labor_force_indicators?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_not_in_labor_force_want_a_job(params, headers):
    """Test the BLS employment situation not in labor force want a job endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/not_in_labor_force_want_a_job?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_reasons_for_unemployment(params, headers):
    """Test the BLS employment situation reasons for unemployment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/reasons_for_unemployment?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_summary_establishment(params, headers):
    """Test the BLS employment situation summary establishment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/summary_establishment?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_summary_household(params, headers):
    """Test the BLS employment situation summary household endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/summary_household?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t1_employment_changes(params, headers):
    """Test the BLS employment situation t1 employment changes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t1_employment_changes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t2_ranked_industries(params, headers):
    """Test the BLS employment situation t2 ranked industries endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t2_ranked_industries?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t3a_employment_changes_sa(params, headers):
    """Test the BLS employment situation t3a employment changes sa endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t3a_employment_changes_sa?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t3b_changes_vs_averages(params, headers):
    """Test the BLS employment situation t3b changes vs averages endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t3b_changes_vs_averages?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t4_over_the_year_changes(params, headers):
    """Test the BLS employment situation t4 over the year changes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t4_over_the_year_changes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t5_hours_earnings(params, headers):
    """Test the BLS employment situation t5 hours earnings endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t5_hours_earnings?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t6_aggregate_hours_payrolls(params, headers):
    """Test the BLS employment situation t6 aggregate hours payrolls endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t6_aggregate_hours_payrolls?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_t7_peak_trough(params, headers):
    """Test the BLS employment situation t7 peak trough endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/t7_peak_trough?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_unemployment_by_education(params, headers):
    """Test the BLS employment situation unemployment by education endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/unemployment_by_education?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_employment_situation_unemployment_by_veteran_status(params, headers):
    """Test the BLS employment situation unemployment by veteran status endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/employment_situation/unemployment_by_veteran_status?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_air_passenger_fares(params, headers):
    """Test the BLS import export air passenger fares endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/import_export/air_passenger_fares?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "archived",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_documents(params, headers):
    """Test the BLS import export documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/import_export/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_exports_by_category(params, headers):
    """Test the BLS import export exports by category endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/import_export/exports_by_category?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_exports_by_grains(params, headers):
    """Test the BLS import export exports by grains endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/import_export/exports_by_grains?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_imports_by_category(params, headers):
    """Test the BLS import export imports by category endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/import_export/imports_by_category?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_imports_by_origin(params, headers):
    """Test the BLS import export imports by origin endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/import_export/imports_by_origin?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_import_export_price_indexes(params, headers):
    """Test the BLS import export price indexes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/import_export/price_indexes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_beveridge_curve(params, headers):
    """Test the BLS jolts beveridge curve endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/beveridge_curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "table_number": 10,
            }
        ),
        (
            {
                "provider": "bls",
                "scope": "state",
                "table_number": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_change_analysis(params, headers):
    """Test the BLS jolts change analysis endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/change_analysis?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "archived",
                "release_code": "jolts",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_documents(params, headers):
    """Test the BLS jolts documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_hires_seps_rates(params, headers):
    """Test the BLS jolts hires seps rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/hires_seps_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_openings_by_industry(params, headers):
    """Test the BLS jolts openings by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/openings_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_openings_hires_seps_by_region(params, headers):
    """Test the BLS jolts openings hires seps by region endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/openings_hires_seps_by_region?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_openings_hires_seps_levels(params, headers):
    """Test the BLS jolts openings hires seps levels endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/openings_hires_seps_levels?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_openings_hires_seps_rates(params, headers):
    """Test the BLS jolts openings hires seps rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/openings_hires_seps_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "seasonally_adjusted": False,
                "industry_code": "23",
            }
        ),
        (
            {
                "provider": "bls",
                "measure": "Quits",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_revisions(params, headers):
    """Test the BLS jolts revisions endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/revisions?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_jolts_unemp_per_opening(params, headers):
    """Test the BLS jolts unemp per opening endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/jolts/unemp_per_opening?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "date": "2026-04-01",
                "table": 9,
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_detailed_report(params, headers):
    """Test the BLS ppi detailed report endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/detailed_report?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "category": "detailed_report",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "detailed_report",
                "year": 2024,
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_documents(params, headers):
    """Test the BLS ppi documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_final_demand_12m(params, headers):
    """Test the BLS ppi final demand 12m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/final_demand_12m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_final_demand_1m(params, headers):
    """Test the BLS ppi final demand 1m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/final_demand_1m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_final_demand_components_12m(params, headers):
    """Test the BLS ppi final demand components 12m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/final_demand_components_12m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_final_demand_components_1m(params, headers):
    """Test the BLS ppi final demand components 1m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/final_demand_components_1m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_processed_12m(params, headers):
    """Test the BLS ppi intermediate processed 12m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_processed_12m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_processed_1m(params, headers):
    """Test the BLS ppi intermediate processed 1m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_processed_1m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_services_12m(params, headers):
    """Test the BLS ppi intermediate services 12m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_services_12m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_services_1m(params, headers):
    """Test the BLS ppi intermediate services 1m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_services_1m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_unprocessed_12m(params, headers):
    """Test the BLS ppi intermediate unprocessed 12m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_unprocessed_12m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_intermediate_unprocessed_1m(params, headers):
    """Test the BLS ppi intermediate unprocessed 1m endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/intermediate_unprocessed_1m?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "category": "final_demand",
            }
        ),
        (
            {
                "provider": "bls",
                "table_id": "ppi-comrlp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_relative_importance(params, headers):
    """Test the BLS ppi relative importance endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/relative_importance?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "category": "fd_id",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "forecast",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_ppi_seasonal_factors(params, headers):
    """Test the BLS ppi seasonal factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/ppi/seasonal_factors?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_by_sector(params, headers):
    """Test the BLS productivity by sector endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/by_sector?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_documents(params, headers):
    """Test the BLS productivity documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_manufacturing_indexes(params, headers):
    """Test the BLS productivity manufacturing indexes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/productivity/manufacturing_indexes?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_manufacturing_labor_costs(params, headers):
    """Test the BLS productivity manufacturing labor costs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/manufacturing_labor_costs?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_manufacturing_productivity(params, headers):
    """Test the BLS productivity manufacturing productivity endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/manufacturing_productivity?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_1yr_change(params, headers):
    """Test the BLS productivity mm 1yr change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_1yr_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_indexes_by_industry(params, headers):
    """Test the BLS productivity mm indexes by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_indexes_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_labor_cost_by_industry(params, headers):
    """Test the BLS productivity mm labor cost by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_labor_cost_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_longterm_change(params, headers):
    """Test the BLS productivity mm longterm change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_longterm_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_productivity_by_period(params, headers):
    """Test the BLS productivity mm productivity by period endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_productivity_by_period?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_mm_productivity_change(params, headers):
    """Test the BLS productivity mm productivity change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/mm_productivity_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_nonfarm_business_indexes(params, headers):
    """Test the BLS productivity nonfarm business indexes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/nonfarm_business_indexes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_nonfarm_business_labor_costs(params, headers):
    """Test the BLS productivity nonfarm business labor costs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/nonfarm_business_labor_costs?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_nonfarm_business_productivity(params, headers):
    """Test the BLS productivity nonfarm business productivity endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/nonfarm_business_productivity?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_nonfinancial_corporations_indexes(params, headers):
    """Test the BLS productivity nonfinancial corporations indexes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/nonfinancial_corporations_indexes?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "sector": "Manufacturing sector",
                "measure": "Unit labor costs",
            }
        ),
        (
            {
                "provider": "bls",
                "dataset": "total-economy-hours-employment",
                "sector": "Total economy",
                "measure": "Hours worked",
                "units": "Billions of hours",
            }
        ),
        (
            {
                "provider": "bls",
                "dataset": "major-sectors-business-cycles",
                "units": "Compound annual growth rate",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tables(params, headers):
    """Test the BLS productivity tables endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tables?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_combined_inputs_output(params, headers):
    """Test the BLS productivity tfp combined inputs output endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_combined_inputs_output?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_contributions(params, headers):
    """Test the BLS productivity tfp contributions endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_contributions?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_fire_trends(params, headers):
    """Test the BLS productivity tfp fire trends endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_fire_trends?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_ict_trends(params, headers):
    """Test the BLS productivity tfp ict trends endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_ict_trends?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_output_and_inputs(params, headers):
    """Test the BLS productivity tfp output and inputs endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_output_and_inputs?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_tfp_percent_change(params, headers):
    """Test the BLS productivity tfp percent change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/tfp_percent_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_1yr_change(params, headers):
    """Test the BLS productivity wr 1yr change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_1yr_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_indexes_by_sector(params, headers):
    """Test the BLS productivity wr indexes by sector endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_indexes_by_sector?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_labor_cost_by_sector(params, headers):
    """Test the BLS productivity wr labor cost by sector endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_labor_cost_by_sector?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_longterm_change(params, headers):
    """Test the BLS productivity wr longterm change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_longterm_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_lp_by_industry(params, headers):
    """Test the BLS productivity wr lp by industry endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_lp_by_industry?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_productivity_by_period(params, headers):
    """Test the BLS productivity wr productivity by period endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_productivity_by_period?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_productivity_wr_productivity_change(params, headers):
    """Test the BLS productivity wr productivity change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/productivity/wr_productivity_change?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
            }
        ),
        (
            {
                "provider": "bls",
                "category": "archived",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        ),
    ],
)
@pytest.mark.integration
def test_bls_real_earnings_documents(params, headers):
    """Test the BLS real earnings documents endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/bls/real_earnings/documents?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

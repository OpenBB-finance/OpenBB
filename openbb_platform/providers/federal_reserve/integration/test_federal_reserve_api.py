"""Federal Reserve extension integration tests (REST API)."""

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


BASE = "http://localhost:8000/api/v1"


@pytest.mark.parametrize(
    "params",
    [
        {
            "url": [
                "https://www.federalreserve.gov/monetarypolicy/files/BeigeBook_20230118.pdf"
            ]
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_download(params, headers):
    """Test the fomc_documents_download endpoint."""
    url = f"{BASE}/federal_reserve/fomc_documents_download"
    result = requests.post(url, headers=headers, timeout=60, json=params)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "url": [
                "https://www.ffiec.gov/npw/StaticData/bhcpRRPT/REPORTS/BHCPR_PEER/Dec2015/PeerGroup_1_December2015.pdf"
            ]
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_bhcpr_report_download(params, headers):
    """Test the bhcpr_report_download endpoint."""
    url = f"{BASE}/federal_reserve/ffiec/bhcpr_report_download"
    result = requests.post(url, headers=headers, timeout=60, json=params)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{}],
)
@pytest.mark.integration
def test_federal_reserve_apps_json(params, headers):
    """Test the /federal_reserve/apps.json endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/apps.json?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "survey", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_business_inflation_expectations(params, headers):
    """Test the /federal_reserve/atlanta/business_inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/business_inflation_expectations?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "index_smoothed", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_business_uncertainty(params, headers):
    """Test the /federal_reserve/atlanta/business_uncertainty endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/business_uncertainty?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "evolution", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_gdpnow(params, headers):
    """Test the /federal_reserve/atlanta/gdpnow endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/gdpnow?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_market_probability(params, headers):
    """Test the /federal_reserve/atlanta/market_probability endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/market_probability?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_publications(params, headers):
    """Test the /federal_reserve/atlanta/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_sticky_cpi(params, headers):
    """Test the /federal_reserve/atlanta/sticky_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/sticky_cpi?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule(params, headers):
    """Test the /federal_reserve/atlanta/taylor_rule endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/taylor_rule?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"quarter": "latest", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule_heatmap(params, headers):
    """Test the /federal_reserve/atlanta/taylor_rule_heatmap endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/taylor_rule_heatmap?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"measure": "natural_rate", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule_measures(params, headers):
    """Test the /federal_reserve/atlanta/taylor_rule_measures endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/taylor_rule_measures?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"cut": "overall", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_wage_growth(params, headers):
    """Test the /federal_reserve/atlanta/wage_growth endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/atlanta/wage_growth?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve", "year": 2024}],
)
@pytest.mark.integration
def test_federal_reserve_bhcpr_report(params, headers):
    """Test the /federal_reserve/ffiec/bhcpr_report endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/bhcpr_report?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "rssd_id": "1039502",
            "section": "Summary Ratios",
            "period": None,
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_bhcpr(params, headers):
    """Test the /federal_reserve/ffiec/bhcpr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/bhcpr?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "year": 2015}],
)
@pytest.mark.integration
def test_federal_reserve_bhcpr_report_choices(params, headers):
    """Test the /federal_reserve/ffiec/bhcpr_report_choices endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/bhcpr_report_choices?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"indicator": "payroll_employment", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_boston_economic_indicators(params, headers):
    """Test the /federal_reserve/boston/economic_indicators endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/boston/economic_indicators?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"series": "neec", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_boston_publications(params, headers):
    """Test the /federal_reserve/boston/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/boston/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "rssd_id": "852218"}],
)
@pytest.mark.integration
def test_federal_reserve_call_report(params, headers):
    """Test the /federal_reserve/ffiec/call_report endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/call_report?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "rssd_id": "451965",
            "section": "Schedule RI - Income Statement",
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_call_report_sectioned(params, headers):
    """Test the /federal_reserve/ffiec/call_report_sectioned endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/call_report_sectioned?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_ag_credit_conditions(params, headers):
    """Test the /federal_reserve/chicago/ag_credit_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/ag_credit_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_brave_butters_kelley(params, headers):
    """Test the /federal_reserve/chicago/brave_butters_kelley endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/brave_butters_kelley?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"date_basis": "publication", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_economic_conditions(params, headers):
    """Test the /federal_reserve/chicago/economic_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/economic_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_farm_loan_rates(params, headers):
    """Test the /federal_reserve/chicago/farm_loan_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/farm_loan_rates?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_farmland_values(params, headers):
    """Test the /federal_reserve/chicago/farmland_values endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/farmland_values?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_financial_conditions(params, headers):
    """Test the /federal_reserve/chicago/financial_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/financial_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "rates", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_labor_market(params, headers):
    """Test the /federal_reserve/chicago/labor_market endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/labor_market?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_midwest_economy(params, headers):
    """Test the /federal_reserve/chicago/midwest_economy endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/midwest_economy?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_national_activity(params, headers):
    """Test the /federal_reserve/chicago/national_activity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/national_activity?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_publications(params, headers):
    """Test the /federal_reserve/chicago/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"figure": "weekly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_retail_trade(params, headers):
    """Test the /federal_reserve/chicago/retail_trade endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/chicago/retail_trade?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "expected_inflation", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_inflation_expectations(params, headers):
    """Test the /federal_reserve/cleveland/inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/inflation_expectations?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"frequency": "month", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_inflation_nowcast(params, headers):
    """Test the /federal_reserve/cleveland/inflation_nowcast endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/inflation_nowcast?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "summary", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_median_cpi(params, headers):
    """Test the /federal_reserve/cleveland/median_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/median_cpi?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_median_cpi_components(params, headers):
    """Test the /federal_reserve/cleveland/median_cpi_components endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/median_cpi_components?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_systemic_risk(params, headers):
    """Test the /federal_reserve/cleveland/systemic_risk endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/systemic_risk?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"series": "regional_policy_report", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_publications(params, headers):
    """Test the /federal_reserve/cleveland/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/cleveland/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "group": "all_banks",
            "table": "1",
            "provider": "federal_reserve",
            "country": "France",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_country_exposure(params, headers):
    """Test the /federal_reserve/ffiec/country_exposure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/country_exposure?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "rssd_id": "451965",
            "peers": "451965,480228,852218",
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_custom_peer_group(params, headers):
    """Test the /federal_reserve/ffiec/custom_peer_group endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/custom_peer_group?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "credit", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_agricultural_survey(params, headers):
    """Test the /federal_reserve/dallas/agricultural_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/agricultural_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_banking_conditions(params, headers):
    """Test the /federal_reserve/dallas/banking_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/banking_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"well_type": "new", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_breakeven_prices(params, headers):
    """Test the /federal_reserve/dallas/breakeven_prices endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/breakeven_prices?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "table": "index",
            "transform": "quarter_over_quarter",
            "firm_group": "all",
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_dallas_energy_survey(params, headers):
    """Test the /federal_reserve/dallas/energy_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/energy_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "battery_cells", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_gigafactory_map(params, headers):
    """Test the /federal_reserve/dallas/gigafactory_map endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/gigafactory_map?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"indicator": "gdp", "weighting": "world_trade", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_global_economic_indicators(params, headers):
    """Test the /federal_reserve/dallas/global_economic_indicators endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/global_economic_indicators?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_global_real_economic_activity(params, headers):
    """Test the /federal_reserve/dallas/global_real_economic_activity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/global_real_economic_activity?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_government_debt(params, headers):
    """Test the /federal_reserve/dallas/government_debt endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/government_debt?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_leading_index(params, headers):
    """Test the /federal_reserve/dallas/leading_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/leading_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_lithium_map(params, headers):
    """Test the /federal_reserve/dallas/lithium_map endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/lithium_map?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_manufacturing(params, headers):
    """Test the /federal_reserve/dallas/manufacturing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/manufacturing?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_publications(params, headers):
    """Test the /federal_reserve/dallas/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_retail(params, headers):
    """Test the /federal_reserve/dallas/retail endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/retail?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_service_sector(params, headers):
    """Test the /federal_reserve/dallas/service_sector endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/service_sector?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_trimmed_mean_pce(params, headers):
    """Test the /federal_reserve/dallas/trimmed_mean_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/trimmed_mean_pce?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_weekly_economic_index(params, headers):
    """Test the /federal_reserve/dallas/weekly_economic_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/dallas/weekly_economic_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"rssd_id": "852218", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_executive_summary(params, headers):
    """Test the /federal_reserve/ffiec/executive_summary endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/executive_summary?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataset": "H.15",
            "provider": "federal_reserve",
            "table": "Treasury Constant Maturities",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_fed_data(params, headers):
    """Test the /federal_reserve/fed_data endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/fed_data?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents(params, headers):
    """Test the /federal_reserve/fomc_documents endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/fomc_documents?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"year": 2022, "document_type": "minutes"}],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_choices(params, headers):
    """Test the /federal_reserve/fomc_documents_choices endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/fomc_documents_choices?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_inflation_expectations(params, headers):
    """Test the /federal_reserve/inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/inflation_expectations?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"kind": "relationships", "provider": "federal_reserve", "rssd_id": "1039502"}],
)
@pytest.mark.integration
def test_federal_reserve_institution_structure(params, headers):
    """Test the /federal_reserve/ffiec/institution_structure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/institution_structure?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"status": "active", "provider": "federal_reserve", "name": "JPMorgan"}],
)
@pytest.mark.integration
def test_federal_reserve_institutions(params, headers):
    """Test the /federal_reserve/ffiec/institutions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/institutions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "table1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_international_portfolio_investment(params, headers):
    """Test the /federal_reserve/international_portfolio_investment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/international_portfolio_investment?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "land_values", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_credit_survey(params, headers):
    """Test the /federal_reserve/kc/ag_credit_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_credit_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "afdr_a1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_databook_archived(params, headers):
    """Test the /federal_reserve/kc/ag_databook_archived endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_databook_archived?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_district_surveys(params, headers):
    """Test the /federal_reserve/kc/ag_district_surveys endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_district_surveys?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "historical", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_finance_databook(params, headers):
    """Test the /federal_reserve/kc/ag_finance_databook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_finance_databook?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "rate_type": "variable",
            "loan_type": "operating",
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_interest_rates(params, headers):
    """Test the /federal_reserve/kc/ag_interest_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_interest_rates?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_terms_of_lending(params, headers):
    """Test the /federal_reserve/kc/ag_terms_of_lending endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/ag_terms_of_lending?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"indicator": "level_of_activity", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_divisional_lmci(params, headers):
    """Test the /federal_reserve/kc/divisional_lmci endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/divisional_lmci?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_financial_stress_index(params, headers):
    """Test the /federal_reserve/kc/financial_stress_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/financial_stress_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_natural_rate(params, headers):
    """Test the /federal_reserve/kc/natural_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/natural_rate?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_policy_rate_uncertainty(params, headers):
    """Test the /federal_reserve/kc/policy_rate_uncertainty endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/policy_rate_uncertainty?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_publications(params, headers):
    """Test the /federal_reserve/kc/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"frequency": "daily", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_risk_index(params, headers):
    """Test the /federal_reserve/kc/risk_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/kc/risk_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "limit": 25}],
)
@pytest.mark.integration
def test_federal_reserve_large_holding_companies(params, headers):
    """Test the /federal_reserve/ffiec/large_holding_companies endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/large_holding_companies?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"dataset": "H.15"}],
)
@pytest.mark.integration
def test_federal_reserve_list_datasets(params, headers):
    """Test the /federal_reserve/list_datasets endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/list_datasets?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_list_of_banks_peer_group(params, headers):
    """Test the /federal_reserve/ffiec/list_of_banks_peer_group endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/list_of_banks_peer_group?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{}],
)
@pytest.mark.integration
def test_federal_reserve_list_releases(params, headers):
    """Test the /federal_reserve/list_releases endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/list_releases?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_business_conditions(params, headers):
    """Test the /federal_reserve/minneapolis/business_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/business_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_job_openings_hiring(params, headers):
    """Test the /federal_reserve/minneapolis/job_openings_hiring endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/job_openings_hiring?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_labor_force_participation(params, headers):
    """Test the /federal_reserve/minneapolis/labor_force_participation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/labor_force_participation?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_quits_rate(params, headers):
    """Test the /federal_reserve/minneapolis/quits_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/quits_rate?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_cpi(params, headers):
    """Test the /federal_reserve/minneapolis/regional_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/regional_cpi?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_employment(params, headers):
    """Test the /federal_reserve/minneapolis/regional_employment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/regional_employment?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_gdp(params, headers):
    """Test the /federal_reserve/minneapolis/regional_gdp endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/regional_gdp?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_unemployment(params, headers):
    """Test the /federal_reserve/minneapolis/regional_unemployment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/regional_unemployment?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_publications(params, headers):
    """Test the /federal_reserve/minneapolis/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_unemployment_claims(params, headers):
    """Test the /federal_reserve/minneapolis/unemployment_claims endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/minneapolis/unemployment_claims?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "total", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_money_market_funds(params, headers):
    """Test the /federal_reserve/money_market_funds endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/money_market_funds?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_money_measures(params, headers):
    """Test the /federal_reserve/money_measures endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/money_measures?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_business_leaders(params, headers):
    """Test the /federal_reserve/ny/business_leaders endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/business_leaders?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "holding_type": "all_treasury",
            "summary": False,
            "wam": False,
            "monthly": False,
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_ny_central_bank_holdings(params, headers):
    """Test the /federal_reserve/ny/central_bank_holdings endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/central_bank_holdings?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"breakdown": "overall", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_credit_access(params, headers):
    """Test the /federal_reserve/ny/consumer_credit_access endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/consumer_credit_access?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"topic": "inflation_expectations", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_expectations(params, headers):
    """Test the /federal_reserve/ny/consumer_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/consumer_expectations?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"topic": "home_price_expectations", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_housing(params, headers):
    """Test the /federal_reserve/ny/consumer_housing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/consumer_housing?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_labor_market(params, headers):
    """Test the /federal_reserve/ny/consumer_labor_market endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/consumer_labor_market?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_core_trend_inflation(params, headers):
    """Test the /federal_reserve/ny/core_trend_inflation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/core_trend_inflation?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_corporate_bond_distress(params, headers):
    """Test the /federal_reserve/ny/corporate_bond_distress endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/corporate_bond_distress?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_effr(params, headers):
    """Test the /federal_reserve/ny/effr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/effr?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"dataset": "seasonally_adjusted_diffusion", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_empire_state_manufacturing(params, headers):
    """Test the /federal_reserve/ny/empire_state_manufacturing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/empire_state_manufacturing?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_empire_state_reports(params, headers):
    """Test the /federal_reserve/ny/empire_state_reports endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/empire_state_reports?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "total_debt_balance", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_household_debt(params, headers):
    """Test the /federal_reserve/ny/household_debt endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/household_debt?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_market_expectations(params, headers):
    """Test the /federal_reserve/ny/market_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/market_expectations?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_overnight_bank_funding(params, headers):
    """Test the /federal_reserve/ny/overnight_bank_funding endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/overnight_bank_funding?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"asset_class": "all", "unit": "value", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_primary_dealer_fails(params, headers):
    """Test the /federal_reserve/ny/primary_dealer_fails endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/primary_dealer_fails?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"category": "treasuries", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_primary_dealer_positioning(params, headers):
    """Test the /federal_reserve/ny/primary_dealer_positioning endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/primary_dealer_positioning?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_publications(params, headers):
    """Test the /federal_reserve/ny/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_sofr(params, headers):
    """Test the /federal_reserve/ny/sofr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/sofr?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_supply_chain_pressure(params, headers):
    """Test the /federal_reserve/ny/supply_chain_pressure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ny/supply_chain_pressure?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_average(params, headers):
    """Test the /federal_reserve/ffiec/peer_group_average endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/peer_group_average?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"rssd_id": "451965", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_bank(params, headers):
    """Test the /federal_reserve/ffiec/peer_group_bank endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/peer_group_bank?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_distribution(params, headers):
    """Test the /federal_reserve/ffiec/peer_group_distribution endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/peer_group_distribution?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_anxious_index(params, headers):
    """Test the /federal_reserve/philadelphia/anxious_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/anxious_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_business_conditions(params, headers):
    """Test the /federal_reserve/philadelphia/business_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/business_conditions?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_gdpplus(params, headers):
    """Test the /federal_reserve/philadelphia/gdpplus endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/gdpplus?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"variable": "RGDPX", "statistic": "mean", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_livingston_survey(params, headers):
    """Test the /federal_reserve/philadelphia/livingston_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/livingston_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_manufacturing_outlook(params, headers):
    """Test the /federal_reserve/philadelphia/manufacturing_outlook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/manufacturing_outlook?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"adjustment": "sa", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_nonmanufacturing_outlook(params, headers):
    """Test the /federal_reserve/philadelphia/nonmanufacturing_outlook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/nonmanufacturing_outlook?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_partisan_conflict(params, headers):
    """Test the /federal_reserve/philadelphia/partisan_conflict endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/partisan_conflict?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_publications(params, headers):
    """Test the /federal_reserve/philadelphia/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"dataset": "indexes", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_state_coincident_index(params, headers):
    """Test the /federal_reserve/philadelphia/state_coincident_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/state_coincident_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "variable": "RGDP",
            "statistic": "median",
            "transform": "level",
            "provider": "federal_reserve",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_survey_professional_forecasters(params, headers):
    """Test the /federal_reserve/philadelphia/survey_professional_forecasters endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/survey_professional_forecasters?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"dataset": "inflation", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_term_structure_inflation(params, headers):
    """Test the /federal_reserve/philadelphia/term_structure_inflation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/philadelphia/term_structure_inflation?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"start_date": "2026-01-01"}],
)
@pytest.mark.integration
def test_federal_reserve_release_calendar(params, headers):
    """Test the /federal_reserve/release_calendar endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/release_calendar?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "optimism", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_cfo_survey(params, headers):
    """Test the /federal_reserve/richmond/cfo_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/cfo_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_manufacturing_survey(params, headers):
    """Test the /federal_reserve/richmond/manufacturing_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/manufacturing_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_non_employment_index(params, headers):
    """Test the /federal_reserve/richmond/non_employment_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/non_employment_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_recession_indicator(params, headers):
    """Test the /federal_reserve/richmond/recession_indicator endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/recession_indicator?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_service_sector_survey(params, headers):
    """Test the /federal_reserve/richmond/service_sector_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/service_sector_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"state": "virginia", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_state_survey(params, headers):
    """Test the /federal_reserve/richmond/state_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/state_survey?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_survey_releases(params, headers):
    """Test the /federal_reserve/richmond/survey_releases endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/richmond/survey_releases?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_cyclical_pce(params, headers):
    """Test the /federal_reserve/sf/cyclical_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/cyclical_pce?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_news_sentiment(params, headers):
    """Test the /federal_reserve/sf/news_sentiment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/news_sentiment?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"frequency": "monthly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_proxy_funds_rate(params, headers):
    """Test the /federal_reserve/sf/proxy_funds_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/proxy_funds_rate?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"publication_type": "economic_letter", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_publications(params, headers):
    """Test the /federal_reserve/sf/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_short_rate_path(params, headers):
    """Test the /federal_reserve/sf/short_rate_path endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/short_rate_path?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_supply_demand_pce(params, headers):
    """Test the /federal_reserve/sf/supply_demand_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/supply_demand_pce?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"maturity": 10, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_term_premium(params, headers):
    """Test the /federal_reserve/sf/term_premium endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/term_premium?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"table": "quarterly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_total_factor_productivity(params, headers):
    """Test the /federal_reserve/sf/total_factor_productivity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/sf/total_factor_productivity?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"state": "SD", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_state_average(params, headers):
    """Test the /federal_reserve/ffiec/state_average endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/state_average?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"transform": False, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_fred_md(params, headers):
    """Test the /federal_reserve/stl/fred_md endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/stl/fred_md?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"transform": False, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_fred_qd(params, headers):
    """Test the /federal_reserve/stl/fred_qd endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/stl/fred_qd?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"index": "financial_stress_index", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_national_index(params, headers):
    """Test the /federal_reserve/stl/national_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/stl/national_index?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_publications(params, headers):
    """Test the /federal_reserve/stl/publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/stl/publications?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_treasury_rates(params, headers):
    """Test the /federal_reserve/treasury_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/treasury_rates?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "rssd_id": "852218"}],
)
@pytest.mark.integration
def test_federal_reserve_ubpr(params, headers):
    """Test the /federal_reserve/ffiec/ubpr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/ffiec/ubpr?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_yield_curve(params, headers):
    """Test the /federal_reserve/yield_curve endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    query = get_querystring(params, [])
    url = f"{BASE}/federal_reserve/yield_curve?{query}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

"""Federal Reserve extension integration tests (Python interface)."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.skip(reason="Raw API route, not in the Python interface.")
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
def test_federal_reserve_fomc_documents_download(params, obb):
    """Test the fomc_documents_download endpoint."""
    result = obb.federal_reserve.fomc_documents_download(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.skip(reason="Raw API route, not in the Python interface.")
@pytest.mark.parametrize(
    "params",
    [{"year": 2022, "document_type": "minutes"}],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_choices(params, obb):
    """Test the fomc_documents_choices endpoint."""
    result = obb.federal_reserve.fomc_documents_choices(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [{"table": "survey", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_business_inflation_expectations(params, obb):
    """Test the federal_reserve.atlanta.business_inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.business_inflation_expectations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "index_smoothed", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_business_uncertainty(params, obb):
    """Test the federal_reserve.atlanta.business_uncertainty endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.business_uncertainty(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "evolution", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_gdpnow(params, obb):
    """Test the federal_reserve.atlanta.gdpnow endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.gdpnow(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_market_probability(params, obb):
    """Test the federal_reserve.atlanta.market_probability endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.market_probability(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_publications(params, obb):
    """Test the federal_reserve.atlanta.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_sticky_cpi(params, obb):
    """Test the federal_reserve.atlanta.sticky_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.sticky_cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule(params, obb):
    """Test the federal_reserve.atlanta.taylor_rule endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.taylor_rule(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"quarter": "latest", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule_heatmap(params, obb):
    """Test the federal_reserve.atlanta.taylor_rule_heatmap endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.taylor_rule_heatmap(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"measure": "natural_rate", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_taylor_rule_measures(params, obb):
    """Test the federal_reserve.atlanta.taylor_rule_measures endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.taylor_rule_measures(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"cut": "overall", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_atlanta_wage_growth(params, obb):
    """Test the federal_reserve.atlanta.wage_growth endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.atlanta.wage_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve", "year": 2024}],
)
@pytest.mark.integration
def test_federal_reserve_bhcpr_report(params, obb):
    """Test the federal_reserve.ffiec.bhcpr_report endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.bhcpr_report(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_bhcpr(params, obb):
    """Test the federal_reserve.ffiec.bhcpr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.bhcpr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"indicator": "payroll_employment", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_boston_economic_indicators(params, obb):
    """Test the federal_reserve.boston.economic_indicators endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.boston.economic_indicators(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"series": "neec", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_boston_publications(params, obb):
    """Test the federal_reserve.boston.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.boston.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "rssd_id": "852218"}],
)
@pytest.mark.integration
def test_federal_reserve_call_report(params, obb):
    """Test the federal_reserve.ffiec.call_report endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.call_report(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_call_report_sectioned(params, obb):
    """Test the federal_reserve.ffiec.call_report_sectioned endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.call_report_sectioned(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_ag_credit_conditions(params, obb):
    """Test the federal_reserve.chicago.ag_credit_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.ag_credit_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_brave_butters_kelley(params, obb):
    """Test the federal_reserve.chicago.brave_butters_kelley endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.brave_butters_kelley(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"date_basis": "publication", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_economic_conditions(params, obb):
    """Test the federal_reserve.chicago.economic_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.economic_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_farm_loan_rates(params, obb):
    """Test the federal_reserve.chicago.farm_loan_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.farm_loan_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_farmland_values(params, obb):
    """Test the federal_reserve.chicago.farmland_values endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.farmland_values(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_financial_conditions(params, obb):
    """Test the federal_reserve.chicago.financial_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.financial_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "rates", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_labor_market(params, obb):
    """Test the federal_reserve.chicago.labor_market endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.labor_market(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_midwest_economy(params, obb):
    """Test the federal_reserve.chicago.midwest_economy endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.midwest_economy(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_national_activity(params, obb):
    """Test the federal_reserve.chicago.national_activity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.national_activity(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_publications(params, obb):
    """Test the federal_reserve.chicago.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"figure": "weekly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_chicago_retail_trade(params, obb):
    """Test the federal_reserve.chicago.retail_trade endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.chicago.retail_trade(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "expected_inflation", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_inflation_expectations(params, obb):
    """Test the federal_reserve.cleveland.inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.inflation_expectations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"frequency": "month", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_inflation_nowcast(params, obb):
    """Test the federal_reserve.cleveland.inflation_nowcast endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.inflation_nowcast(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "summary", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_median_cpi(params, obb):
    """Test the federal_reserve.cleveland.median_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.median_cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_median_cpi_components(params, obb):
    """Test the federal_reserve.cleveland.median_cpi_components endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.median_cpi_components(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_systemic_risk(params, obb):
    """Test the federal_reserve.cleveland.systemic_risk endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.systemic_risk(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"series": "regional_policy_report", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_cleveland_publications(params, obb):
    """Test the federal_reserve.cleveland.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.cleveland.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_country_exposure(params, obb):
    """Test the federal_reserve.ffiec.country_exposure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.country_exposure(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_custom_peer_group(params, obb):
    """Test the federal_reserve.ffiec.custom_peer_group endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.custom_peer_group(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "credit", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_agricultural_survey(params, obb):
    """Test the federal_reserve.dallas.agricultural_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.agricultural_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_banking_conditions(params, obb):
    """Test the federal_reserve.dallas.banking_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.banking_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"well_type": "new", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_breakeven_prices(params, obb):
    """Test the federal_reserve.dallas.breakeven_prices endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.breakeven_prices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_dallas_energy_survey(params, obb):
    """Test the federal_reserve.dallas.energy_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.energy_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "battery_cells", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_gigafactory_map(params, obb):
    """Test the federal_reserve.dallas.gigafactory_map endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.gigafactory_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"indicator": "gdp", "weighting": "world_trade", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_global_economic_indicators(params, obb):
    """Test the federal_reserve.dallas.global_economic_indicators endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.global_economic_indicators(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_global_real_economic_activity(params, obb):
    """Test the federal_reserve.dallas.global_real_economic_activity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.global_real_economic_activity(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_government_debt(params, obb):
    """Test the federal_reserve.dallas.government_debt endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.government_debt(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_leading_index(params, obb):
    """Test the federal_reserve.dallas.leading_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.leading_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_lithium_map(params, obb):
    """Test the federal_reserve.dallas.lithium_map endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.lithium_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_manufacturing(params, obb):
    """Test the federal_reserve.dallas.manufacturing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.manufacturing(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_publications(params, obb):
    """Test the federal_reserve.dallas.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_retail(params, obb):
    """Test the federal_reserve.dallas.retail endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.retail(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_service_sector(params, obb):
    """Test the federal_reserve.dallas.service_sector endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.service_sector(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_trimmed_mean_pce(params, obb):
    """Test the federal_reserve.dallas.trimmed_mean_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.trimmed_mean_pce(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_dallas_weekly_economic_index(params, obb):
    """Test the federal_reserve.dallas.weekly_economic_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.dallas.weekly_economic_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"rssd_id": "852218", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_executive_summary(params, obb):
    """Test the federal_reserve.ffiec.executive_summary endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.executive_summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_fed_data(params, obb):
    """Test the federal_reserve.fed_data endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.fed_data(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents(params, obb):
    """Test the federal_reserve.fomc_documents endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.fomc_documents(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_inflation_expectations(params, obb):
    """Test the federal_reserve.inflation_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.inflation_expectations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"kind": "relationships", "provider": "federal_reserve", "rssd_id": "1039502"}],
)
@pytest.mark.integration
def test_federal_reserve_institution_structure(params, obb):
    """Test the federal_reserve.ffiec.institution_structure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.institution_structure(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"status": "active", "provider": "federal_reserve", "name": "JPMorgan"}],
)
@pytest.mark.integration
def test_federal_reserve_institutions(params, obb):
    """Test the federal_reserve.ffiec.institutions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.institutions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "table1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_international_portfolio_investment(params, obb):
    """Test the federal_reserve.international_portfolio_investment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.international_portfolio_investment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "land_values", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_credit_survey(params, obb):
    """Test the federal_reserve.kc.ag_credit_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_credit_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "afdr_a1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_databook_archived(params, obb):
    """Test the federal_reserve.kc.ag_databook_archived endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_databook_archived(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_district_surveys(params, obb):
    """Test the federal_reserve.kc.ag_district_surveys endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_district_surveys(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "historical", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_finance_databook(params, obb):
    """Test the federal_reserve.kc.ag_finance_databook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_finance_databook(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_kc_ag_interest_rates(params, obb):
    """Test the federal_reserve.kc.ag_interest_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_interest_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_ag_terms_of_lending(params, obb):
    """Test the federal_reserve.kc.ag_terms_of_lending endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.ag_terms_of_lending(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"indicator": "level_of_activity", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_divisional_lmci(params, obb):
    """Test the federal_reserve.kc.divisional_lmci endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.divisional_lmci(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_financial_stress_index(params, obb):
    """Test the federal_reserve.kc.financial_stress_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.financial_stress_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_natural_rate(params, obb):
    """Test the federal_reserve.kc.natural_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.natural_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_policy_rate_uncertainty(params, obb):
    """Test the federal_reserve.kc.policy_rate_uncertainty endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.policy_rate_uncertainty(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_publications(params, obb):
    """Test the federal_reserve.kc.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"frequency": "daily", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_kc_risk_index(params, obb):
    """Test the federal_reserve.kc.risk_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.kc.risk_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "limit": 25}],
)
@pytest.mark.integration
def test_federal_reserve_large_holding_companies(params, obb):
    """Test the federal_reserve.ffiec.large_holding_companies endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.large_holding_companies(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"dataset": "H.15"}],
)
@pytest.mark.integration
def test_federal_reserve_list_datasets(params, obb):
    """Test the federal_reserve.list_datasets endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.list_datasets(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_list_of_banks_peer_group(params, obb):
    """Test the federal_reserve.ffiec.list_of_banks_peer_group endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.list_of_banks_peer_group(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{}],
)
@pytest.mark.integration
def test_federal_reserve_list_releases(params, obb):
    """Test the federal_reserve.list_releases endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.list_releases(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_business_conditions(params, obb):
    """Test the federal_reserve.minneapolis.business_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.business_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_job_openings_hiring(params, obb):
    """Test the federal_reserve.minneapolis.job_openings_hiring endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.job_openings_hiring(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_labor_force_participation(params, obb):
    """Test the federal_reserve.minneapolis.labor_force_participation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.labor_force_participation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_quits_rate(params, obb):
    """Test the federal_reserve.minneapolis.quits_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.quits_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_cpi(params, obb):
    """Test the federal_reserve.minneapolis.regional_cpi endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.regional_cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_employment(params, obb):
    """Test the federal_reserve.minneapolis.regional_employment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.regional_employment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_gdp(params, obb):
    """Test the federal_reserve.minneapolis.regional_gdp endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.regional_gdp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_regional_unemployment(params, obb):
    """Test the federal_reserve.minneapolis.regional_unemployment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.regional_unemployment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_publications(params, obb):
    """Test the federal_reserve.minneapolis.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_minneapolis_unemployment_claims(params, obb):
    """Test the federal_reserve.minneapolis.unemployment_claims endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.minneapolis.unemployment_claims(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "total", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_money_market_funds(params, obb):
    """Test the federal_reserve.money_market_funds endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.money_market_funds(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_money_measures(params, obb):
    """Test the federal_reserve.money_measures endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.money_measures(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_business_leaders(params, obb):
    """Test the federal_reserve.ny.business_leaders endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.business_leaders(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_ny_central_bank_holdings(params, obb):
    """Test the federal_reserve.ny.central_bank_holdings endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.central_bank_holdings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"breakdown": "overall", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_credit_access(params, obb):
    """Test the federal_reserve.ny.consumer_credit_access endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.consumer_credit_access(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"topic": "inflation_expectations", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_expectations(params, obb):
    """Test the federal_reserve.ny.consumer_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.consumer_expectations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"topic": "home_price_expectations", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_housing(params, obb):
    """Test the federal_reserve.ny.consumer_housing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.consumer_housing(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_consumer_labor_market(params, obb):
    """Test the federal_reserve.ny.consumer_labor_market endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.consumer_labor_market(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_core_trend_inflation(params, obb):
    """Test the federal_reserve.ny.core_trend_inflation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.core_trend_inflation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_corporate_bond_distress(params, obb):
    """Test the federal_reserve.ny.corporate_bond_distress endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.corporate_bond_distress(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_effr(params, obb):
    """Test the federal_reserve.ny.effr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.effr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"dataset": "seasonally_adjusted_diffusion", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_empire_state_manufacturing(params, obb):
    """Test the federal_reserve.ny.empire_state_manufacturing endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.empire_state_manufacturing(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_empire_state_reports(params, obb):
    """Test the federal_reserve.ny.empire_state_reports endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.empire_state_reports(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "total_debt_balance", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_household_debt(params, obb):
    """Test the federal_reserve.ny.household_debt endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.household_debt(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_market_expectations(params, obb):
    """Test the federal_reserve.ny.market_expectations endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.market_expectations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_overnight_bank_funding(params, obb):
    """Test the federal_reserve.ny.overnight_bank_funding endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.overnight_bank_funding(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"asset_class": "all", "unit": "value", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_primary_dealer_fails(params, obb):
    """Test the federal_reserve.ny.primary_dealer_fails endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.primary_dealer_fails(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"category": "treasuries", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_primary_dealer_positioning(params, obb):
    """Test the federal_reserve.ny.primary_dealer_positioning endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.primary_dealer_positioning(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_publications(params, obb):
    """Test the federal_reserve.ny.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_sofr(params, obb):
    """Test the federal_reserve.ny.sofr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.sofr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_ny_supply_chain_pressure(params, obb):
    """Test the federal_reserve.ny.supply_chain_pressure endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ny.supply_chain_pressure(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_average(params, obb):
    """Test the federal_reserve.ffiec.peer_group_average endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.peer_group_average(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"rssd_id": "451965", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_bank(params, obb):
    """Test the federal_reserve.ffiec.peer_group_bank endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.peer_group_bank(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"peer_group": "1", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_peer_group_distribution(params, obb):
    """Test the federal_reserve.ffiec.peer_group_distribution endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.peer_group_distribution(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_anxious_index(params, obb):
    """Test the federal_reserve.philadelphia.anxious_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.anxious_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_business_conditions(params, obb):
    """Test the federal_reserve.philadelphia.business_conditions endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.business_conditions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_gdpplus(params, obb):
    """Test the federal_reserve.philadelphia.gdpplus endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.gdpplus(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"variable": "RGDPX", "statistic": "mean", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_livingston_survey(params, obb):
    """Test the federal_reserve.philadelphia.livingston_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.livingston_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_manufacturing_outlook(params, obb):
    """Test the federal_reserve.philadelphia.manufacturing_outlook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.manufacturing_outlook(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"adjustment": "sa", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_nonmanufacturing_outlook(params, obb):
    """Test the federal_reserve.philadelphia.nonmanufacturing_outlook endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.nonmanufacturing_outlook(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_partisan_conflict(params, obb):
    """Test the federal_reserve.philadelphia.partisan_conflict endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.partisan_conflict(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_publications(params, obb):
    """Test the federal_reserve.philadelphia.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"dataset": "indexes", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_state_coincident_index(params, obb):
    """Test the federal_reserve.philadelphia.state_coincident_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.state_coincident_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_federal_reserve_philadelphia_survey_professional_forecasters(params, obb):
    """Test the federal_reserve.philadelphia.survey_professional_forecasters endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.survey_professional_forecasters(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"dataset": "inflation", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_philadelphia_term_structure_inflation(params, obb):
    """Test the federal_reserve.philadelphia.term_structure_inflation endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.philadelphia.term_structure_inflation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"start_date": "2026-01-01"}],
)
@pytest.mark.integration
def test_federal_reserve_release_calendar(params, obb):
    """Test the federal_reserve.release_calendar endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.release_calendar(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [{"table": "optimism", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_cfo_survey(params, obb):
    """Test the federal_reserve.richmond.cfo_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.cfo_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_manufacturing_survey(params, obb):
    """Test the federal_reserve.richmond.manufacturing_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.manufacturing_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_non_employment_index(params, obb):
    """Test the federal_reserve.richmond.non_employment_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.non_employment_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_recession_indicator(params, obb):
    """Test the federal_reserve.richmond.recession_indicator endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.recession_indicator(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_service_sector_survey(params, obb):
    """Test the federal_reserve.richmond.service_sector_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.service_sector_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"state": "virginia", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_state_survey(params, obb):
    """Test the federal_reserve.richmond.state_survey endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.state_survey(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_richmond_survey_releases(params, obb):
    """Test the federal_reserve.richmond.survey_releases endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.richmond.survey_releases(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_cyclical_pce(params, obb):
    """Test the federal_reserve.sf.cyclical_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.cyclical_pce(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_news_sentiment(params, obb):
    """Test the federal_reserve.sf.news_sentiment endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.news_sentiment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"frequency": "monthly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_proxy_funds_rate(params, obb):
    """Test the federal_reserve.sf.proxy_funds_rate endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.proxy_funds_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"publication_type": "economic_letter", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_publications(params, obb):
    """Test the federal_reserve.sf.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_short_rate_path(params, obb):
    """Test the federal_reserve.sf.short_rate_path endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.short_rate_path(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_supply_demand_pce(params, obb):
    """Test the federal_reserve.sf.supply_demand_pce endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.supply_demand_pce(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"maturity": 10, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_term_premium(params, obb):
    """Test the federal_reserve.sf.term_premium endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.term_premium(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"table": "quarterly", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_sf_total_factor_productivity(params, obb):
    """Test the federal_reserve.sf.total_factor_productivity endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.sf.total_factor_productivity(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"state": "SD", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_state_average(params, obb):
    """Test the federal_reserve.ffiec.state_average endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.state_average(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"transform": False, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_fred_md(params, obb):
    """Test the federal_reserve.stl.fred_md endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.stl.fred_md(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"transform": False, "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_fred_qd(params, obb):
    """Test the federal_reserve.stl.fred_qd endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.stl.fred_qd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"index": "financial_stress_index", "provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_national_index(params, obb):
    """Test the federal_reserve.stl.national_index endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.stl.national_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_stl_publications(params, obb):
    """Test the federal_reserve.stl.publications endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.stl.publications(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_treasury_rates(params, obb):
    """Test the federal_reserve.treasury_rates endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.treasury_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve", "rssd_id": "852218"}],
)
@pytest.mark.integration
def test_federal_reserve_ubpr(params, obb):
    """Test the federal_reserve.ffiec.ubpr endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.ffiec.ubpr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "federal_reserve"}],
)
@pytest.mark.integration
def test_federal_reserve_yield_curve(params, obb):
    """Test the federal_reserve.yield_curve endpoint."""
    params = {p: v for p, v in params.items() if v is not None}
    result = obb.federal_reserve.yield_curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

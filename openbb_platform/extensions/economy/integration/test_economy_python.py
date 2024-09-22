"""Test economy extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        (
            {
                "provider": "nasdaq",
                "start_date": "2023-10-24",
                "end_date": "2023-11-03",
                "country": "united_states,japan",
            }
        ),
        (
            {
                "provider": "tradingeconomics",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "country": "mexico,sweden",
                "importance": "low",
                "group": "gdp",
                "calendar_id": None,
            }
        ),
        (
            {
                "provider": "fmp",
                "start_date": "2023-10-24",
                "end_date": "2023-11-03",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_calendar(params, obb):
    """Test economy calendar."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.calendar(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "spain",
                "transform": "yoy",
                "frequency": "annual",
                "harmonized": False,
                "start_date": "2020-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            }
        ),
        (
            {
                "country": "portugal,spain",
                "transform": "period",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            }
        ),
        (
            {
                "country": "portugal,spain",
                "transform": "yoy",
                "frequency": "quarter",
                "harmonized": False,
                "start_date": "2020-01-01",
                "end_date": "2023-06-06",
                "provider": "oecd",
                "expenditure": "transport",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_cpi(params, obb):
    """Test economy cpi."""
    result = obb.economy.cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_economy_risk_premium(params, obb):
    """Test economy risk premium."""
    result = obb.economy.risk_premium(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
                "units": "volume",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdp_forecast(params, obb):
    """Test economy gdp forecast."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.forecast(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "econdb",
                "use_cache": False,
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "level",
                "price_base": "volume",
                "frequency": "quarter",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdp_nominal(params, obb):
    """Test economy gdp nominal."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.nominal(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "frequency": "quarter",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "oecd",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "econdb",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdp_real(params, obb):
    """Test economy gdp real."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.real(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "report_type": "summary",
                "frequency": "monthly",
                "country": None,
                "provider": "ecb",
            }
        ),
        (
            {
                "report_type": "direct_investment",
                "frequency": "monthly",
                "country": None,
                "provider": "ecb",
            }
        ),
        (
            {
                "report_type": "main",
                "frequency": "quarterly",
                "country": "united_states",
                "provider": "ecb",
            }
        ),
        (
            {
                "country": "united_states",
                "start_date": None,
                "end_date": None,
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_balance_of_payments(params, obb):
    """Test economy balance of payments."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.balance_of_payments(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "query": None,
                "is_release": False,
                "release_id": "15",
                "offset": 0,
                "limit": 1000,
                "filter_variable": "frequency",
                "filter_value": "Monthly",
                "tag_names": "nsa",
                "exclude_tag_names": None,
                "series_id": None,
                "provider": "fred",
            }
        ),
        (
            {
                "query": "GDP",
                "is_release": True,
                "release_id": None,
                "offset": 0,
                "limit": 1000,
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "series_id": None,
                "provider": "fred",
            }
        ),
        (
            {
                "query": None,
                "is_release": False,
                "release_id": None,
                "offset": None,
                "limit": None,
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "series_id": None,
                "provider": "fred",
            }
        ),
        (
            {
                "query": None,
                "is_release": False,
                "release_id": None,
                "offset": None,
                "limit": None,
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "series_id": "NYICLAIMS",
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_search(params, obb):
    """Test economy fred search."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.fred_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "SP500",
                "start_date": None,
                "end_date": None,
                "limit": 10000,
                "frequency": "q",
                "aggregation_method": "eop",
                "transform": "chg",
                "provider": "fred",
            }
        ),
        (
            {
                "symbol": "FEDFUNDS",
                "start_date": None,
                "end_date": None,
                "limit": 10000,
                "all_pages": True,
                "provider": "intrinio",
                "sleep": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_series(params, obb):
    """Test economy fred series."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.fred_series(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "adjusted": True}),
        (
            {
                "provider": "federal_reserve",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "adjusted": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_money_measures(params, obb):
    """Test economy money measures."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.money_measures(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "sex": "total",
                "frequency": "monthly",
                "age": "total",
                "seasonal_adjustment": True,
                "provider": "oecd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_unemployment(params, obb):
    """Test economy unemployment."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.unemployment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "adjustment": "amplitude",
                "growth_rate": False,
                "provider": "oecd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_composite_leading_indicator(params, obb):
    """Test economy composite leading indicator."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.composite_leading_indicator(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "frequency": "monthly",
                "provider": "oecd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_short_term_interest_rate(params, obb):
    """Test economy short term interest rate."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.short_term_interest_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "frequency": "monthly",
                "provider": "oecd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_long_term_interest_rate(params, obb):
    """Test economy long term interest rate."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.long_term_interest_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    argnames="params",
    argvalues=[
        (
            {
                "symbol": "156241",
                "is_series_group": True,
                "start_date": "2000-01-01",
                "end_date": None,
                "frequency": "w",
                "units": "Number",
                "region_type": "state",
                "season": "nsa",
                "aggregation_method": "eop",
                "transform": "ch1",
                "provider": "fred",
                "limit": None,
            }
        ),
        (
            {
                "symbol": "CAICLAIMS",
                "is_series_group": False,
                "start_date": "1990-01-01",
                "end_date": "2010-01-01",
                "frequency": None,
                "units": None,
                "region_type": None,
                "season": None,
                "aggregation_method": "avg",
                "transform": "chg",
                "provider": "fred",
                "limit": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_regional(params, obb):
    """Test economy fred regional."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.fred_regional(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "econdb",
                "country": "us,uk,jp",
                "latest": True,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_country_profile(params, obb):
    """Test economy country profile."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.country_profile(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "econdb", "use_cache": False}),
    ],
)
@pytest.mark.integration
def test_economy_available_indicators(params, obb):
    """Test economy available indicators."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.available_indicators(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "econdb",
                "country": "us,uk,jp",
                "symbol": "GDP,GDEBT",
                "transform": None,
                "start_date": "2022-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "frequency": None,
            }
        ),
        (
            {
                "provider": "econdb",
                "country": None,
                "symbol": "MAIN",
                "transform": None,
                "start_date": "2022-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "frequency": "quarter",
            }
        ),
        (
            {
                "provider": "imf",
                "country": "us,uk,jp",
                "symbol": "gold_reserves",
                "start_date": "2022-01-01",
                "end_date": "2023-12-31",
                "frequency": "annual",
            }
        ),
        (
            {
                "provider": "imf",
                "country": "all",
                "symbol": "derivative_assets",
                "start_date": "2022-01-01",
                "end_date": "2023-12-31",
                "frequency": "annual",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_indicators(params, obb):
    """Test economy indicators."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.indicators(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "date": None,
                "provider": "federal_reserve",
                "holding_type": "all_treasury",
                "summary": False,
                "monthly": False,
                "cusip": None,
                "wam": False,
            }
        ),
        (
            {
                "date": None,
                "provider": "federal_reserve",
                "holding_type": "all_agency",
                "summary": False,
                "monthly": False,
                "cusip": None,
                "wam": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_central_bank_holdings(params, obb):
    """Test economy central bank holdings."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.central_bank_holdings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states,united_kingdom",
                "frequency": "monthly",
                "provider": "oecd",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_share_price_index(params, obb):
    """Test economy share price index."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.share_price_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states,united_kingdom",
                "frequency": "quarter",
                "provider": "oecd",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "transform": "index",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_house_price_index(params, obb):
    """Test economy house price index."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.house_price_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states,united_kingdom",
                "frequency": "monthly",
                "provider": "oecd",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_immediate_interest_rate(params, obb):
    """Test economy immediate interest rate."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.immediate_interest_rate(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "frequency": "monthly",
                "provider": "oecd",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "duration": "long",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_interest_rates(params, obb):
    """Test economy country interest rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.interest_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "country": "united_states",
                "item": "meats",
                "region": "all_city",
                "frequency": "annual",
                "provider": "fred",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "transform": "pc1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_retail_prices(params, obb):
    """Test economy retail prices."""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.retail_prices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "frequency": None,
                "provider": "fred",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_university_of_michigan(params, obb):
    """Test the economy survey university_of_michigan endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.university_of_michigan(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "category": "auto",
                "provider": "fred",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_sloos(params, obb):
    """Test the economy survey sloos endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.sloos(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_economic_conditions_chicago(params, obb):
    """Test the economy survey economic conditions chicago endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.economic_conditions_chicago(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "topic": "business_outlook,new_orders",
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_manufacturing_outlook_texas(params, obb):
    """Test the economy survey manufacturing outlook texas endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.manufacturing_outlook_texas(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "federal_reserve",
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "category": "cmbs",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_primary_dealer_positioning(params, obb):
    """Test the economy primary dealer positioning endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.primary_dealer_positioning(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "date": "2024-06-01,2023-06-01",
                "category": "avg_earnings_hourly",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_nonfarm_payrolls(params, obb):
    """Test the economy survery nonfarm payrolls endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.nonfarm_payrolls(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "date": "2024-05-01,2024-04-01,2023-05-01",
                "category": "pce_price_index",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_pce(params, obb):
    """Test the economy pce endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.pce(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "fred",
                "date": None,
                "release_id": "14",
                "element_id": "7930",
            }
        ),
        (
            {
                "provider": "fred",
                "date": None,
                "release_id": "14",
                "element_id": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_release_table(params, obb):
    """Test the economy fred release table endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.fred_release_table(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "query": "gasoline;seattle;average price",
                "category": "cpi",
                "include_extras": False,
                "include_code_map": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_bls_search(params, obb):
    """Test the economy survey bls search endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.bls_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "bls",
                "symbol": "APUS49D74714,APUS49D74715,APUS49D74716",
                "start_date": "2024-01-01",
                "end_date": "2024-07-01",
                "aspects": False,
                "calculations": True,
                "annual_average": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_survey_bls_series(params, obb):
    """Test the economy survey bls series endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.survey.bls_series(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "econdb",
                "country": "IN,CN",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_export_destinations(params, obb):
    """Test the economy export destinations endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.export_destinations(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "federal_reserve",
                "start_date": None,
                "end_date": None,
                "asset_class": "mbs",
                "unit": "value",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_primary_dealer_fails(params, obb):
    """Test the economy primary dealer fails endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.primary_dealer_fails(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "econdb",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_port_volume(params, obb):
    """Test the economy port volume endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.port_volume(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "imf",
                "country": "us",
                "counterpart": "world,eu",
                "frequency": "annual",
                "direction": "exports",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_direction_of_trade(params, obb):
    """Test the economy direction of trade endpoint"""
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.direction_of_trade(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

"""Test Economy API."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
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
def test_economy_calendar(params, headers):
    """Test the economy calendar endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/calendar?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_cpi(params, headers):
    """Test the economy CPI endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/cpi?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"provider": "fmp"})],
)
@pytest.mark.integration
def test_economy_risk_premium(params, headers):
    """Test the economy risk premium endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/risk_premium?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_gdp_forecast(params, headers):
    """Test the economy GDP forecast endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/forecast?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
                "frequency": "quarter",
                "price_base": "volume",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdp_nominal(params, headers):
    """Test the economy GDP nominal endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/nominal?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_gdp_real(params, headers):
    """Test the economy GDP real endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/gdp/real?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_balance_of_payments(params, headers):
    """Test the economy balance of payments endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/balance_of_payments?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "query": "GDP*",
                "search_type": "series_id",
                "release_id": None,
                "offset": 0,
                "limit": 10,
                "order_by": "observation_end",
                "sort_order": "desc",
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
                "search_type": "release",
                "release_id": None,
                "offset": None,
                "limit": None,
                "order_by": "observation_end",
                "sort_order": "desc",
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
                "search_type": "full_text",
                "release_id": None,
                "offset": None,
                "limit": None,
                "order_by": "observation_end",
                "sort_order": "desc",
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
def test_economy_fred_search(params, headers):
    """Test the economy FRED search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_fred_series(params, headers):
    """Test the economy FRED series endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_series?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_money_measures(params, headers):
    """Test the economy money measures endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/money_measures?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_unemployment(params, headers):
    """Test the economy unemployment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/unemployment?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_composite_leading_indicator(params, headers):
    """Test the economy composite leading indicator endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/composite_leading_indicator?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "oecd"}),
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
def test_economy_short_term_interest_rate(params, headers):
    """Test the economy short term interest rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/short_term_interest_rate?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "oecd"}),
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
def test_economy_long_term_interest_rate(params, headers):
    """Test the economy long term interest rate endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/long_term_interest_rate?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
                "aggregation_method": None,
                "transform": None,
                "provider": "fred",
                "limit": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_regional(params, headers):
    """Test the economy FRED regional endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_regional?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_indicators(params, headers):
    """Test the economy indicators."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/indicators?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"provider": "econdb", "use_cache": False}),
    ],
)
@pytest.mark.integration
def test_economy_available_indicators(params, headers):
    """Test the economy available indicators."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/available_indicators?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_country_profile(params, headers):
    """Test the economy country profile."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/country_profile?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_central_bank_holdings(params, headers):
    """Test the economy central bank holdings."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/central_bank_holdings?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_share_price_index(params, headers):
    """Test the economy share price index."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/share_price_index?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_house_price_index(params, headers):
    """Test the economy house price index."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/house_price_index?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_immediate_interest_rate(params, headers):
    """Test the economy immediate_interest_rate."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/immediate_interest_rate?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_interest_rates(params, headers):
    """Test the economy interest rates endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/interest_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_retail_prices(params, headers):
    """Test the economy retail_prices."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/retail_prices?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_university_of_michigan(params, headers):
    """Test the economy survey university_of_michigan endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/economy/survey/university_of_michigan?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_sloos(params, headers):
    """Test the economy survey sloos endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/sloos?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_economic_conditions_chicago(params, headers):
    """Test the economy survey economic_conditions_chicago endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/economic_conditions_chicago?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_manufacturing_outlook_texas(params, headers):
    """Test the economy survey manufacturing outlook texas endpoint"""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/manufacturing_outlook_texas?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_primary_dealer_positioning(params, headers):
    """Test the economy primary dealer positioning endpoint"""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/primary_dealer_positioning?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_nonfarm_payrolls(params, headers):
    """Test the economy survey nonfarm payrolls endpoint"""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/nonfarm_payrolls?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_pce(params, headers):
    """Test the economy pce endpoint"""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/pce?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_fred_release_table(params, headers):
    """Test the economy fred release table"""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/fred_release_table?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_bls_search(params, headers):
    """Test the economy survey bls search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/bls_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_survey_bls_series(params, headers):
    """Test the economy survey bls search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/survey/bls_series?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_export_destinations(params, headers):
    """Test the economy export destinations endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/export_destinations?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_primary_dealer_fails(params, headers):
    """Test the economy primary dealer fails endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/primary_dealer_fails?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_port_volume(params, headers):
    """Test the economy port volume endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/port_volume?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_economy_direction_of_trade(params, headers):
    """Test the economy direction of trade endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/economy/direction_of_trade?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

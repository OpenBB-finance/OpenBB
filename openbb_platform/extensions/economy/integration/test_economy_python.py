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
                "country": "portugal,spain",
                "units": "growth_same",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
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
        ({"units": "usd", "start_date": "2021-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "usd",
                "start_date": "2021-01-01",
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
        ({"units": "yoy", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "yoy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
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
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
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
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
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
                "season": "NSA",
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

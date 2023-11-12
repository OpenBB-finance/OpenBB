"""Test economy extension."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
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
                "importance": "Medium",
                "group": "gdp",
            }
        ),
        (
            {
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_calendar(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.calendar(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "countries": ["portugal", "spain"],
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
    result = obb.economy.cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({}),
    ],
)
@pytest.mark.integration
def test_economy_risk_premium(params, obb):
    result = obb.economy.risk_premium(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.forecast(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.nominal(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdp.real(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
    ],
)
@pytest.mark.integration
def test_economy_balance_of_payments(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.balance_of_payments(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

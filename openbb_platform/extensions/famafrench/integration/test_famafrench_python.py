"""Test Fama-French Python Interface."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "region": "america",
                "factor": "momentum",
                "frequency": "monthly",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_factors(params, obb):
    """Test the Fama-French factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.factors(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "portfolio": "5_industry_portfolios",
                "measure": "equal",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_us_portfolio_returns(params, obb):
    """Test the US portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.us_portfolio_returns(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "portfolio": "developed_ex_us_6_portfolios_me_op",
                "measure": "equal",
                "frequency": None,
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_regional_portfolio_returns(params, obb):
    """Test the regional portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.regional_portfolio_returns(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "country": "japan",
                "measure": "ratios",
                "frequency": None,
                "start_date": None,
                "end_date": None,
                "dividends": True,
                "all_data_items_required": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_country_portfolio_returns(params, obb):
    """Test the country portfolio returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.country_portfolio_returns(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "index": "asia_pacific",
                "measure": "local",
                "frequency": "annual",
                "start_date": None,
                "end_date": None,
                "dividends": True,
                "all_data_items_required": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_international_index_returns(params, obb):
    """Test the international index returns endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.international_index_returns(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "famafrench",
            }
        ),
        (
            {
                "provider": "famafrench",
                "breakpoint_type": "op",
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_breakpoints(params, obb):
    """Test the Fama-French breakpoints endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.breakpoints(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "region": "america",
                "factor": "Momentum",
                "is_portfolio": None,
                "portfolio": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_famafrench_factor_choices(params, obb):
    """Test Fama-French available factors endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.famafrench.factor_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0

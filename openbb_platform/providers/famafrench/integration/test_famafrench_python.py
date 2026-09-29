"""Fama-French Python interface integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    return None


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"region": "europe", "factor": "5_factors", "frequency": "monthly"},
    ],
)
@pytest.mark.integration
def test_famafrench_factors(params, obb):
    """Test the famafrench factors endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.factors(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {},
        {
            "portfolio": "portfolios_formed_on_me",
            "measure": "equal",
            "frequency": "annual",
        },
    ],
)
@pytest.mark.integration
def test_famafrench_us_portfolio_returns(params, obb):
    """Test the famafrench us_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.us_portfolio_returns(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"measure": "equal", "frequency": "annual"},
    ],
)
@pytest.mark.integration
def test_famafrench_regional_portfolio_returns(params, obb):
    """Test the famafrench regional_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.regional_portfolio_returns(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"country": "japan", "measure": "local", "frequency": "annual"},
    ],
)
@pytest.mark.integration
def test_famafrench_country_portfolio_returns(params, obb):
    """Test the famafrench country_portfolio_returns endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.country_portfolio_returns(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"index": "europe_ex_uk", "frequency": "annual"},
    ],
)
@pytest.mark.integration
def test_famafrench_international_index_returns(params, obb):
    """Test the famafrench international_index_returns endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.international_index_returns(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"breakpoint_type": "op", "start_date": "1998-01-01"},
    ],
)
@pytest.mark.integration
def test_famafrench_breakpoints(params, obb):
    """Test the famafrench breakpoints endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.famafrench.breakpoints(provider="famafrench", **params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

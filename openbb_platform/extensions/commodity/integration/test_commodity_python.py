"""Test Commodity extension."""

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
                "asset": "gold",
                "start_date": None,
                "end_date": None,
                "collapse": None,
                "transform": None,
                "provider": "nasdaq",
            }
        ),
        (
            {
                "asset": "silver",
                "start_date": "1990-01-01",
                "end_date": "2023-01-01",
                "collapse": "monthly",
                "transform": "diff",
                "provider": "nasdaq",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_lbma_fixing(params, obb):
    """Test the LBMA fixing endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.commodity.lbma_fixing(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "category": "balance_sheet",
                "table": "stocks",
                "start_date": None,
                "end_date": None,
                "provider": "eia",
                "use_cache": True,
            }
        ),
        (
            {
                "category": "weekly_estimates",
                "table": "crude_production",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "provider": "eia",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_petroleum_status_report(params, obb):
    """Test Commodity extension."""
    result = obb.commodity.petroleum_status_report(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

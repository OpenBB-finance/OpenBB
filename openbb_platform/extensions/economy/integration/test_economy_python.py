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
        (
            {
                "provider": "bis",
                "country": "united_states,japan",
                "frequency": "quarter",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
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

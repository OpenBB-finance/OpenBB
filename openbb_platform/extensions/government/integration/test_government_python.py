"""Test Government extension."""

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
                "provider": "congress_gov",
            }
        ),
        (
            {
                "provider": "congress_gov",
                "limit": 5,
                "sort": "desc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_government_congress_bills(params, obb):
    """Test government congress bills."""
    params = {p: v for p, v in params.items() if v}

    result = obb.government.us.congress_bills(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

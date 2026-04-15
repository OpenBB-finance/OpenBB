"""Test Regulators extension."""

# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.model.obbject import OBBject


# pylint: disable=inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "query": "grain",
                "report_type": "legacy",
                "futures_only": False,
                "category": None,
                "subcategory": None,
                "code": None,
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_cftc_cot_search(params, obb):
    """Test the CFTC COT search endpoint."""
    result = obb.cftc.cot_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "code": "045601",
                "report_type": "legacy",
                "start_date": None,
                "end_date": None,
                "limit": 1,
                "futures_only": False,
                "measure": "all",
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_cftc_cot(params, obb):
    """Test the CFTC COT endpoint."""
    result = obb.cftc.cot(**params)
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
@pytest.mark.skip(reason="This is not included in the Python interface.")
def test_cftc_get_cot_choices(params, obb):
    """Test the CFTC get_cot_choices endpoint."""
    result = obb.cftc.get_cot_choices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

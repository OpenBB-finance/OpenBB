"""Federal Reserve Utilities module integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.skip(reason="Not implemented in Python Interface.")
@pytest.mark.parametrize(
    "params",
    [{"params": {}}],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_download(params, obb):
    """Test federal_reserve_fomc_documents_download endpoint."""
    params = {
        "url": [
            "https://www.federalreserve.gov/monetarypolicy/files/BeigeBook_20230118.pdf"
        ]
    }

    result = obb.federal_reserve.fomc_documents_download(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.skip(reason="Not implemented in Python Interface.")
@pytest.mark.parametrize(
    "params",
    [
        {
            "year": 2022,
            "document_type": "minutes",
        }
    ],
)
@pytest.mark.integration
def test_federal_reserve_fomc_documents_choices(params, obb):
    """Test federal_reserve_fomc_documents_choices endpoint."""

    result = obb.federal_reserve.fomc_documents_choices(**params)
    assert result
    assert isinstance(result, OBBject)

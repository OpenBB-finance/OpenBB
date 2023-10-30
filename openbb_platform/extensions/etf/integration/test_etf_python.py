"""Test etf extension."""
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
        ({"query": None, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_search(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
        (
            {
                "symbol": "MISL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_historical(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_info(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_sectors(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.sectors(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

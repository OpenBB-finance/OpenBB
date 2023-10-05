"""Test futures extension."""
import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "ES",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "expiration": "2024-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "1d",
                "prepost": True,
                "adjust": True,
                "back_adjust": True,
                "provider": "yfinance",
                "symbol": "ES",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "expiration": "2024-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_futures_load(params, obb):
    result = obb.futures.load(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01"}),
    ],
)
@pytest.mark.integration
def test_futures_curve(params, obb):
    result = obb.futures.curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

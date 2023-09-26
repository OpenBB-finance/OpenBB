"""Test futures extension."""
import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


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
def test_futures_load(params):
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
def test_futures_curve(params):
    result = obb.futures.curve(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

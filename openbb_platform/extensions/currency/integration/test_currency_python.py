"""Test currency extension."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name
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
                "provider": "fmp",
                "query": "eur",
            }
        ),
        (
            {
                "provider": "intrinio",
                "query": "eur",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_search(params, obb):
    """Test the currency search endpoint."""
    result = obb.currency.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "EURUSD",
                "interval": "1d",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fmp",
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "fmp",
                "symbol": "EURUSD,USDJPY",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-10",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "yfinance",
                "symbol": "EURUSD",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "tiingo",
                "symbol": "EURUSD",
                "start_date": "2023-05-21",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "tiingo",
                "symbol": "EURUSD",
                "start_date": "2023-05-21",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_price_historical(params, obb):
    """Test the currency historical price endpoint."""
    result = obb.currency.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "ecb"}],
)
@pytest.mark.integration
def test_currency_reference_rates(params, obb):
    """Test the currency reference rates endpoint."""
    result = obb.currency.reference_rates(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.model_dump()["results"].items()) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "base": "USD,XAU",
                "counter_currencies": "EUR,JPY,GBP",
                "quote_type": "indirect",
            }
        ),
    ],
)
@pytest.mark.integration
def test_currency_snapshots(params, obb):
    """Test the currency snapshots endpoint."""
    result = obb.currency.snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

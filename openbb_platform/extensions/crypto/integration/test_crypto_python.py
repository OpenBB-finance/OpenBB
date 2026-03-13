"""Test crypto extension."""

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
        ({"query": "asd"}),
        ({"query": "btc", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_crypto_search(params, obb):
    """Test the crypto search endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.crypto.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "interval": "1d",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "fmp",
                "symbol": "BTCUSD,ETHUSD",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-04",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1d",
                "exchanges": None,
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1h",
                "exchanges": ["POLONIEX", "GDAX"],
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
    ],
)
@pytest.mark.integration
def test_crypto_price_historical(params, obb):
    """Test crypto price historical."""
    result = obb.crypto.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

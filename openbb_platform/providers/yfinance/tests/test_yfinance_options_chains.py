"""Tests for the YFinance options chains model."""

import pytest
from numpy import nan
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.models.options_chains import (
    YFinanceOptionsChainsFetcher,
    YFinanceOptionsChainsQueryParams,
)


def test_transform_data_normalizes_missing_values_and_preserves_metadata():
    """Test missing-value normalization and metadata preservation."""
    query = YFinanceOptionsChainsQueryParams(symbol="AAPL")
    data = {
        "underlying": {
            "symbol": "AAPL",
            "exchange": "NMS",
            "currency": "USD",
        },
        "chains": [
            {
                "contractSymbol": "AAPL260731C00200000",
                "expiration": "2026-07-31",
                "dte": 4,
                "strike": 200.0,
                "option_type": "call",
                "volume": nan,
                "openInterest": nan,
                "bid": nan,
            }
        ],
    }

    transformed = YFinanceOptionsChainsFetcher.transform_data(query, data)

    assert transformed.metadata == data["underlying"]
    assert transformed.result is not None
    assert transformed.result.contract_symbol == ["AAPL260731C00200000"]
    assert transformed.result.volume == [0]
    assert transformed.result.open_interest == [0]
    assert transformed.result.bid == [None]


def test_transform_data_converts_existing_counts_to_integers():
    """Test that numeric volume and open interest become integers."""
    query = YFinanceOptionsChainsQueryParams(symbol="AAPL")
    data = {
        "underlying": {"symbol": "AAPL"},
        "chains": [
            {
                "contractSymbol": "AAPL260731P00200000",
                "expiration": "2026-07-31",
                "dte": 4,
                "strike": 200.0,
                "option_type": "put",
                "volume": 12.0,
                "openInterest": 34.0,
            }
        ],
    }

    transformed = YFinanceOptionsChainsFetcher.transform_data(query, data)

    assert transformed.result is not None
    assert transformed.result.volume == [12]
    assert transformed.result.open_interest == [34]
    assert isinstance(transformed.result.volume[0], int)
    assert isinstance(transformed.result.open_interest[0], int)


def test_transform_data_raises_for_empty_data():
    """Test that empty input raises EmptyDataError."""
    query = YFinanceOptionsChainsQueryParams(symbol="AAPL")

    with pytest.raises(EmptyDataError):
        YFinanceOptionsChainsFetcher.transform_data(query, {})

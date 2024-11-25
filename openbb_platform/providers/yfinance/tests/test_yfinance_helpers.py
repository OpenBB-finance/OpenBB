"""Test yfinance helpers."""

import pandas as pd
import pytest

from providers.yfinance.openbb_yfinance.utils.helpers import (
    df_transform_numbers,
    get_futures_data,
)

# pylint: disable=redefined-outer-name, unused-argument

MOCK_FUTURES_DATA = pd.DataFrame({"Ticker": ["ES", "NQ"], "Exchange": ["CME", "CME"]})


@pytest.fixture
def mock_futures_csv(monkeypatch):
    """Mock pd.read_csv to return predefined futures data."""
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: MOCK_FUTURES_DATA)


def test_get_futures_data(mock_futures_csv):
    """Test get_futures_data."""
    df = get_futures_data()
    assert not df.empty
    assert df.equals(MOCK_FUTURES_DATA)


def test_df_transform_numbers():
    """Test df_transform_numbers."""
    data = pd.DataFrame(
        {"Value": ["1M", "2.5B", "3T"], "% Change": ["1%", "-2%", "3.5%"]}
    )
    transformed = df_transform_numbers(data, ["Value", "% Change"])
    assert transformed["Value"].equals(pd.Series([1e6, 2.5e9, 3e12]))
    assert transformed["% Change"].equals(pd.Series([1/100, -2/100, 3.5/100]))

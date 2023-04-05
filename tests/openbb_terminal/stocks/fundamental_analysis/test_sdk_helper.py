"""Test the SDK helper functions."""

import pytest
from pandas import DataFrame

from openbb_terminal.stocks.fundamental_analysis import sdk_helpers


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, kwargs",
    [
        ("AAPL", "YahooFinance", {}),
        ("AAPL", "AlphaVantage", {}),
        ("AAPL", "FinancialModelingPrep", {}),
        ("AAPL", "Polygon", {}),
    ],
)
def test_get_income_statement(symbol, source, kwargs):
    """Test the get_income_statement function."""
    df = sdk_helpers.get_income_statement(symbol, source=source, **kwargs)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, kwargs",
    [
        ("AAPL", "YahooFinance", {}),
        ("AAPL", "AlphaVantage", {}),
        ("AAPL", "FinancialModelingPrep", {}),
        ("AAPL", "Polygon", {}),
    ],
)
def test_get_balance_sheet(symbol, source, kwargs):
    """Test the get_balance_sheet function."""
    df = sdk_helpers.get_balance_sheet(symbol, source=source, **kwargs)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, kwargs",
    [
        ("AAPL", "YahooFinance", {}),
        ("AAPL", "AlphaVantage", {}),
        ("AAPL", "FinancialModelingPrep", {}),
        ("AAPL", "Polygon", {}),
    ],
)
def test_get_cash_flow(symbol, source, kwargs):
    """Test the get_cash_flow function."""
    df = sdk_helpers.get_cash_flow(symbol, source=source, **kwargs)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, quarterly",
    [
        ("AAPL", "YahooFinance", False),
        ("AAPL", "AlphaVantage", False),
    ],
)
def test_earnings(symbol, source, quarterly):
    """Test the earnings function."""
    df = sdk_helpers.earnings(symbol, source=source, quarterly=quarterly)
    assert isinstance(df, DataFrame)
    assert not df.empty

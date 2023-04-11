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
            ("api_token", "MOCK_API_KEY"),
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
    "symbol, source, func, kwargs",
    [
        ("AAPL", "EODHD", "get_income_statement", {}),
        ("AAPL", "EODHD", "get_balance_sheet", {}),
        ("AAPL", "EODHD", "get_cash_flow", {}),
    ],
)
def test_eodhd_premium(symbol, source, func, kwargs):
    """Test the get_income_statement function."""
    df = getattr(sdk_helpers, func)(symbol, source=source, **kwargs)
    assert isinstance(df, DataFrame)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, quarterly, func",
    [
        ("AAPL", "YahooFinance", True, "get_income_statement"),
        ("AAPL", "YahooFinance", True, "get_balance_sheet"),
        ("AAPL", "YahooFinance", True, "get_cash_flow"),
    ],
)
def test_yahoo_finance_no_quarterly(symbol, source, quarterly, func):
    """Test the get_income_statement function."""
    df = getattr(sdk_helpers, func)(symbol, source=source, quarterly=quarterly)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, source, kwargs",
    [
        ("AAPL", "YahooFinance", {"limit": 1}),
        ("AAPL", "AlphaVantage", {"limit": 1}),
        ("AAPL", "FinancialModelingPrep", {"limit": 1}),
        ("AAPL", "Polygon", {"limit": 1}),
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
        ("AAPL", "YahooFinance", {"limit": 1}),
        ("AAPL", "AlphaVantage", {"limit": 1}),
        ("AAPL", "FinancialModelingPrep", {"limit": 1}),
        ("AAPL", "Polygon", {"limit": 1}),
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

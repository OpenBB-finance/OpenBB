"""Tests for the Nasdaq fetchers."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_nasdaq.models.calendar_dividend import NasdaqCalendarDividendFetcher
from openbb_nasdaq.models.calendar_earnings import NasdaqCalendarEarningsFetcher
from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
from openbb_nasdaq.models.equity_screener import NasdaqEquityScreenerFetcher
from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher
from openbb_nasdaq.models.historical_dividends import NasdaqHistoricalDividendsFetcher
from openbb_nasdaq.models.top_retail import NasdaqTopRetailFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
            ("x-api-token", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
            ("x-api-token", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_nasdaq_equity_search_fetcher(credentials=test_credentials):
    """Test the Nasdaq Equity Search fetcher."""
    params = {"query": "", "is_etf": True, "use_cache": False}

    fetcher = NasdaqEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_economic_calendar_fetcher(credentials=test_credentials):
    """Test the Nasdaq Economic Calendar fetcher."""
    params = {
        "start_date": datetime.date(2024, 7, 1),
        "end_date": datetime.date(2024, 7, 7),
    }

    fetcher = NasdaqEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_dividend_fetcher(credentials=test_credentials):
    """Test the Nasdaq Calendar Dividend fetcher."""
    params = {
        "start_date": datetime.date(2024, 7, 1),
        "end_date": datetime.date(2024, 7, 7),
    }

    fetcher = NasdaqCalendarDividendFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_ipo_fetcher(credentials=test_credentials):
    """Test the Nasdaq Calendar IPO fetcher."""
    params = {
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 7, 1),
        "status": "upcoming",
    }

    fetcher = NasdaqCalendarIpoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_top_retail_fetcher(credentials=test_credentials):
    """Test the Nasdaq Top Retail fetcher."""
    params = {}

    fetcher = NasdaqTopRetailFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_earnings_fetcher(credentials=test_credentials):
    """Test the Nasdaq Calendar Earnings fetcher."""
    params = {
        "start_date": datetime.date(2024, 7, 1),
        "end_date": datetime.date(2024, 7, 3),
    }

    fetcher = NasdaqCalendarEarningsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_historical_dividends_fetcher(credentials=test_credentials):
    """Test the Nasdaq Historical Dividends fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = NasdaqHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_equity_screener_fetcher(credentials=test_credentials):
    """Test the Nasdaq Equity Screener fetcher."""
    params = {"mktcap": "large", "sector": "consumer_staples"}

    fetcher = NasdaqEquityScreenerFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

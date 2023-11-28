import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_nasdaq.models.calendar_dividend import NasdaqCalendarDividendFetcher
from openbb_nasdaq.models.calendar_earnings import NasdaqCalendarEarningsFetcher
from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
from openbb_nasdaq.models.cot import NasdaqCotFetcher
from openbb_nasdaq.models.cot_search import NasdaqCotSearchFetcher
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher
from openbb_nasdaq.models.sp500_multiples import NasdaqSP500MultiplesFetcher
from openbb_nasdaq.models.top_retail import NasdaqTopRetailFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("api_key", "MOCK_API_KEY")],
    }


@pytest.mark.record_http
def test_nasdaq_equity_search_fetcher(credentials=test_credentials):
    params = {"query": "", "is_etf": True, "use_cache": False}

    fetcher = NasdaqEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_economic_calendar_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 11, 3),
        "end_date": datetime.date(2023, 11, 3),
    }

    fetcher = NasdaqEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_dividend_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 11, 6),
        "end_date": datetime.date(2023, 11, 6),
    }

    fetcher = NasdaqCalendarDividendFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_ipo_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 11, 1),
        "end_date": datetime.date(2023, 11, 30),
        "status": "upcoming",
    }

    fetcher = NasdaqCalendarIpoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_top_retail_fetcher(credentials=test_credentials):
    params = {}

    fetcher = NasdaqTopRetailFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_sp500_multiples_fetcher(credentials=test_credentials):
    params = {}

    fetcher = NasdaqSP500MultiplesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_cot_fetcher(credentials=test_credentials):
    params = {}

    fetcher = NasdaqCotFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_nasdaq_cot_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = NasdaqCotSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_nasdaq_calendar_earnings_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 11, 1),
        "end_date": datetime.date(2023, 11, 30),
    }

    fetcher = NasdaqCalendarEarningsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

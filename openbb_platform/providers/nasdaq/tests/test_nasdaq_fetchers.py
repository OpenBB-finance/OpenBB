import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_nasdaq.models.calendar_dividend import NasdaqDividendCalendarFetcher
from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
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
def test_nasdaq_economic_calendar_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 10, 23),
        "end_date": datetime.date(2023, 10, 26),
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

    fetcher = NasdaqDividendCalendarFetcher()
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

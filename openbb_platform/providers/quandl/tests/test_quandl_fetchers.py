import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_quandl.models.cot import QuandlCotFetcher
from openbb_quandl.models.cot_search import QuandlCotSearchFetcher
from openbb_quandl.models.economic_calendar import QuandlEconomicCalendarFetcher
from openbb_quandl.models.sp500_multiples import QuandlSP500MultiplesFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-api-token", "MOCK_API_TOKEN")],
    }


@pytest.mark.record_http
def test_quandl_sp500_multiples_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlSP500MultiplesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_quandl_cot_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlCotFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_quandl_cot_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlCotSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_quandl_economic_calendar_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 10, 26),
        "end_date": datetime.date(2023, 10, 30),
    }

    fetcher = QuandlEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

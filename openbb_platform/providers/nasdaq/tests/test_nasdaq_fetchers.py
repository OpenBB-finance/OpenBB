import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.record_http
def test_nasdaq_economic_calendar_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 11, 3),
        "end_date": datetime.date(2023, 11, 3),
    }

    fetcher = NasdaqEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

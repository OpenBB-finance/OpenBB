from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tradingeconomics.models.economic_calendar import TEEconomicCalendarFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("c", "mock_api_key"),
        ],
    }


@pytest.mark.record_http
def test_tradingeconomics_economic_calendar_fetcher(credentials=test_credentials):
    params = {
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = TEEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

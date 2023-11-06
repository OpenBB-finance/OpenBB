import pytest
from openbb_core.app.service.user_service import UserService
from openbb_seeking_alpha.models.upcoming_release_days import (
    SAUpcomingReleaseDaysFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.record_http
def test_sa_upcoming_release_days_fetcher(credentials=test_credentials):
    params = {"start_date": "2023-11-03", "limit": 5}

    fetcher = SAUpcomingReleaseDaysFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

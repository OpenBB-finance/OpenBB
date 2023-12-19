import pytest
from openbb_core.app.service.user_service import UserService
from openbb_wsj.models.active import WSJActiveFetcher
from openbb_wsj.models.gainers import WSJGainersFetcher
from openbb_wsj.models.losers import WSJLosersFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_wsj_gainers_fetcher(credentials=test_credentials):
    params = {}

    fetcher = WSJGainersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_wsj_losers_fetcher(credentials=test_credentials):
    params = {}

    fetcher = WSJLosersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_wsj_active_fetcher(credentials=test_credentials):
    params = {}

    fetcher = WSJActiveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

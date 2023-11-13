import pytest
from openbb_biztoc.models.global_news import BiztocGlobalNewsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.dict()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None), ("X-RapidAPI-Key", "MOCK_API_KEY")],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_biztoc_global_news_fetcher(credentials=test_credentials):
    params = {"term": "earnings"}

    fetcher = BiztocGlobalNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

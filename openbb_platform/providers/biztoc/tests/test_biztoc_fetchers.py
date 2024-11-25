"""Tests for the Biztoc fetchers."""

import pytest
from openbb_biztoc.models.world_news import BiztocWorldNewsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("X-RapidAPI-Key", "MOCK_API_KEY"),
            ("User-Agent", None),
        ],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_biztoc_world_news_fetcher(credentials=test_credentials):
    """Test the Biztoc World News fetcher."""
    params = {"source": "bloomberg"}

    fetcher = BiztocWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

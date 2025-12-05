"""Test the BIS fetchers."""

import datetime

import pytest
from openbb_bis.models.house_price_index import (
    BISHousePriceIndexFetcher,
)
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
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
def test_bis_house_price_index_fetcher(credentials=test_credentials):
    """Test the BIS House Price Index fetcher."""
    params = {
        "start_date": datetime.date(2023, 11, 3),
        "end_date": datetime.date(2024, 5, 3),
        "country": "united_kingdom",
    }

    fetcher = BISHousePriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

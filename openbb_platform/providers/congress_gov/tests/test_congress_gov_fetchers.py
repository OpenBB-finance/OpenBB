"""Congress.gov Fetchers tests."""

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_congress_bills_fetcher(credentials=test_credentials):
    """Test Congress Bills fetcher."""
    params = {
        "limit": 5,
        "sort": "desc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

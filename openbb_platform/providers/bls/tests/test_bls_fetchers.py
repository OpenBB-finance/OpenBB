"""Test the BLS fetchers."""

from datetime import date

import pytest
from openbb_bls.models.search import BlsSearchFetcher
from openbb_bls.models.series import BlsSeriesFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_post_data_parameters": [("registrationkey", "MOCK_API_KEY")],
        "filter_query_parameters": [
            ("registrationkey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_bls_series_fetcher(credentials=test_credentials):
    """Test the BLS Series fetcher."""
    params = {
        "symbol": "APU0000701111",
        "start_date": date(2022, 1, 1),
        "end_date": date(2022, 12, 1),
    }

    fetcher = BlsSeriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


# The data for this request are local files, so we can't record them.
def test_bls_search_fetcher(credentials=test_credentials):
    """Test the BLS Search fetcher."""
    params = {"category": "cpi", "query": "average price;flour"}

    fetcher = BlsSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

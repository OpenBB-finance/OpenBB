"""Test NSE fetchers."""

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_nse.models.index_constituents import NseIndexConstituentsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(mode="json")


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [],
    }


@pytest.mark.record_http
def test_nse_index_constituents_fetcher(credentials=test_credentials):
    """Test the NSE Index Constituents fetcher."""
    params = {"symbol": "nifty_50"}

    fetcher = NseIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

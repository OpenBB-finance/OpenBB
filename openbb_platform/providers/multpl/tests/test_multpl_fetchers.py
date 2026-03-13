"""Multpl Fetcher Tests."""

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_multpl.models.sp500_multiples import MultplSP500MultiplesFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.record_http
def test_multpl_sp500_multiples_fetcher(credentials=None):
    """Test multpl sp500 multiples fetcher."""
    params = {}

    fetcher = MultplSP500MultiplesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

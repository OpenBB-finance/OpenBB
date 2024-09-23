"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.models.senate_disclosures import USSenateDisclosuresFetcher, USSenateDisclosuresQueryParams
import asyncio
test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }

@pytest.mark.record_http
def test_senate_disclosures_fetcher(credentials=test_credentials):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    params = {
        "num_reports": 5
    }

    fetcher = USSenateDisclosuresFetcher()
    result = fetcher.test(params, credentials)
    assert result is None



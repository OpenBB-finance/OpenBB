"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.models.hor_disclosures import USHoRDisclosuresData, USHoRDisclosuresQueryParams, USHoRDisclosuresFetcher
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
def test_hor_disclosures_fetcher(credentials=test_credentials):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    params = {
        "year": 2024
    }

    fetcher = USHoRDisclosuresFetcher()
    result = fetcher.test(params, credentials)
    assert result is None



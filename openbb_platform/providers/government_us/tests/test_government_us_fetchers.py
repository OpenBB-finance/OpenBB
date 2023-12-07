"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.models.treasury_auctions import (
    GovernmentUSTreasuryAuctionsFetcher,
)
from openbb_government_us.models.treasury_prices import (
    GovernmentUSTreasuryPricesFetcher,
)

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
def test_government_us_treasury_auctions_fetcher(credentials=test_credentials):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    params = {
        "start_date": datetime.date(2023, 9, 1),
        "end_date": datetime.date(2023, 11, 16),
    }

    fetcher = GovernmentUSTreasuryAuctionsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_government_us_treasury_prices_fetcher(credentials=test_credentials):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    params = {}

    fetcher = GovernmentUSTreasuryPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.utils import senate_helpers

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
@pytest.mark.asyncio
async def test_get_transactions():
    """Test GovernmentUSTreasuryAuctionsFetcher."""


    result = await senate_helpers.get_transactions(num_reports=10)
    print(result)
    assert result is not  None




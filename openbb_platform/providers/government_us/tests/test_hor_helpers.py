"""Government US Fetchers tests."""

import datetime

import pytest

from openbb_government_us.utils import hor_helpers

@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }

@pytest.mark.asyncio
async def test_get_transactions():
    """Test GovernmentUSTreasuryAuctionsFetcher."""


    result = await hor_helpers.get_transactions(2024)
    print(result)
    assert result is not  None




"""Test OilPriceAPI fetchers."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_oilpriceapi.models.commodity_spot_prices import (
    OilPriceAPICommoditySpotPricesFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.mark.record_http
def test_oilpriceapi_commodity_spot_prices_fetcher(credentials=test_credentials):
    """Test the OilPriceAPI commodity spot prices fetcher, latest observation."""
    params = {"commodity": "brent"}

    fetcher = OilPriceAPICommoditySpotPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oilpriceapi_commodity_spot_prices_fetcher_historical(
    credentials=test_credentials,
):
    """Test the OilPriceAPI commodity spot prices fetcher over a date range."""
    params = {
        "commodity": "wti",
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 7, 31),
    }

    fetcher = OilPriceAPICommoditySpotPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

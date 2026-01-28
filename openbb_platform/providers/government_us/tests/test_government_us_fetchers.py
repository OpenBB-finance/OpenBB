"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.models.commodity_psd_data import (
    GovernmentUsCommodityPsdDataFetcher,
)
from openbb_government_us.models.commodity_psd_report import (
    GovernmentUsCommodityPsdReportFetcher,
)
from openbb_government_us.models.treasury_auctions import (
    GovernmentUSTreasuryAuctionsFetcher,
)
from openbb_government_us.models.treasury_prices import (
    GovernmentUSTreasuryPricesFetcher,
)
from openbb_government_us.models.weather_bulletin import (
    GovernmentUsWeatherBulletinFetcher,
)
from openbb_government_us.models.weather_bulletin_download import (
    GovernmentUsWeatherBulletinDownloadFetcher,
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
    params = {"date": datetime.date(2024, 6, 25)}

    fetcher = GovernmentUSTreasuryPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_government_us_commodity_psd_report_fetcher(credentials=test_credentials):
    """Test GovernmentUsCommodityPsdReportFetcher."""
    params = {
        "commodity": "sugar",
        "year": 2025,
        "month": 5,
    }

    fetcher = GovernmentUsCommodityPsdReportFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_government_us_weather_bulletin_fetcher(credentials=test_credentials):
    """Test GovernmentUsWeatherBulletinFetcher."""
    params = {"year": 2024, "month": 12, "week": 2}

    fetcher = GovernmentUsWeatherBulletinFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_government_us_weather_bulletin_download_fetcher(credentials=test_credentials):
    """Test GovernmentUsWeatherBulletinDownloadFetcher."""
    params = {
        "urls": [
            "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
        ],
    }

    fetcher = GovernmentUsWeatherBulletinDownloadFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_government_us_commodity_psd_data_fetcher(credentials=test_credentials):
    """Test GovernmentUsCommodityPsdDataFetcher."""

    params = {
        "report_id": "coffee_summary",
    }

    fetcher = GovernmentUsCommodityPsdDataFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

    time_series_params = {
        "report_id": "world_crop_production_summary",
        "commodity": "coffee",
        "attribute": ["exports"],
        "country": "BR",
        "start_year": 2025,
        "end_year": 2025,
        "aggregate_regions": False,
    }
    result = fetcher.test(time_series_params, credentials)
    assert result is None

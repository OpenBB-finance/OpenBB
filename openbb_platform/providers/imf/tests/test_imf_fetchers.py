"""IMF Fetcher Tests."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.consumer_price_index import ImfConsumerPriceIndexFetcher
from openbb_imf.models.direction_of_trade import ImfDirectionOfTradeFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoFetcher
from openbb_imf.models.maritime_chokepoint_volume import (
    ImfMaritimeChokePointVolumeFetcher,
)
from openbb_imf.models.port_info import ImfPortInfoFetcher
from openbb_imf.models.port_volume import ImfPortVolumeFetcher

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
def test_imf_consumer_price_index_fetcher(credentials=test_credentials):
    """Test the IMF ConsumerPriceIndex fetcher."""
    params = {
        "country": "JPN",
        "frequency": "quarter",
        "transform": "yoy",
        "expenditure": "total",
        "start_date": date(2024, 1, 1),
        "end_date": date(2025, 1, 1),
        "harmonized": False,
        "limit": None,
    }

    fetcher = ImfConsumerPriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_economic_indicators_fetcher(credentials=test_credentials):
    """Test the IMF EconomicIndicators fetcher."""
    params = {
        "country": "JPN",
        "frequency": "quarter",
        "symbol": "IL::RGV_REVS",
        "start_date": date(2023, 1, 1),
        "end_date": date(2024, 1, 1),
        "limit": None,
        "transform": None,
        "dimension_values": None,
    }

    fetcher = ImfEconomicIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


# The data for this request are local files, so we can't record them.
def test_imf_available_indicators_fetcher(credentials=test_credentials):
    """Test the IMF Available Indicators fetcher."""
    params = {"query": "gold+volume"}

    fetcher = ImfAvailableIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_direction_of_trade_fetcher(credentials=test_credentials):
    """Test the ImfDirectionOfTrade fetcher."""
    params = {
        "country": "USA",
        "counterpart": "G001,G998",
        "frequency": "annual",
        "direction": "exports",
        "start_date": date(2023, 1, 1),
        "end_date": date(2025, 1, 1),
        "limit": None,
    }

    fetcher = ImfDirectionOfTradeFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_port_info_fetcher(credentials=test_credentials):
    """Test the ImfPortInfo fetcher."""
    params = {"continent": "asia_pacific", "limit": 10}

    fetcher = ImfPortInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_port_volume_fetcher(credentials=test_credentials):
    """Test the ImfPortVolume fetcher."""
    params = {
        "port_code": "port1201",
        "start_date": date(year=2023, month=1, day=1),
        "end_date": date(year=2023, month=1, day=31),
    }

    fetcher = ImfPortVolumeFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_maritime_chokepoint_info_fetcher(credentials=test_credentials):
    """Test the ImfMaritimeChokePointInfo fetcher."""
    params = {}

    fetcher = ImfMaritimeChokePointInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_maritime_chokepoint_volume_fetcher(credentials=test_credentials):
    """Test the ImfMaritimeChokePointVolume fetcher."""
    params = {
        "chokepoint": "taiwan_strait",
        "start_date": date(year=2023, month=1, day=1),
        "end_date": date(year=2023, month=1, day=31),
    }

    fetcher = ImfMaritimeChokePointVolumeFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

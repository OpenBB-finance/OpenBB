"""IMF Fetcher Tests."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.balance_of_payments import ImfBalanceOfPaymentsFetcher
from openbb_imf.models.consumer_price_index import ImfConsumerPriceIndexFetcher
from openbb_imf.models.container_metrics import ImfContainerMetricsFetcher
from openbb_imf.models.country_activity import ImfCountryActivityFetcher
from openbb_imf.models.direction_of_trade import ImfDirectionOfTradeFetcher
from openbb_imf.models.disruption_events import ImfDisruptionEventsFetcher
from openbb_imf.models.disruption_sankey import ImfDisruptionSankeyFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoFetcher
from openbb_imf.models.maritime_chokepoint_volume import (
    ImfMaritimeChokePointVolumeFetcher,
)
from openbb_imf.models.monthly_trade import ImfMonthlyTradeFetcher
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
        "decode_compressed_response": True,
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


def test_imf_available_indicators_fetcher(credentials=test_credentials):
    """Test the IMF Available Indicators fetcher.

    The IMF SDMX catalog references a handful of codelists
    (``CL_NA_MAIN_REF_SECTOR``, ``CL_NA_MAIN_EXPENDITURE``,
    ``CL_GS_LI_GS_MS``, ``CL_SDG_COMPOSITE_BREAKDOWN``) that aren't
    published as standalone resources and one dataflow (``FFS``) with
    no clear indicator dimension; the fetcher warns on these by design.
    """
    import warnings as _warnings

    from openbb_core.app.model.abstract.warning import OpenBBWarning

    params = {"query": "gold+volume"}

    fetcher = ImfAvailableIndicatorsFetcher()
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", OpenBBWarning)
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


@pytest.mark.record_http
def test_imf_balance_of_payments_fetcher(credentials=test_credentials):
    """Test the ImfBalanceOfPayments fetcher."""
    params = {
        "country": "JPN",
        "frequency": "quarterly",
        "start_date": date(2023, 1, 1),
        "end_date": date(2024, 1, 1),
    }

    fetcher = ImfBalanceOfPaymentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_container_metrics_fetcher(credentials=test_credentials):
    """Test the ImfContainerMetrics fetcher."""
    params = {
        "metric": "portcalls",
        "port_ids": "TOP10",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
    }

    fetcher = ImfContainerMetricsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_country_activity_fetcher(credentials=test_credentials):
    """Test the ImfCountryActivity fetcher."""
    params = {
        "country_code": "USA",
        "metric": "portcalls",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }

    fetcher = ImfCountryActivityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_disruption_events_fetcher(credentials=test_credentials):
    """Test the ImfDisruptionEvents fetcher."""
    params = {"alertlevel": "ALL", "active_only": False}

    fetcher = ImfDisruptionEventsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_disruption_sankey_fetcher(credentials=test_credentials):
    """Test the ImfDisruptionSankey fetcher."""
    params = {"event_id": "1001234"}

    fetcher = ImfDisruptionSankeyFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_imf_monthly_trade_fetcher(credentials=test_credentials):
    """Test the ImfMonthlyTrade fetcher."""
    params = {
        "code": "USA",
        "metric": "trade_value",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
    }

    fetcher = ImfMonthlyTradeFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

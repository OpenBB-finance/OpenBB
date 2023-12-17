import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_oecd.models.composite_leading_indicator import (
    OECDCompositeLeadingIndicatorFetcher,
)
from openbb_oecd.models.customer_confidence_index import (
    OECDConsumerConfidenceIndexFetcher,
)
from openbb_oecd.models.gdp_forecast import OECDGdpForecastFetcher
from openbb_oecd.models.gdp_nominal import OECDGdpNominalFetcher
from openbb_oecd.models.gdp_real import OECDGdpRealFetcher
from openbb_oecd.models.ppi import OECDProducerPriceIndexFetcher
from openbb_oecd.models.unemployment import OECDUnemploymentFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_oecd_nominal_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGdpNominalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_real_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }
    fetcher = OECDGdpRealFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_forecast_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGdpForecastFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_unemployment_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDUnemploymentFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_producer_price_index_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDProducerPriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_consumer_confidence_index_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDConsumerConfidenceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_composite_leading_indicator_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDCompositeLeadingIndicatorFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

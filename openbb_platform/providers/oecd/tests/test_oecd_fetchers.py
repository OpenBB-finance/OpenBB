"""Test the OECD fetchers."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_oecd.models.composite_leading_indicator import (
    OECDCompositeLeadingIndicatorFetcher,
)
from openbb_oecd.models.consumer_price_index import OECDCPIFetcher
from openbb_oecd.models.country_interest_rates import OecdCountryInterestRatesFetcher
from openbb_oecd.models.gdp_forecast import OECDGdpForecastFetcher
from openbb_oecd.models.gdp_nominal import OECDGdpNominalFetcher
from openbb_oecd.models.gdp_real import OECDGdpRealFetcher
from openbb_oecd.models.house_price_index import OECDHousePriceIndexFetcher
from openbb_oecd.models.share_price_index import OECDSharePriceIndexFetcher
from openbb_oecd.models.unemployment import OECDUnemploymentFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_oecd_cpi_fetcher(credentials=test_credentials):
    """Test the OECD CPI fetcher."""
    params = {
        "country": "united_kingdom",
        "frequency": "annual",
    }

    fetcher = OECDCPIFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_nominal_gdp_fetcher(credentials=test_credentials):
    """Test the OECD Nominal GDP fetcher."""
    params = {
        "country": "united_states",
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGdpNominalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_real_gdp_fetcher(credentials=test_credentials):
    """Test the OECD Real GDP fetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2024, 1, 1),
        "country": "united_states",
    }
    fetcher = OECDGdpRealFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_gdp_forecast_fetcher(credentials=test_credentials):
    """Test the OECD GDP Forecast fetcher."""
    params = {
        "country": "united_states",
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2024, 1, 1),
    }

    fetcher = OECDGdpForecastFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_unemployment_fetcher(credentials=test_credentials):
    """Test the OECD Unemployment Rate fetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDUnemploymentFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_composite_leading_indicator_fetcher(credentials=test_credentials):
    """Test the OECD Composite Leading Indicator fetcher."""
    params = {
        "country": "G20",
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDCompositeLeadingIndicatorFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_share_price_index_fetcher(credentials=test_credentials):
    """Test the OECD Share Price Index fetcher."""
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2024, 4, 1),
        "country": "united_kingdom",
    }

    fetcher = OECDSharePriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_house_price_index_fetcher(credentials=test_credentials):
    """Test the OECD House Price Index fetcher."""
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2024, 4, 1),
        "country": "united_kingdom",
    }

    fetcher = OECDHousePriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_country_interest_rates_fetcher(credentials=test_credentials):
    """Test the OECD Country Interest Rates fetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2024, 1, 1),
        "country": "united_kingdom",
        "duration": "long",
        "frequency": "monthly",
    }

    fetcher = OecdCountryInterestRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

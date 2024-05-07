""" Test EconDB Fetchers. """

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_econdb.models.available_indicators import EconDbAvailableIndicatorsFetcher
from openbb_econdb.models.country_profile import EconDbCountryProfileFetcher
from openbb_econdb.models.economic_indicators import EconDbEconomicIndicatorsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_econdb_available_indicators_fetcher(credentials=test_credentials):
    """Test EconDB Available Indicators Fetcher."""
    params = {"use_cache": False}

    fetcher = EconDbAvailableIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_econdb_country_profile_fetcher(credentials=test_credentials):
    """Test EconDB Country Profile Fetcher."""
    params = {"country": "us", "latest": True, "use_cache": False}

    fetcher = EconDbCountryProfileFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_econdb_economic_indicators_fetcher(credentials=test_credentials):
    """Test EconDB Economic Indicators Fetcher."""
    params = {
        "country": "us",
        "symbol": "GDP",
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2024, 1, 1),
        "use_cache": False,
    }

    fetcher = EconDbEconomicIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_econdb_economic_indicators_main_fetcher(credentials=test_credentials):
    """Test EconDB Economic Indicators Fetcher with main."""
    params = {
        "symbol": "main",
        "country": "jp",
        "start_date": datetime.date(2022, 1, 1),
        "end_date": datetime.date(2024, 4, 1),
        "transform": None,
        "frequency": "quarter",
        "use_cache": False,
    }

    fetcher = EconDbEconomicIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

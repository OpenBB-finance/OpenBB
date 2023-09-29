import pytest
from openbb_blackrock.models.etf_countries import BlackrockEtfCountriesFetcher
from openbb_blackrock.models.etf_holdings import BlackrockEtfHoldingsFetcher
from openbb_blackrock.models.etf_info import BlackrockEtfInfoFetcher
from openbb_blackrock.models.etf_search import BlackrockEtfSearchFetcher
from openbb_blackrock.models.etf_sectors import BlackrockEtfSectorsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.dict()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr(record=True)
def test_blackrock_etf_countries_fetcher(credentials=test_credentials):
    params = {"symbol": "GOVT"}

    fetcher = BlackrockEtfCountriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.vcr(record=True)
def test_blackrock_etf_holdings_fetcher(credentials=test_credentials):
    params = {"symbol": "GOVZ"}

    fetcher = BlackrockEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.vcr(record=True)
def test_blackrock_etf_info_fetcher(credentials=test_credentials):
    params = {"symbol": "GOVT"}

    fetcher = BlackrockEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.vcr(record=True)
def test_blackrock_etf_search_fetcher(credentials=test_credentials):
    params = {"query": "Treasury"}

    fetcher = BlackrockEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.vcr(record=True)
def test_blackrock_etf_sectors_fetcher(credentials=test_credentials):
    params = {"symbol": "IGOV"}

    fetcher = BlackrockEtfSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

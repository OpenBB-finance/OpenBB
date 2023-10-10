import pytest
from openbb_bmo.models.etf_countries import BmoEtfCountriesFetcher
from openbb_bmo.models.etf_historical_nav import BmoEtfHistoricalNavFetcher
from openbb_bmo.models.etf_holdings import BmoEtfHoldingsFetcher
from openbb_bmo.models.etf_info import BmoEtfInfoFetcher
from openbb_bmo.models.etf_search import BmoEtfSearchFetcher
from openbb_bmo.models.etf_sectors import BmoEtfSectorsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.dict()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


@pytest.mark.record_http
def test_bmo_etf_search_fetcher(credentials=test_credentials):
    params = {"query": "equity"}

    fetcher = BmoEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_bmo_etf_countries_fetcher(credentials=test_credentials):
    params = {"symbol": "ZEQT"}

    fetcher = BmoEtfCountriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_bmo_etf_sectors_fetcher(credentials=test_credentials):
    params = {"symbol": "BGIF"}  #

    fetcher = BmoEtfSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_bmo_etf_holdings_fetcher(credentials=test_credentials):
    params = {"symbol": "ZGSB"}

    fetcher = BmoEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_bmo_etf_historical_nav_fetcher(credentials=test_credentials):
    params = {"symbol": "ZSP"}

    fetcher = BmoEtfHistoricalNavFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_bmo_etf_info_fetcher(credentials=test_credentials):
    params = {"symbol": "ZMID"}

    fetcher = BmoEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

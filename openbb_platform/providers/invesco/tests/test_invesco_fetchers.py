import pytest
from openbb_core.app.service.user_service import UserService
from openbb_invesco.models.etf_historical_nav import InvescoEtfHistoricalNavFetcher
from openbb_invesco.models.etf_holdings import InvescoEtfHoldingsFetcher
from openbb_invesco.models.etf_search import InvescoEtfSearchFetcher

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
def test_invesco_etf_search_fetcher(credentials=test_credentials):
    params = {"query": "equal weight", "options": "True", "short": "False"}

    fetcher = InvescoEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_invesco_etf_holdings_fetcher(credentials=test_credentials):
    params = {"symbol": "QQQ"}

    fetcher = InvescoEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_invesco_etf_historical_nav_fetcher(credentials=test_credentials):
    params = {"symbol": "QQQ"}

    fetcher = InvescoEtfHistoricalNavFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

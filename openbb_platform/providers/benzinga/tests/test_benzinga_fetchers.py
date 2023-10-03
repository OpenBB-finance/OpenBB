import pytest
from openbb_benzinga.models.global_news import BenzingaGlobalNewsFetcher
from openbb_benzinga.models.stock_news import BenzingaStockNewsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.dict()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_benzinga_global_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = BenzingaGlobalNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_benzinga_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = BenzingaStockNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

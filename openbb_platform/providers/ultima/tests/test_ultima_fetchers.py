import pytest
from openbb_core.app.service.user_service import UserService
from openbb_ultima.models.stock_news import UltimaStockNewsFetcher

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
def test_ultima_stock_news_fetcher(credentials={}):
    params = {"symbols": "AAPL, MSFT"}

    fetcher = UltimaStockNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

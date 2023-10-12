import pytest
from openbb_core.app.service.user_service import UserService
from openbb_sec.models.stock_ftd import SecStockFtdFetcher

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
def test_sec_ftd_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = SecStockFtdFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

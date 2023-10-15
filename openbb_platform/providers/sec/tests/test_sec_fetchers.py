import pytest
from openbb_core.app.service.user_service import UserService
from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
from openbb_sec.models.stock_ftd import SecStockFtdFetcher
from openbb_sec.models.stock_search import SecStockSearchFetcher

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
def test_sec_stock_ftd_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = SecStockFtdFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_stock_search_fetcher(credentials=test_credentials):
    params = {"query": "trust", "use_cache": False}

    fetcher = SecStockSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_company_filings_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "type": "10-K", "use_cache": False}

    fetcher = SecCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

import pytest
from openbb import obb
from openbb_quandl.models.cot import QuandlCotFetcher
from openbb_quandl.models.cot_search import QuandlCotSearchFetcher
from openbb_quandl.models.sp500_multiples import QuandlSP500MultiplesFetcher

test_credentials = obb.user.credentials.__dict__


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_quandl_sp500_multiples_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlSP500MultiplesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_quandl_cot_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlCotFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_quandl_cot_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = QuandlCotSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

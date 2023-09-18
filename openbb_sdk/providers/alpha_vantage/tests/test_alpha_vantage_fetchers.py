import pytest
from openbb import obb
from openbb_alpha_vantage.models.stock_historical import AVStockHistoricalFetcher

test_credentials = obb.user.credentials.__dict__


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_av_stock_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = AVStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

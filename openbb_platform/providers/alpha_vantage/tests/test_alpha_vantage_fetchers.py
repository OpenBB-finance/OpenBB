import pytest
from openbb_alpha_vantage.models.stock_historical import AVStockHistoricalFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.skip(reason="This is a premium endpoint.")
def test_av_stock_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = AVStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

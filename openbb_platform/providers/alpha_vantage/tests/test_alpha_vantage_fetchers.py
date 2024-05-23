"""Test the Alpha Vantage fetchers."""

from datetime import date

import pytest
from openbb_alpha_vantage.models.equity_historical import AVEquityHistoricalFetcher
from openbb_alpha_vantage.models.historical_eps import AVHistoricalEpsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_av_equity_historical_fetcher(credentials=test_credentials):
    """Test the Alpha Vantage Equity Historical fetcher."""
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "15m",
    }

    fetcher = AVEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_av_historical_eps_fetcher(credentials=test_credentials):
    """Test the Alpha Vantage Historical Earnings fetcher."""
    params = {"symbol": "AAPL,MSFT", "period": "quarter", "limit": 4}

    fetcher = AVHistoricalEpsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

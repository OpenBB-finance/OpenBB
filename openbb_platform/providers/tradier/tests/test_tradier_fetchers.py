"""Tradier Fetchers Tests."""

from datetime import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tradier.models.equity_historical import TradierEquityHistoricalFetcher
from openbb_tradier.models.equity_quote import TradierEquityQuoteFetcher
from openbb_tradier.models.equity_search import TradierEquitySearchFetcher
from openbb_tradier.models.options_chains import TradierOptionsChainsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [],
    }


@pytest.mark.record_http
def test_tradier_equity_historical_fetcher(credentials=test_credentials):
    """Test the Tradier Equity Historical fetcher."""
    params = {
        "start_date": datetime(2024, 2, 1).date(),
        "end_date": datetime(2024, 2, 29).date(),
        "symbol": "AAPL",
        "interval": "1d",
    }

    fetcher = TradierEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tradier_equity_search_fetcher(credentials=test_credentials):
    """Test the Tradier Equity Search fetcher."""
    params = {
        "query": "brookfield",
        "is_symbol": False,
    }

    fetcher = TradierEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tradier_equity_quote_fetcher(credentials=test_credentials):
    """Test the Tradier Equity Quote fetcher."""
    params = {"symbol": "SPY,SPY251219P00450000"}

    fetcher = TradierEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tradier_derivatives_options_chains_fetcher(credentials=test_credentials):
    """Test the Tradier Derivatives Options Chains fetcher."""

    params = {"symbol": "PLTR"}

    fetcher = TradierOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

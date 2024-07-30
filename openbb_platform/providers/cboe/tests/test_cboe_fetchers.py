"""CBOE Fetchers Tests.

The CBOE provider extension uses request caching.

For tests, set all functions using cache with the `use_cache` parameter to `False`.

When an item like a symbol directory is already cached, the cassette recorder does
not record the request event. If functions share a cached resource, it will only capture
the cassette for the first instance.

If an update of the cassettes is required the procedure is to delete the cache file and
then only run the single test which needs to be recorded.
"""

from datetime import date

import pytest
from openbb_cboe.models.available_indices import CboeAvailableIndicesFetcher
from openbb_cboe.models.equity_historical import CboeEquityHistoricalFetcher
from openbb_cboe.models.equity_quote import CboeEquityQuoteFetcher
from openbb_cboe.models.equity_search import CboeEquitySearchFetcher
from openbb_cboe.models.futures_curve import CboeFuturesCurveFetcher
from openbb_cboe.models.index_constituents import CboeIndexConstituentsFetcher
from openbb_cboe.models.index_historical import CboeIndexHistoricalFetcher
from openbb_cboe.models.index_search import CboeIndexSearchFetcher
from openbb_cboe.models.index_snapshots import CboeIndexSnapshotsFetcher
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
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
            None,
        ],
    }


@pytest.mark.record_http
def test_cboe_index_historical_fetcher(credentials=test_credentials):
    """Test Cboe index historical fetcher."""
    params = {"symbol": "AAVE10RP", "use_cache": False}

    fetcher = CboeIndexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_constituents_fetcher(credentials=test_credentials):
    """Test Cboe index constituents fetcher."""
    params = {"symbol": "BUK100P"}

    fetcher = CboeIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_search_fetcher(credentials=test_credentials):
    """Test Cboe index search fetcher."""
    params = {"query": "uk", "use_cache": False}

    fetcher = CboeIndexSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_equity_historical_fetcher(credentials=test_credentials):
    """Test Cboe equity historical fetcher."""
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
        "use_cache": False,
    }

    fetcher = CboeEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_available_indices_fetcher(credentials=test_credentials):
    """Test Cboe available indices fetcher."""
    params = {"use_cache": False}

    fetcher = CboeAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_options_chains_fetcher(credentials=test_credentials):
    """Test Cboe options chains fetcher."""

    params = {"symbol": "AAPL", "use_cache": False}

    fetcher = CboeOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_equity_search_fetcher(credentials=test_credentials):
    """Test Cboe equity search fetcher."""
    params = {"query": "ETF", "use_cache": False}

    fetcher = CboeEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_equity_quote_fetcher(credentials=test_credentials):
    """Test Cboe equity quote fetcher."""
    params = {"symbol": "AAPL", "use_cache": False}

    fetcher = CboeEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_futures_curve_fetcher(credentials=test_credentials):
    """Test Cboe futures curve fetcher."""
    params = {"symbol": "VX_EOD", "date": "2024-06-27", "use_cache": False}

    fetcher = CboeFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_snapshots_fetcher(credentials=test_credentials):
    """Test Cboe index snapshots fetcher."""
    params = {"region": "eu"}

    fetcher = CboeIndexSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

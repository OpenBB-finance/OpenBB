"""CBOE Fetchers Tests.

The CBOE provider extension uses request caching.
So, when an item like a symbol directory is already cached, the cassette recorder does
not record the request event. If functions share a cached resource, it will only capture
the cassette for the first instance.

If an update of the cassettes is required the procedure is to delete the cache file and
then only run the single test which needs to be recorded.
"""
from datetime import date

import pytest
from openbb_cboe.models.available_indices import CboeAvailableIndicesFetcher
from openbb_cboe.models.equity_historical import CboeEquityHistoricalFetcher
from openbb_cboe.models.equity_info import CboeEquityInfoFetcher
from openbb_cboe.models.equity_search import CboeEquitySearchFetcher
from openbb_cboe.models.european_index_constituents import (
    CboeEuropeanIndexConstituentsFetcher,
)
from openbb_cboe.models.european_indices import (
    CboeEuropeanIndicesFetcher,
)
from openbb_cboe.models.futures_curve import CboeFuturesCurveFetcher
from openbb_cboe.models.index_search import CboeIndexSearchFetcher
from openbb_cboe.models.index_snapshots import CboeIndexSnapshotsFetcher
from openbb_cboe.models.market_indices import (
    CboeMarketIndicesFetcher,
)
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.mark.record_http
def test_cboe_available_indices_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeIndexSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_options_chains_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = CboeOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


@pytest.mark.record_http
def test_cboe_equity_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_equity_historical_fetcher(credentials=test_credentials):
    params = params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = CboeEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_equity_info_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = CboeEquityInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_futures_curve_fetcher(credentials=test_credentials):
    params = {"symbol": "VX"}

    fetcher = CboeFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_european_index_constituents_fetcher(credentials=test_credentials):
    params = {"symbol": "BUKBUS"}

    fetcher = CboeEuropeanIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_european_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BUKBUS",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = CboeEuropeanIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_market_indices_fetcher(credentials=test_credentials):
    params = {"symbol": "AAVE10RP"}

    fetcher = CboeMarketIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_snapshots_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeIndexSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

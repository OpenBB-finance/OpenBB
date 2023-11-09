from datetime import date

import pytest
from openbb_cboe.models.available_indices import CboeAvailableIndicesFetcher
from openbb_cboe.models.equity_search import CboeEquitySearchFetcher
from openbb_cboe.models.european_index_constituents import (
    CboeEuropeanIndexConstituentsFetcher,
)
from openbb_cboe.models.european_index_historical import (
    CboeEuropeanIndexHistoricalFetcher,
)
from openbb_cboe.models.futures_curve import CboeFuturesCurveFetcher
from openbb_cboe.models.index_search import CboeIndexSearchFetcher
from openbb_cboe.models.index_snapshots import CboeIndexSnapshotsFetcher
from openbb_cboe.models.major_indices_historical import (
    CboeMajorIndicesHistoricalFetcher,
)
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
from openbb_cboe.models.stock_historical import CboeStockHistoricalFetcher
from openbb_cboe.models.stock_info import CboeStockInfoFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


@pytest.mark.record_http
@pytest.mark.skip(reason="Needs to be fixed.")
def test_cboe_equity_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="Needs to be fixed.")
def test_cboe_options_chains_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = CboeOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_stock_historical_fetcher(credentials=test_credentials):
    params = params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = CboeStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_stock_info_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = CboeStockInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_futures_curve_fetcher(credentials=test_credentials):
    params = {"symbol": "VX"}

    fetcher = CboeFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="Can't record")
def test_cboe_available_indices_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_european_index_constituents_fetcher(credentials=test_credentials):
    params = {"symbol": "BUKBUS"}

    fetcher = CboeEuropeanIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_european_index_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BUKBUS",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = CboeEuropeanIndexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_major_indices_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "AAVE10RP"}

    fetcher = CboeMajorIndicesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="Can't record.")
def test_cboe_index_search_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeIndexSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cboe_index_snapshots_fetcher(credentials=test_credentials):
    params = {}

    fetcher = CboeIndexSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

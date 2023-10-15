from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.earnings_calendar import TmxEarningsCalendarFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher
from openbb_tmx.models.stock_info import TmxStockInfoFetcher
from openbb_tmx.models.stock_insider_activity import TmxStockInsiderActivityFetcher
from openbb_tmx.models.stock_news import TmxStockNewsFetcher
from openbb_tmx.models.stock_search import TmxStockSearchFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


@pytest.mark.record_http
def test_tmx_stock_insider_activity_fetcher(credentials=test_credentials):
    params = {"symbol": "CNQ"}

    fetcher = TmxStockInsiderActivityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "SU"}

    fetcher = TmxStockNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_stock_search_fetcher(credentials=test_credentials):
    params = {"query": "bmo"}

    fetcher = TmxStockSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_countries_fetcher(credentials=test_credentials):
    params = {"symbol": "BKCC,ENCC"}

    fetcher = TmxEtfCountriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_holdings_fetcher(credentials=test_credentials):
    params = {"symbol": "VDY"}

    fetcher = TmxEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_info_fetcher(credentials=test_credentials):
    params = {"symbol": "VAB,VCB,VEF,VEQT"}

    fetcher = TmxEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_search_fetcher(credentials=test_credentials):
    params = {"query": "Vanguard"}

    fetcher = TmxEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_sectors_fetcher(credentials=test_credentials):
    params = {"symbol": "XIU,XIC,VCN,VCNS"}

    fetcher = TmxEtfSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_historical_dividends_fetcher(credentials=test_credentials):
    params = {"symbol": "RY"}

    fetcher = TmxHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_company_filings_fetcher(credentials=test_credentials):
    params = {"symbol": "CNQ"}

    fetcher = TmxCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_price_target_consensus_fetcher(credentials=test_credentials):
    params = {"symbol": "RY"}

    fetcher = TmxPriceTargetConsensusFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_stock_info_fetcher(credentials=test_credentials):
    params = {"symbol": "RY,NTR"}

    fetcher = TmxStockInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_available_indices_fetcher(credentials=test_credentials):
    params = {}

    fetcher = TmxAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_earnings_calendar_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 9, 1), "end_date": date(2023, 9, 30)}

    fetcher = TmxEarningsCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_index_constituents_fetcher(credentials=test_credentials):
    params = {"symbol": "tsx"}

    fetcher = TmxIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

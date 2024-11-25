"""TMX fetchers tests."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.bond_prices import TmxBondPricesFetcher
from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.company_news import TmxCompanyNewsFetcher
from openbb_tmx.models.equity_historical import TmxEquityHistoricalFetcher
from openbb_tmx.models.equity_profile import TmxEquityProfileFetcher
from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
from openbb_tmx.models.equity_search import TmxEquitySearchFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.gainers import TmxGainersFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.index_sectors import TmxIndexSectorsFetcher
from openbb_tmx.models.index_snapshots import TmxIndexSnapshotsFetcher
from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher
from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher
from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump()


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
def test_tmx_equity_profile_fetcher(credentials=test_credentials):
    """Test equity profile fetcher."""
    params = {"symbol": "RY,NTR"}

    fetcher = TmxEquityProfileFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_equity_search_fetcher(credentials=test_credentials):
    """Test equity search fetcher."""
    params = {"query": "gold", "use_cache": False}

    fetcher = TmxEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_available_indices_fetcher(credentials=test_credentials):
    """Test available indices fetcher."""
    params = {"use_cache": False}

    fetcher = TmxAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_calendar_earnings_fetcher(credentials=test_credentials):
    """Test calendar earnings fetcher."""
    params = {"start_date": date(2023, 1, 2), "end_date": date(2023, 1, 31)}

    fetcher = TmxCalendarEarningsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_company_filings_fetcher(credentials=test_credentials):
    """Test company filings fetcher."""
    params = {
        "symbol": "SHOP",
        "start_date": date(2023, 6, 30),
        "end_date": date(2023, 9, 30),
    }

    fetcher = TmxCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_company_news_fetcher(credentials=test_credentials):
    """Test company news fetcher."""
    params = {"symbol": "SHOP", "limit": 5}

    fetcher = TmxCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_equity_historical_fetcher(credentials=test_credentials):
    """Test equity historical fetcher."""
    params = {
        "symbol": "SHOP",
        "start_date": date(2022, 1, 1),
        "end_date": date(2023, 1, 1),
    }

    fetcher = TmxEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_equity_quote_fetcher(credentials=test_credentials):
    """Test equity quote fetcher."""
    params = {"symbol": "SHOP"}

    fetcher = TmxEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_countries_fetcher(credentials=test_credentials):
    """Test ETF countries fetcher."""
    params = {"symbol": "HXX", "use_cache": False}

    fetcher = TmxEtfCountriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_holdings_fetcher(credentials=test_credentials):
    """Test ETF holdings fetcher."""
    params = {"symbol": "XIU", "use_cache": False}

    fetcher = TmxEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_info_fetcher(credentials=test_credentials):
    """Test ETF info fetcher."""
    params = {"symbol": "XIU", "use_cache": False}

    fetcher = TmxEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_search_fetcher(credentials=test_credentials):
    """Test ETF search fetcher."""
    params = {"query": "sector", "use_cache": False}

    fetcher = TmxEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_etf_sectors_fetcher(credentials=test_credentials):
    """Test ETF sectors fetcher."""
    params = {"symbol": "XIU", "use_cache": False}

    fetcher = TmxEtfSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_gainers_fetcher(credentials=test_credentials):
    """Test gainers fetcher."""
    params = {}

    fetcher = TmxGainersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_historical_dividends_fetcher(credentials=test_credentials):
    """Test historical dividends fetcher."""
    params = {"symbol": "TD"}

    fetcher = TmxHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_index_constituents_fetcher(credentials=test_credentials):
    """Test index constituents fetcher."""
    params = {"symbol": "^TX60", "use_cache": False}

    fetcher = TmxIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_index_sectors_fetcher(credentials=test_credentials):
    """Test index sectors fetcher."""
    params = {"symbol": "^TSX", "use_cache": False}

    fetcher = TmxIndexSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_index_snapshots_fetcher(credentials=test_credentials):
    """Test index snapshots fetcher."""
    params = {"use_cache": False}

    fetcher = TmxIndexSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_insider_trading_fetcher(credentials=test_credentials):
    """Test insider trading fetcher."""
    params = {"symbol": "SHOP", "summary": False}

    fetcher = TmxInsiderTradingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_options_chains_fetcher(credentials=test_credentials):
    """Test options chains fetcher."""

    params = {"symbol": "SHOP", "use_cache": False, "date": date(2023, 9, 15)}

    fetcher = TmxOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_price_target_consensus_fetcher(credentials=test_credentials):
    """Test price target consensus fetcher."""
    params = {"symbol": "SHOP"}

    fetcher = TmxPriceTargetConsensusFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_treasury_prices_fetcher(credentials=test_credentials):
    """Test treasury prices fetcher."""
    params = {"govt_type": "federal", "use_cache": False}

    fetcher = TmxTreasuryPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tmx_bond_prices_fetcher(credentials=test_credentials):
    """Test bond prices fetcher."""
    params = {"use_cache": False, "coupon_rate_min": 4}

    fetcher = TmxBondPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

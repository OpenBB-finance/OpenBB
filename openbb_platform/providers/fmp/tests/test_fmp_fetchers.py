"""Unit tests for FMP provider modules."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fmp.models.analyst_estimates import FMPAnalystEstimatesFetcher
from openbb_fmp.models.available_indices import FMPAvailableIndicesFetcher
from openbb_fmp.models.balance_sheet import FMPBalanceSheetFetcher
from openbb_fmp.models.balance_sheet_growth import FMPBalanceSheetGrowthFetcher
from openbb_fmp.models.calendar_dividend import FMPCalendarDividendFetcher
from openbb_fmp.models.calendar_earnings import FMPCalendarEarningsFetcher
from openbb_fmp.models.calendar_splits import FMPCalendarSplitsFetcher
from openbb_fmp.models.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.models.cash_flow_growth import FMPCashFlowStatementGrowthFetcher
from openbb_fmp.models.company_filings import FMPCompanyFilingsFetcher
from openbb_fmp.models.company_news import FMPCompanyNewsFetcher
from openbb_fmp.models.company_overview import FMPCompanyOverviewFetcher
from openbb_fmp.models.crypto_historical import FMPCryptoHistoricalFetcher
from openbb_fmp.models.crypto_search import FMPCryptoSearchFetcher
from openbb_fmp.models.currency_historical import FMPCurrencyHistoricalFetcher
from openbb_fmp.models.currency_pairs import FMPCurrencyPairsFetcher
from openbb_fmp.models.discovery_filings import FMPDiscoveryFilingsFetcher
from openbb_fmp.models.earnings_call_transcript import FMPEarningsCallTranscriptFetcher
from openbb_fmp.models.economic_calendar import FMPEconomicCalendarFetcher
from openbb_fmp.models.equity_historical import FMPEquityHistoricalFetcher
from openbb_fmp.models.equity_ownership import FMPEquityOwnershipFetcher
from openbb_fmp.models.equity_peers import FMPEquityPeersFetcher
from openbb_fmp.models.equity_quote import FMPEquityQuoteFetcher
from openbb_fmp.models.equity_screener import FMPEquityScreenerFetcher
from openbb_fmp.models.equity_valuation_multiples import (
    FMPEquityValuationMultiplesFetcher,
)
from openbb_fmp.models.etf_countries import FMPEtfCountriesFetcher
from openbb_fmp.models.etf_holdings import FMPEtfHoldingsFetcher
from openbb_fmp.models.etf_holdings_date import FMPEtfHoldingsDateFetcher
from openbb_fmp.models.etf_holdings_performance import FMPEtfHoldingsPerformanceFetcher
from openbb_fmp.models.etf_info import FMPEtfInfoFetcher
from openbb_fmp.models.etf_search import FMPEtfSearchFetcher
from openbb_fmp.models.etf_sectors import FMPEtfSectorsFetcher
from openbb_fmp.models.executive_compensation import FMPExecutiveCompensationFetcher
from openbb_fmp.models.financial_ratios import FMPFinancialRatiosFetcher
from openbb_fmp.models.historical_dividends import FMPHistoricalDividendsFetcher
from openbb_fmp.models.historical_employees import FMPHistoricalEmployeesFetcher
from openbb_fmp.models.historical_eps import FMPHistoricalEpsFetcher
from openbb_fmp.models.historical_splits import FMPHistoricalSplitsFetcher
from openbb_fmp.models.income_statement import FMPIncomeStatementFetcher
from openbb_fmp.models.income_statement_growth import FMPIncomeStatementGrowthFetcher
from openbb_fmp.models.index_constituents import (
    FMPIndexConstituentsFetcher,
)
from openbb_fmp.models.insider_trading import FMPInsiderTradingFetcher
from openbb_fmp.models.institutional_ownership import FMPInstitutionalOwnershipFetcher
from openbb_fmp.models.key_executives import FMPKeyExecutivesFetcher
from openbb_fmp.models.key_metrics import FMPKeyMetricsFetcher
from openbb_fmp.models.market_indices import FMPMarketIndicesFetcher
from openbb_fmp.models.market_snapshots import FMPMarketSnapshotsFetcher
from openbb_fmp.models.price_performance import FMPPricePerformanceFetcher
from openbb_fmp.models.price_target import FMPPriceTargetFetcher
from openbb_fmp.models.price_target_consensus import FMPPriceTargetConsensusFetcher
from openbb_fmp.models.revenue_business_line import FMPRevenueBusinessLineFetcher
from openbb_fmp.models.revenue_geographic import FMPRevenueGeographicFetcher
from openbb_fmp.models.risk_premium import FMPRiskPremiumFetcher
from openbb_fmp.models.share_statistics import FMPShareStatisticsFetcher
from openbb_fmp.models.treasury_rates import FMPTreasuryRatesFetcher
from openbb_fmp.models.world_news import FMPWorldNewsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_fmp_company_filings_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "form_type": "10-K", "limit": 100}

    fetcher = FMPCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_crypto_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = FMPCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_currency_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = FMPCurrencyHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_market_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "^DJI",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = FMPMarketIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = FMPEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = FMPCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_balance_sheet_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_cash_flow_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_income_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_available_indices_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_key_executives_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPKeyExecutivesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_world_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_income_statement_growth_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPIncomeStatementGrowthFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_balance_sheet_growth_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPBalanceSheetGrowthFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_cash_flow_statement_growth_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPCashFlowStatementGrowthFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_share_statistics_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPShareStatisticsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_revenue_geographic_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPRevenueGeographicFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_revenue_business_line_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPRevenueBusinessLineFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_institutional_ownership_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPInstitutionalOwnershipFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_company_overview_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPCompanyOverviewFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_insider_trading_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPInsiderTradingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_ownership_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "date": date(2022, 12, 31)}

    fetcher = FMPEquityOwnershipFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_price_target_consensus_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPPriceTargetConsensusFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_price_target_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPPriceTargetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_analyst_estimates_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPAnalystEstimatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_historical_eps_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPHistoricalEpsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_earnings_call_transcript_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "year": 2020}

    fetcher = FMPEarningsCallTranscriptFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_historical_splits_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPHistoricalSplitsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_calendar_splits_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 1, 10)}

    fetcher = FMPCalendarSplitsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_historical_dividends_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_key_metrics_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPKeyMetricsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_treasury_rates_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FMPTreasuryRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_executive_compensation_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPExecutiveCompensationFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_currency_pairs_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPCurrencyPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_peers_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPEquityPeersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_valuation_multiples_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPEquityValuationMultiplesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_historical_employees_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPHistoricalEmployeesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_risk_premium_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPRiskPremiumFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_index_constituents_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPIndexConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_calendar_dividend_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 11, 6), "end_date": date(2023, 11, 10)}

    fetcher = FMPCalendarDividendFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_quote_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_equity_screener_fetcher(credentials=test_credentials):
    params = {"query": "midstream", "sector": "Energy", "beta_max": 0.5}

    fetcher = FMPEquityScreenerFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_financial_ratios_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPFinancialRatiosFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_economic_calendar_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_market_snapshots_fetcher(credentials=test_credentials):
    params = {"market": "LSE"}

    fetcher = FMPMarketSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_search_fetcher(credentials=test_credentials):
    params = {"query": "India"}

    fetcher = FMPEtfSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_info_fetcher(credentials=test_credentials):
    params = {"symbol": "IOO"}

    fetcher = FMPEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_sectors_fetcher(credentials=test_credentials):
    params = {"symbol": "IOO"}

    fetcher = FMPEtfSectorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_holdings_fetcher(credentials=test_credentials):
    params = {"symbol": "IOO", "date": date(2022, 12, 31)}

    fetcher = FMPEtfHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_holdings_date_fetcher(credentials=test_credentials):
    params = {"symbol": "IOO"}

    fetcher = FMPEtfHoldingsDateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_price_performance_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL,SPY,QQQ,MSFT,AMZN,GOOG"}

    fetcher = FMPPricePerformanceFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_countries_fetcher(credentials=test_credentials):
    params = {"symbol": "VTI,QQQ,VOO,IWM"}

    fetcher = FMPEtfCountriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_etf_holdings_performance_fetcher(credentials=test_credentials):
    params = {"symbol": "SILJ"}

    fetcher = FMPEtfHoldingsPerformanceFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_discovery_filings_fetcher(credentials=test_credentials):
    params = {
        "start_date": None,
        "end_date": None,
        "form_type": "8-K",
        "limit": 100,
        "is_done": None,
    }

    fetcher = FMPDiscoveryFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_crypto_search_fetcher(credentials=test_credentials):
    params = {"query": "asd"}

    fetcher = FMPCryptoSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_calendar_earnings_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    params = {
        "start_date": date(2023, 11, 6),
        "end_date": date(2023, 1, 10),
    }
    fetcher = FMPCalendarEarningsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

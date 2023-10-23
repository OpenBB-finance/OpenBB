from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fmp.models.analyst_estimates import FMPAnalystEstimatesFetcher
from openbb_fmp.models.available_indices import FMPAvailableIndicesFetcher
from openbb_fmp.models.balance_sheet import FMPBalanceSheetFetcher
from openbb_fmp.models.balance_sheet_growth import FMPBalanceSheetGrowthFetcher
from openbb_fmp.models.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.models.cash_flow_growth import FMPCashFlowStatementGrowthFetcher
from openbb_fmp.models.company_filings import FMPCompanyFilingsFetcher
from openbb_fmp.models.company_overview import FMPCompanyOverviewFetcher
from openbb_fmp.models.crypto_historical import FMPCryptoHistoricalFetcher
from openbb_fmp.models.dividend_calendar import FMPDividendCalendarFetcher
from openbb_fmp.models.earnings_calendar import FMPEarningsCalendarFetcher
from openbb_fmp.models.earnings_call_transcript import FMPEarningsCallTranscriptFetcher
from openbb_fmp.models.executive_compensation import FMPExecutiveCompensationFetcher
from openbb_fmp.models.financial_ratios import FMPFinancialRatiosFetcher
from openbb_fmp.models.forex_historical import FMPForexHistoricalFetcher
from openbb_fmp.models.forex_pairs import FMPForexPairsFetcher
from openbb_fmp.models.global_news import FMPGlobalNewsFetcher
from openbb_fmp.models.historical_dividends import FMPHistoricalDividendsFetcher
from openbb_fmp.models.historical_employees import FMPHistoricalEmployeesFetcher
from openbb_fmp.models.historical_stock_splits import FMPHistoricalStockSplitsFetcher
from openbb_fmp.models.income_statement import FMPIncomeStatementFetcher
from openbb_fmp.models.income_statement_growth import FMPIncomeStatementGrowthFetcher
from openbb_fmp.models.institutional_ownership import FMPInstitutionalOwnershipFetcher
from openbb_fmp.models.key_executives import FMPKeyExecutivesFetcher
from openbb_fmp.models.key_metrics import FMPKeyMetricsFetcher
from openbb_fmp.models.major_indices_constituents import (
    FMPMajorIndicesConstituentsFetcher,
)
from openbb_fmp.models.major_indices_historical import FMPMajorIndicesHistoricalFetcher
from openbb_fmp.models.price_target import FMPPriceTargetFetcher
from openbb_fmp.models.price_target_consensus import FMPPriceTargetConsensusFetcher
from openbb_fmp.models.revenue_business_line import FMPRevenueBusinessLineFetcher
from openbb_fmp.models.revenue_geographic import FMPRevenueGeographicFetcher
from openbb_fmp.models.risk_premium import FMPRiskPremiumFetcher
from openbb_fmp.models.share_statistics import FMPShareStatisticsFetcher
from openbb_fmp.models.stock_historical import FMPStockHistoricalFetcher
from openbb_fmp.models.stock_insider_trading import FMPStockInsiderTradingFetcher
from openbb_fmp.models.stock_multiples import FMPStockMultiplesFetcher
from openbb_fmp.models.stock_news import FMPStockNewsFetcher
from openbb_fmp.models.stock_ownership import FMPStockOwnershipFetcher
from openbb_fmp.models.stock_peers import FMPStockPeersFetcher
from openbb_fmp.models.stock_quote import FMPStockQuoteFetcher
from openbb_fmp.models.stock_splits import FMPStockSplitCalendarFetcher
from openbb_fmp.models.treasury_rates import FMPTreasuryRatesFetcher

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
    params = {"symbol": "AAPL", "limit": 100}

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
def test_fmp_forex_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = FMPForexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_major_indices_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "^DJI",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = FMPMajorIndicesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = FMPStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = FMPStockNewsFetcher()
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
def test_fmp_global_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPGlobalNewsFetcher()
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
def test_fmp_stock_insider_trading_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPStockInsiderTradingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_ownership_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "date": date(2022, 12, 31)}

    fetcher = FMPStockOwnershipFetcher()
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
def test_fmp_earnings_calendar_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPEarningsCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_earnings_call_transcript_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "year": 2020}

    fetcher = FMPEarningsCallTranscriptFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_historical_stock_splits_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPHistoricalStockSplitsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_split_calendar_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 1, 10)}

    fetcher = FMPStockSplitCalendarFetcher()
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
def test_fmp_forex_pairs_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPForexPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_peers_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPStockPeersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_multiples_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPStockMultiplesFetcher()
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
def test_fmp_major_indices_constituents_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FMPMajorIndicesConstituentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_dividend_calendar_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FMPDividendCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_stock_quote_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPStockQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fmp_financial_ratios_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FMPFinancialRatiosFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

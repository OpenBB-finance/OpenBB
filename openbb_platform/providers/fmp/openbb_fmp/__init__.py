"""FMP Provider Modules."""

from openbb_core.provider.abstract.provider import Provider
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
from openbb_fmp.models.index_constituents import FMPIndexConstituentsFetcher
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

fmp_provider = Provider(
    name="fmp",
    website="https://financialmodelingprep.com/",
    description="""Financial Modeling Prep is a new concept that informs you about
    stock market information (news, currencies, and stock prices).""",
    credentials=["api_key"],
    fetcher_dict={
        "AnalystEstimates": FMPAnalystEstimatesFetcher,
        "AvailableIndices": FMPAvailableIndicesFetcher,
        "BalanceSheet": FMPBalanceSheetFetcher,
        "BalanceSheetGrowth": FMPBalanceSheetGrowthFetcher,
        "CalendarDividend": FMPCalendarDividendFetcher,
        "CalendarEarnings": FMPCalendarEarningsFetcher,
        "CalendarSplits": FMPCalendarSplitsFetcher,
        "CashFlowStatement": FMPCashFlowStatementFetcher,
        "CashFlowStatementGrowth": FMPCashFlowStatementGrowthFetcher,
        "CompanyFilings": FMPCompanyFilingsFetcher,
        "CompanyNews": FMPCompanyNewsFetcher,
        "CompanyOverview": FMPCompanyOverviewFetcher,
        "CryptoHistorical": FMPCryptoHistoricalFetcher,
        "CryptoSearch": FMPCryptoSearchFetcher,
        "CurrencyHistorical": FMPCurrencyHistoricalFetcher,
        "CurrencyPairs": FMPCurrencyPairsFetcher,
        "DiscoveryFilings": FMPDiscoveryFilingsFetcher,
        "EarningsCallTranscript": FMPEarningsCallTranscriptFetcher,
        "EconomicCalendar": FMPEconomicCalendarFetcher,
        "EquityHistorical": FMPEquityHistoricalFetcher,
        "EquityOwnership": FMPEquityOwnershipFetcher,
        "EquityPeers": FMPEquityPeersFetcher,
        "EquityQuote": FMPEquityQuoteFetcher,
        "EquityScreener": FMPEquityScreenerFetcher,
        "EquityValuationMultiples": FMPEquityValuationMultiplesFetcher,
        "EtfCountries": FMPEtfCountriesFetcher,
        "EtfHoldings": FMPEtfHoldingsFetcher,
        "EtfHoldingsDate": FMPEtfHoldingsDateFetcher,
        "EtfHoldingsPerformance": FMPEtfHoldingsPerformanceFetcher,
        "EtfInfo": FMPEtfInfoFetcher,
        "EtfSearch": FMPEtfSearchFetcher,
        "EtfSectors": FMPEtfSectorsFetcher,
        "ExecutiveCompensation": FMPExecutiveCompensationFetcher,
        "FinancialRatios": FMPFinancialRatiosFetcher,
        "HistoricalDividends": FMPHistoricalDividendsFetcher,
        "HistoricalEmployees": FMPHistoricalEmployeesFetcher,
        "HistoricalEps": FMPHistoricalEpsFetcher,
        "HistoricalSplits": FMPHistoricalSplitsFetcher,
        "IncomeStatement": FMPIncomeStatementFetcher,
        "IncomeStatementGrowth": FMPIncomeStatementGrowthFetcher,
        "IndexConstituents": FMPIndexConstituentsFetcher,
        "InsiderTrading": FMPInsiderTradingFetcher,
        "InstitutionalOwnership": FMPInstitutionalOwnershipFetcher,
        "KeyExecutives": FMPKeyExecutivesFetcher,
        "KeyMetrics": FMPKeyMetricsFetcher,
        "MarketIndices": FMPMarketIndicesFetcher,
        "MarketSnapshots": FMPMarketSnapshotsFetcher,
        "PricePerformance": FMPPricePerformanceFetcher,
        "PriceTarget": FMPPriceTargetFetcher,
        "PriceTargetConsensus": FMPPriceTargetConsensusFetcher,
        "RevenueBusinessLine": FMPRevenueBusinessLineFetcher,
        "RevenueGeographic": FMPRevenueGeographicFetcher,
        "RiskPremium": FMPRiskPremiumFetcher,
        "ShareStatistics": FMPShareStatisticsFetcher,
        "TreasuryRates": FMPTreasuryRatesFetcher,
        "WorldNews": FMPWorldNewsFetcher,
    },
)

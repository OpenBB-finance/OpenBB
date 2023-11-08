"""FMP Provider module."""
from openbb_fmp.models.analyst_estimates import FMPAnalystEstimatesFetcher
from openbb_fmp.models.available_indices import FMPAvailableIndicesFetcher
from openbb_fmp.models.balance_sheet import FMPBalanceSheetFetcher
from openbb_fmp.models.balance_sheet_growth import FMPBalanceSheetGrowthFetcher
from openbb_fmp.models.calendar_dividend import FMPDividendCalendarFetcher
from openbb_fmp.models.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.models.cash_flow_growth import FMPCashFlowStatementGrowthFetcher
from openbb_fmp.models.company_filings import FMPCompanyFilingsFetcher
from openbb_fmp.models.company_news import FMPCompanyNewsFetcher
from openbb_fmp.models.company_overview import FMPCompanyOverviewFetcher
from openbb_fmp.models.crypto_historical import FMPCryptoHistoricalFetcher
from openbb_fmp.models.crypto_search import FMPCryptoSearchFetcher
from openbb_fmp.models.currency_historical import FMPCurrencyHistoricalFetcher
from openbb_fmp.models.currency_pairs import FMPCurrencyPairsFetcher
from openbb_fmp.models.disc_filings import FMPFilingsFetcher
from openbb_fmp.models.earnings_calendar import FMPEarningsCalendarFetcher
from openbb_fmp.models.earnings_call_transcript import FMPEarningsCallTranscriptFetcher
from openbb_fmp.models.economic_calendar import FMPEconomicCalendarFetcher
from openbb_fmp.models.etf_countries import FMPEtfCountriesFetcher
from openbb_fmp.models.etf_holdings import FMPEtfHoldingsFetcher
from openbb_fmp.models.etf_holdings_date import FMPEtfHoldingsDateFetcher
from openbb_fmp.models.etf_holdings_performance import FMPEtfHoldingsPerformanceFetcher
from openbb_fmp.models.etf_info import FMPEtfInfoFetcher
from openbb_fmp.models.etf_search import FMPEtfSearchFetcher
from openbb_fmp.models.etf_sectors import FMPEtfSectorsFetcher
from openbb_fmp.models.executive_compensation import FMPExecutiveCompensationFetcher
from openbb_fmp.models.financial_ratios import FMPFinancialRatiosFetcher
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
from openbb_fmp.models.market_snapshots import FMPMarketSnapshotsFetcher
from openbb_fmp.models.price_performance import FMPPricePerformanceFetcher
from openbb_fmp.models.price_target import FMPPriceTargetFetcher
from openbb_fmp.models.price_target_consensus import FMPPriceTargetConsensusFetcher
from openbb_fmp.models.revenue_business_line import FMPRevenueBusinessLineFetcher
from openbb_fmp.models.revenue_geographic import FMPRevenueGeographicFetcher
from openbb_fmp.models.risk_premium import FMPRiskPremiumFetcher
from openbb_fmp.models.share_statistics import FMPShareStatisticsFetcher
from openbb_fmp.models.stock_historical import FMPStockHistoricalFetcher
from openbb_fmp.models.stock_insider_trading import FMPStockInsiderTradingFetcher
from openbb_fmp.models.stock_multiples import FMPStockMultiplesFetcher
from openbb_fmp.models.stock_ownership import FMPStockOwnershipFetcher
from openbb_fmp.models.stock_peers import FMPStockPeersFetcher
from openbb_fmp.models.stock_quote import FMPStockQuoteFetcher
from openbb_fmp.models.stock_search import FMPStockSearchFetcher
from openbb_fmp.models.stock_splits import FMPStockSplitCalendarFetcher
from openbb_fmp.models.treasury_rates import FMPTreasuryRatesFetcher
from openbb_provider.abstract.provider import Provider

fmp_provider = Provider(
    name="fmp",
    website="https://financialmodelingprep.com/",
    description="""Financial Modeling Prep is a new concept that informs you about
    stock market information (news, currencies, and stock prices).""",
    required_credentials=["api_key"],
    fetcher_dict={
        "AnalystEstimates": FMPAnalystEstimatesFetcher,
        "AvailableIndices": FMPAvailableIndicesFetcher,
        "BalanceSheet": FMPBalanceSheetFetcher,
        "BalanceSheetGrowth": FMPBalanceSheetGrowthFetcher,
        "CalendarDividend": FMPDividendCalendarFetcher,
        "CashFlowStatement": FMPCashFlowStatementFetcher,
        "CashFlowStatementGrowth": FMPCashFlowStatementGrowthFetcher,
        "CompanyFilings": FMPCompanyFilingsFetcher,
        "CompanyNews": FMPCompanyNewsFetcher,
        "CompanyOverview": FMPCompanyOverviewFetcher,
        "CryptoHistorical": FMPCryptoHistoricalFetcher,
        "CryptoSearch": FMPCryptoSearchFetcher,
        "CurrencyHistorical": FMPCurrencyHistoricalFetcher,
        "CurrencyPairs": FMPCurrencyPairsFetcher,
        "DiscFilings": FMPFilingsFetcher,
        "EarningsCalendar": FMPEarningsCalendarFetcher,
        "EarningsCallTranscript": FMPEarningsCallTranscriptFetcher,
        "EconomicCalendar": FMPEconomicCalendarFetcher,
        "EtfCountries": FMPEtfCountriesFetcher,
        "EtfHoldings": FMPEtfHoldingsFetcher,
        "EtfHoldingsDate": FMPEtfHoldingsDateFetcher,
        "EtfHoldingsPerformance": FMPEtfHoldingsPerformanceFetcher,
        "EtfInfo": FMPEtfInfoFetcher,
        "EtfSearch": FMPEtfSearchFetcher,
        "EtfSectors": FMPEtfSectorsFetcher,
        "ExecutiveCompensation": FMPExecutiveCompensationFetcher,
        "FinancialRatios": FMPFinancialRatiosFetcher,
        "GlobalNews": FMPGlobalNewsFetcher,
        "HistoricalDividends": FMPHistoricalDividendsFetcher,
        "HistoricalEmployees": FMPHistoricalEmployeesFetcher,
        "HistoricalStockSplits": FMPHistoricalStockSplitsFetcher,
        "IncomeStatement": FMPIncomeStatementFetcher,
        "IncomeStatementGrowth": FMPIncomeStatementGrowthFetcher,
        "InstitutionalOwnership": FMPInstitutionalOwnershipFetcher,
        "KeyExecutives": FMPKeyExecutivesFetcher,
        "KeyMetrics": FMPKeyMetricsFetcher,
        "MajorIndicesConstituents": FMPMajorIndicesConstituentsFetcher,
        "MajorIndicesHistorical": FMPMajorIndicesHistoricalFetcher,
        "MarketSnapshots": FMPMarketSnapshotsFetcher,
        "PricePerformance": FMPPricePerformanceFetcher,
        "PriceTarget": FMPPriceTargetFetcher,
        "PriceTargetConsensus": FMPPriceTargetConsensusFetcher,
        "RevenueBusinessLine": FMPRevenueBusinessLineFetcher,
        "RevenueGeographic": FMPRevenueGeographicFetcher,
        "RiskPremium": FMPRiskPremiumFetcher,
        "ShareStatistics": FMPShareStatisticsFetcher,
        "StockHistorical": FMPStockHistoricalFetcher,
        "StockInsiderTrading": FMPStockInsiderTradingFetcher,
        "StockMultiples": FMPStockMultiplesFetcher,
        "StockOwnership": FMPStockOwnershipFetcher,
        "StockPeers": FMPStockPeersFetcher,
        "StockQuote": FMPStockQuoteFetcher,
        "StockSearch": FMPStockSearchFetcher,
        "StockSplitCalendar": FMPStockSplitCalendarFetcher,
        "TreasuryRates": FMPTreasuryRatesFetcher,
    },
)

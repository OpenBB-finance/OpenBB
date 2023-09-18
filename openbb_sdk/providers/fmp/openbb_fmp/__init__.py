"""FMP Provider module."""
from openbb_fmp.models.analyst_estimates import FMPAnalystEstimatesFetcher
from openbb_fmp.models.available_indices import FMPAvailableIndicesFetcher
from openbb_fmp.models.balance_sheet import FMPBalanceSheetFetcher
from openbb_fmp.models.balance_sheet_growth import FMPBalanceSheetGrowthFetcher
from openbb_fmp.models.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.models.cash_flow_growth import FMPCashFlowStatementGrowthFetcher
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
from openbb_fmp.models.sec_filings import FMPSECFilingsFetcher
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
from openbb_provider.abstract.provider import Provider

fmp_provider = Provider(
    name="fmp",
    website="https://financialmodelingprep.com/",
    description="""Financial Modeling Prep is a new concept that informs you about
    stock market information (news, currencies, and stock prices).""",
    required_credentials=["api_key"],
    fetcher_dict={
        "KeyExecutives": FMPKeyExecutivesFetcher,
        "StockHistorical": FMPStockHistoricalFetcher,
        "GlobalNews": FMPGlobalNewsFetcher,
        "StockNews": FMPStockNewsFetcher,
        "IncomeStatement": FMPIncomeStatementFetcher,
        "IncomeStatementGrowth": FMPIncomeStatementGrowthFetcher,
        "BalanceSheet": FMPBalanceSheetFetcher,
        "BalanceSheetGrowth": FMPBalanceSheetGrowthFetcher,
        "CashFlowStatement": FMPCashFlowStatementFetcher,
        "CashFlowStatementGrowth": FMPCashFlowStatementGrowthFetcher,
        "ShareStatistics": FMPShareStatisticsFetcher,
        "MajorIndicesHistorical": FMPMajorIndicesHistoricalFetcher,
        "RevenueGeographic": FMPRevenueGeographicFetcher,
        "RevenueBusinessLine": FMPRevenueBusinessLineFetcher,
        "InstitutionalOwnership": FMPInstitutionalOwnershipFetcher,
        "CompanyOverview": FMPCompanyOverviewFetcher,
        "StockInsiderTrading": FMPStockInsiderTradingFetcher,
        "StockOwnership": FMPStockOwnershipFetcher,
        "PriceTargetConsensus": FMPPriceTargetConsensusFetcher,
        "PriceTarget": FMPPriceTargetFetcher,
        "AnalystEstimates": FMPAnalystEstimatesFetcher,
        "EarningsCalendar": FMPEarningsCalendarFetcher,
        "EarningsCallTranscript": FMPEarningsCallTranscriptFetcher,
        "HistoricalStockSplits": FMPHistoricalStockSplitsFetcher,
        "StockSplitCalendar": FMPStockSplitCalendarFetcher,
        "HistoricalDividends": FMPHistoricalDividendsFetcher,
        "KeyMetrics": FMPKeyMetricsFetcher,
        "SECFilings": FMPSECFilingsFetcher,
        "TreasuryRates": FMPTreasuryRatesFetcher,
        "ExecutiveCompensation": FMPExecutiveCompensationFetcher,
        "CryptoHistorical": FMPCryptoHistoricalFetcher,
        "ForexHistorical": FMPForexHistoricalFetcher,
        "ForexPairs": FMPForexPairsFetcher,
        "StockPeers": FMPStockPeersFetcher,
        "StockMultiples": FMPStockMultiplesFetcher,
        "HistoricalEmployees": FMPHistoricalEmployeesFetcher,
        "AvailableIndices": FMPAvailableIndicesFetcher,
        "RiskPremium": FMPRiskPremiumFetcher,
        "MajorIndicesConstituents": FMPMajorIndicesConstituentsFetcher,
        "DividendCalendar": FMPDividendCalendarFetcher,
        "StockQuote": FMPStockQuoteFetcher,
        "FinancialRatios": FMPFinancialRatiosFetcher,
    },
)

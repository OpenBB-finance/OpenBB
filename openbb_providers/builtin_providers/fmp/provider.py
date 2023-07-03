"""FMP Provider module."""

# IMPORT STANDARD

# IMPORT THIRD-PARTY

# IMPORT INTERNAL
from openbb_provider.provider.abstract.provider import Provider, ProviderNameType

from builtin_providers.fmp.analyst_estimates import FMPAnalystEstimatesFetcher
from builtin_providers.fmp.balance_sheet import FMPBalanceSheetFetcher
from builtin_providers.fmp.cash_flow import FMPCashFlowStatementFetcher
from builtin_providers.fmp.company_profile import FMPCompanyProfileFetcher
from builtin_providers.fmp.crypto_eod import FMPCryptoEODFetcher
from builtin_providers.fmp.crypto_price import FMPCryptoPriceFetcher
from builtin_providers.fmp.earnings_calendar import FMPEarningsCalendarFetcher
from builtin_providers.fmp.earnings_call_transcript import (
    FMPEarningsCallTranscriptFetcher,
)
from builtin_providers.fmp.esg_risk_rating import FMPESGRiskRatingFetcher
from builtin_providers.fmp.esg_score import FMPESGScoreFetcher
from builtin_providers.fmp.esg_sector import FMPESGSectorFetcher
from builtin_providers.fmp.executive_compensation import FMPExecutiveCompensationFetcher
from builtin_providers.fmp.executives import FMPKeyExecutivesFetcher
from builtin_providers.fmp.forex_eod import FMPForexEODFetcher
from builtin_providers.fmp.forex_price import FMPForexPriceFetcher
from builtin_providers.fmp.global_news import FMPGlobalNewsFetcher
from builtin_providers.fmp.historical_dividends import FMPHistoricalDividendsFetcher
from builtin_providers.fmp.historical_stock_splits import (
    FMPHistoricalStockSplitsFetcher,
)
from builtin_providers.fmp.income_statement import FMPIncomeStatementFetcher
from builtin_providers.fmp.institutional_ownership import (
    FMPInstitutionalOwnershipFetcher,
)
from builtin_providers.fmp.key_metrics import FMPKeyMetricsFetcher
from builtin_providers.fmp.major_indices_eod import FMPMajorIndicesEODFetcher
from builtin_providers.fmp.major_indices_price import FMPMajorIndicesPriceFetcher
from builtin_providers.fmp.price_target import FMPPriceTargetFetcher
from builtin_providers.fmp.price_target_consensus import FMPPriceTargetConsensusFetcher
from builtin_providers.fmp.revenue_business_line import FMPRevenueBusinessLineFetcher
from builtin_providers.fmp.revenue_geographic import FMPRevenueGeographicFetcher
from builtin_providers.fmp.sec_filings import FMPSECFilingsFetcher
from builtin_providers.fmp.share_stats import FMPShareStatisticsFetcher
from builtin_providers.fmp.stock_eod import FMPStockEODFetcher
from builtin_providers.fmp.stock_insider_trading import FMPStockInsiderTradingFetcher
from builtin_providers.fmp.stock_news import FMPStockNewsFetcher
from builtin_providers.fmp.stock_ownership import FMPStockOwnershipFetcher
from builtin_providers.fmp.stock_price import FMPStockPriceFetcher
from builtin_providers.fmp.treasury_rates import FMPTreasuryRatesFetcher

# mypy: disable-error-code="list-item"

fmp_provider = Provider(
    name=ProviderNameType("fmp"),
    description="Provider for FMP.",
    fetcher_list=[
        FMPKeyExecutivesFetcher,
        FMPStockEODFetcher,
        FMPGlobalNewsFetcher,
        FMPStockNewsFetcher,
        FMPIncomeStatementFetcher,
        FMPBalanceSheetFetcher,
        FMPCashFlowStatementFetcher,
        FMPShareStatisticsFetcher,
        FMPMajorIndicesEODFetcher,
        FMPRevenueGeographicFetcher,
        FMPRevenueBusinessLineFetcher,
        FMPInstitutionalOwnershipFetcher,
        FMPCompanyProfileFetcher,
        FMPStockInsiderTradingFetcher,
        FMPStockOwnershipFetcher,
        FMPESGScoreFetcher,
        FMPESGSectorFetcher,
        FMPESGRiskRatingFetcher,
        FMPStockPriceFetcher,
        FMPPriceTargetConsensusFetcher,
        FMPPriceTargetFetcher,
        FMPAnalystEstimatesFetcher,
        FMPEarningsCalendarFetcher,
        FMPEarningsCallTranscriptFetcher,
        FMPHistoricalStockSplitsFetcher,
        FMPHistoricalDividendsFetcher,
        FMPKeyMetricsFetcher,
        FMPSECFilingsFetcher,
        FMPTreasuryRatesFetcher,
        FMPExecutiveCompensationFetcher,
        FMPCryptoPriceFetcher,
        FMPCryptoEODFetcher,
        FMPMajorIndicesPriceFetcher,
        FMPForexEODFetcher,
        FMPForexPriceFetcher,
    ],
)

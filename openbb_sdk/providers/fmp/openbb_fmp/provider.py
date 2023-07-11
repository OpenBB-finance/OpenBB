"""FMP Provider module."""

# IMPORT STANDARD

# IMPORT THIRD-PARTY

# IMPORT INTERNAL
from openbb_provider.provider.abstract.provider import Provider, ProviderNameType

from openbb_fmp.analyst_estimates import FMPAnalystEstimatesFetcher
from openbb_fmp.balance_sheet import FMPBalanceSheetFetcher
from openbb_fmp.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.company_profile import FMPCompanyProfileFetcher
from openbb_fmp.crypto_eod import FMPCryptoEODFetcher
from openbb_fmp.crypto_price import FMPCryptoPriceFetcher
from openbb_fmp.earnings_calendar import FMPEarningsCalendarFetcher
from openbb_fmp.earnings_call_transcript import (
    FMPEarningsCallTranscriptFetcher,
)
from openbb_fmp.esg_risk_rating import FMPESGRiskRatingFetcher
from openbb_fmp.esg_score import FMPESGScoreFetcher
from openbb_fmp.esg_sector import FMPESGSectorFetcher
from openbb_fmp.executive_compensation import FMPExecutiveCompensationFetcher
from openbb_fmp.executives import FMPKeyExecutivesFetcher
from openbb_fmp.forex_eod import FMPForexEODFetcher
from openbb_fmp.forex_price import FMPForexPriceFetcher
from openbb_fmp.global_news import FMPGlobalNewsFetcher
from openbb_fmp.historical_dividends import FMPHistoricalDividendsFetcher
from openbb_fmp.historical_stock_splits import (
    FMPHistoricalStockSplitsFetcher,
)
from openbb_fmp.income_statement import FMPIncomeStatementFetcher
from openbb_fmp.institutional_ownership import (
    FMPInstitutionalOwnershipFetcher,
)
from openbb_fmp.key_metrics import FMPKeyMetricsFetcher
from openbb_fmp.major_indices_eod import FMPMajorIndicesEODFetcher
from openbb_fmp.major_indices_price import FMPMajorIndicesPriceFetcher
from openbb_fmp.price_target import FMPPriceTargetFetcher
from openbb_fmp.price_target_consensus import FMPPriceTargetConsensusFetcher
from openbb_fmp.revenue_business_line import FMPRevenueBusinessLineFetcher
from openbb_fmp.revenue_geographic import FMPRevenueGeographicFetcher
from openbb_fmp.sec_filings import FMPSECFilingsFetcher
from openbb_fmp.share_statistics import FMPShareStatisticsFetcher
from openbb_fmp.stock_eod import FMPStockEODFetcher
from openbb_fmp.stock_insider_trading import FMPStockInsiderTradingFetcher
from openbb_fmp.stock_news import FMPStockNewsFetcher
from openbb_fmp.stock_ownership import FMPStockOwnershipFetcher
from openbb_fmp.stock_price import FMPStockPriceFetcher
from openbb_fmp.stock_splits import FMPStockSplitCalendarFetcher
from openbb_fmp.treasury_rates import FMPTreasuryRatesFetcher

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
        FMPStockSplitCalendarFetcher,
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

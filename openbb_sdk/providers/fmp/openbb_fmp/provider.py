"""FMP Provider module."""

# IMPORT STANDARD

# IMPORT THIRD-PARTY

# IMPORT INTERNAL
from openbb_provider.abstract.provider import Provider, ProviderNameType

from .analyst_estimates import FMPAnalystEstimatesFetcher
from .available_indices import FMPAvailableIndicesFetcher
from .balance_sheet import FMPBalanceSheetFetcher
from .cash_flow import FMPCashFlowStatementFetcher
from .company_profile import FMPCompanyProfileFetcher
from .crypto_eod import FMPCryptoEODFetcher
from .crypto_price import FMPCryptoPriceFetcher
from .dividend_calendar import FMPDividendCalendarFetcher
from .earnings_calendar import FMPEarningsCalendarFetcher
from .earnings_call_transcript import FMPEarningsCallTranscriptFetcher
from .esg_risk_rating import FMPESGRiskRatingFetcher
from .esg_score import FMPESGScoreFetcher
from .esg_sector import FMPESGSectorFetcher
from .executive_compensation import FMPExecutiveCompensationFetcher
from .executives import FMPKeyExecutivesFetcher
from .forex_eod import FMPForexEODFetcher
from .forex_pairs import FMPForexPairsFetcher
from .forex_price import FMPForexPriceFetcher
from .global_news import FMPGlobalNewsFetcher
from .historical_dividends import FMPHistoricalDividendsFetcher
from .historical_employees import FMPHistoricalEmployeesFetcher
from .historical_stock_splits import FMPHistoricalStockSplitsFetcher
from .income_statement import FMPIncomeStatementFetcher
from .institutional_ownership import FMPInstitutionalOwnershipFetcher
from .key_metrics import FMPKeyMetricsFetcher
from .major_indices_constituents import FMPMajorIndicesConstituentsFetcher
from .major_indices_eod import FMPMajorIndicesEODFetcher
from .major_indices_price import FMPMajorIndicesPriceFetcher
from .price_target import FMPPriceTargetFetcher
from .price_target_consensus import FMPPriceTargetConsensusFetcher
from .revenue_business_line import FMPRevenueBusinessLineFetcher
from .revenue_geographic import FMPRevenueGeographicFetcher
from .risk_premium import FMPRiskPremiumFetcher
from .sec_filings import FMPSECFilingsFetcher
from .share_statistics import FMPShareStatisticsFetcher
from .stock_eod import FMPStockEODFetcher
from .stock_insider_trading import FMPStockInsiderTradingFetcher
from .stock_multiples import FMPStockMultiplesFetcher
from .stock_news import FMPStockNewsFetcher
from .stock_ownership import FMPStockOwnershipFetcher
from .stock_peers import FMPStockPeersFetcher
from .stock_price import FMPStockPriceFetcher
from .stock_splits import FMPStockSplitCalendarFetcher
from .treasury_rates import FMPTreasuryRatesFetcher

# mypy: disable-error-code="list-item"

fmp_provider = Provider(
    name=ProviderNameType("fmp"),
    description="Provider for FMP.",
    required_credentials=["api_key"],
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
        FMPForexPairsFetcher,
        FMPStockPeersFetcher,
        FMPStockMultiplesFetcher,
        FMPHistoricalEmployeesFetcher,
        FMPAvailableIndicesFetcher,
        FMPRiskPremiumFetcher,
        FMPMajorIndicesConstituentsFetcher,
        FMPDividendCalendarFetcher,
    ],
)

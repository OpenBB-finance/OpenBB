"""OpenBB Nasdaq Provider Module."""

from __future__ import annotations

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_nasdaq.models.balance_sheet import NasdaqBalanceSheetFetcher
from openbb_nasdaq.models.calendar_dividend import NasdaqCalendarDividendFetcher
from openbb_nasdaq.models.calendar_earnings import NasdaqCalendarEarningsFetcher
from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
from openbb_nasdaq.models.calendar_splits import NasdaqCalendarSplitsFetcher
from openbb_nasdaq.models.cash_flow import NasdaqCashFlowStatementFetcher
from openbb_nasdaq.models.company_filings import NasdaqCompanyFilingsFetcher
from openbb_nasdaq.models.company_news import NasdaqCompanyNewsFetcher
from openbb_nasdaq.models.crypto_historical import NasdaqCryptoHistoricalFetcher
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
from openbb_nasdaq.models.equity_historical import NasdaqEquityHistoricalFetcher
from openbb_nasdaq.models.equity_info import NasdaqEquityInfoFetcher
from openbb_nasdaq.models.equity_quote import NasdaqEquityQuoteFetcher
from openbb_nasdaq.models.equity_screener import NasdaqEquityScreenerFetcher
from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher
from openbb_nasdaq.models.equity_short_interest import NasdaqEquityShortInterestFetcher
from openbb_nasdaq.models.etf_equity_exposure import NasdaqEtfEquityExposureFetcher
from openbb_nasdaq.models.etf_historical import NasdaqEtfHistoricalFetcher
from openbb_nasdaq.models.etf_holdings import NasdaqEtfHoldingsFetcher
from openbb_nasdaq.models.etf_info import NasdaqEtfInfoFetcher
from openbb_nasdaq.models.etf_search import NasdaqEtfSearchFetcher
from openbb_nasdaq.models.financial_ratios import NasdaqFinancialRatiosFetcher
from openbb_nasdaq.models.historical_dividends import NasdaqHistoricalDividendsFetcher
from openbb_nasdaq.models.historical_eps import NasdaqHistoricalEpsFetcher
from openbb_nasdaq.models.income_statement import NasdaqIncomeStatementFetcher
from openbb_nasdaq.models.index_historical import NasdaqIndexHistoricalFetcher
from openbb_nasdaq.models.index_search import NasdaqIndexSearchFetcher
from openbb_nasdaq.models.index_snapshots import NasdaqIndexSnapshotsFetcher
from openbb_nasdaq.models.insider_trading import NasdaqInsiderTradingFetcher
from openbb_nasdaq.models.institutional_ownership import (
    NasdaqInstitutionalOwnershipFetcher,
)
from openbb_nasdaq.models.market_movers import NasdaqMarketMoversFetcher
from openbb_nasdaq.models.market_status import NasdaqMarketStatusFetcher
from openbb_nasdaq.models.nordic_bond_yields import NasdaqNordicBondYieldsFetcher
from openbb_nasdaq.models.nordic_dividends import NasdaqNordicDividendsFetcher
from openbb_nasdaq.models.nordic_fundamentals import NasdaqNordicFundamentalsFetcher
from openbb_nasdaq.models.nordic_historical import NasdaqNordicHistoricalFetcher
from openbb_nasdaq.models.nordic_historical_trades import (
    NasdaqNordicHistoricalTradesFetcher,
)
from openbb_nasdaq.models.nordic_holidays import NasdaqNordicHolidaysFetcher
from openbb_nasdaq.models.nordic_index_factors import NasdaqNordicIndexFactorsFetcher
from openbb_nasdaq.models.nordic_info import NasdaqNordicInfoFetcher
from openbb_nasdaq.models.nordic_knocked_out import NasdaqNordicKnockedOutFetcher
from openbb_nasdaq.models.nordic_mortgage_rates import (
    NasdaqNordicMortgageRatesFetcher,
)
from openbb_nasdaq.models.nordic_movers import NasdaqNordicMoversFetcher
from openbb_nasdaq.models.nordic_news import NasdaqNordicNewsFetcher
from openbb_nasdaq.models.nordic_screener import NasdaqNordicScreenerFetcher
from openbb_nasdaq.models.nordic_trading_hours import (
    NasdaqNordicTradingHoursFetcher,
)
from openbb_nasdaq.models.options_chains import NasdaqOptionsChainsFetcher
from openbb_nasdaq.models.price_quote import NasdaqPriceQuoteFetcher
from openbb_nasdaq.models.price_target import NasdaqPriceTargetFetcher
from openbb_nasdaq.models.price_target_consensus import (
    NasdaqPriceTargetConsensusFetcher,
)

EQUITY_INSTALLED = find_spec("openbb_equity") is not None
ETF_INSTALLED = find_spec("openbb_etf") is not None
INDEX_INSTALLED = find_spec("openbb_index") is not None
CRYPTO_INSTALLED = find_spec("openbb_crypto") is not None
DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None
ECONOMY_INSTALLED = find_spec("openbb_economy") is not None
NEWS_INSTALLED = find_spec("openbb_news") is not None


def _key(standard: str, nasdaq_alias: str, installed: bool) -> str:
    """Return the standard key when the extension owning it is installed, else the alias."""
    return standard if installed else nasdaq_alias


_fetcher_dict: dict = {
    # Owned by openbb-equity.
    _key("BalanceSheet", "NasdaqBalanceSheet", EQUITY_INSTALLED): (
        NasdaqBalanceSheetFetcher
    ),
    _key("CalendarDividend", "NasdaqCalendarDividend", EQUITY_INSTALLED): (
        NasdaqCalendarDividendFetcher
    ),
    _key("CalendarEarnings", "NasdaqCalendarEarnings", EQUITY_INSTALLED): (
        NasdaqCalendarEarningsFetcher
    ),
    _key("CalendarIpo", "NasdaqCalendarIpo", EQUITY_INSTALLED): (
        NasdaqCalendarIpoFetcher
    ),
    _key("CalendarSplits", "NasdaqCalendarSplits", EQUITY_INSTALLED): (
        NasdaqCalendarSplitsFetcher
    ),
    _key("CashFlowStatement", "NasdaqCashFlowStatement", EQUITY_INSTALLED): (
        NasdaqCashFlowStatementFetcher
    ),
    _key("CompanyFilings", "NasdaqCompanyFilings", EQUITY_INSTALLED): (
        NasdaqCompanyFilingsFetcher
    ),
    _key("EquityHistorical", "NasdaqEquityHistorical", EQUITY_INSTALLED): (
        NasdaqEquityHistoricalFetcher
    ),
    _key("EquityInfo", "NasdaqEquityInfo", EQUITY_INSTALLED): NasdaqEquityInfoFetcher,
    _key("EquityQuote", "NasdaqEquityQuote", EQUITY_INSTALLED): (
        NasdaqEquityQuoteFetcher
    ),
    _key("EquityScreener", "NasdaqEquityScreener", EQUITY_INSTALLED): (
        NasdaqEquityScreenerFetcher
    ),
    _key("EquitySearch", "NasdaqEquitySearch", EQUITY_INSTALLED): (
        NasdaqEquitySearchFetcher
    ),
    _key("EquityShortInterest", "NasdaqEquityShortInterest", EQUITY_INSTALLED): (
        NasdaqEquityShortInterestFetcher
    ),
    _key("FinancialRatios", "NasdaqFinancialRatios", EQUITY_INSTALLED): (
        NasdaqFinancialRatiosFetcher
    ),
    _key("HistoricalDividends", "NasdaqHistoricalDividends", EQUITY_INSTALLED): (
        NasdaqHistoricalDividendsFetcher
    ),
    _key("HistoricalEps", "NasdaqHistoricalEps", EQUITY_INSTALLED): (
        NasdaqHistoricalEpsFetcher
    ),
    _key("IncomeStatement", "NasdaqIncomeStatement", EQUITY_INSTALLED): (
        NasdaqIncomeStatementFetcher
    ),
    _key("InsiderTrading", "NasdaqInsiderTrading", EQUITY_INSTALLED): (
        NasdaqInsiderTradingFetcher
    ),
    _key("InstitutionalOwnership", "NasdaqInstitutionalOwnership", EQUITY_INSTALLED): (
        NasdaqInstitutionalOwnershipFetcher
    ),
    _key("PriceTarget", "NasdaqPriceTarget", EQUITY_INSTALLED): (
        NasdaqPriceTargetFetcher
    ),
    _key("PriceTargetConsensus", "NasdaqPriceTargetConsensus", EQUITY_INSTALLED): (
        NasdaqPriceTargetConsensusFetcher
    ),
    # Owned by openbb-etf.
    _key("EtfEquityExposure", "NasdaqEtfEquityExposure", ETF_INSTALLED): (
        NasdaqEtfEquityExposureFetcher
    ),
    _key("EtfHistorical", "NasdaqEtfHistorical", ETF_INSTALLED): (
        NasdaqEtfHistoricalFetcher
    ),
    _key("EtfHoldings", "NasdaqEtfHoldings", ETF_INSTALLED): NasdaqEtfHoldingsFetcher,
    _key("EtfInfo", "NasdaqEtfInfo", ETF_INSTALLED): NasdaqEtfInfoFetcher,
    _key("EtfSearch", "NasdaqEtfSearch", ETF_INSTALLED): NasdaqEtfSearchFetcher,
    # Owned by openbb-index.
    _key("IndexHistorical", "NasdaqIndexHistorical", INDEX_INSTALLED): (
        NasdaqIndexHistoricalFetcher
    ),
    _key("IndexSearch", "NasdaqIndexSearch", INDEX_INSTALLED): NasdaqIndexSearchFetcher,
    _key("IndexSnapshots", "NasdaqIndexSnapshots", INDEX_INSTALLED): (
        NasdaqIndexSnapshotsFetcher
    ),
    # Owned by openbb-crypto.
    _key("CryptoHistorical", "NasdaqCryptoHistorical", CRYPTO_INSTALLED): (
        NasdaqCryptoHistoricalFetcher
    ),
    # Owned by openbb-derivatives.
    _key("OptionsChains", "NasdaqOptionsChains", DERIVATIVES_INSTALLED): (
        NasdaqOptionsChainsFetcher
    ),
    # Owned by openbb-economy.
    _key("EconomicCalendar", "NasdaqEconomicCalendar", ECONOMY_INSTALLED): (
        NasdaqEconomicCalendarFetcher
    ),
    # Owned by openbb-news.
    _key("CompanyNews", "NasdaqCompanyNews", NEWS_INSTALLED): NasdaqCompanyNewsFetcher,
    # No OpenBB extension claims these, so they are always Nasdaq's.
    "MarketMovers": NasdaqMarketMoversFetcher,
    "NasdaqMarketStatus": NasdaqMarketStatusFetcher,
    "NasdaqPriceQuote": NasdaqPriceQuoteFetcher,
    "NasdaqNordicScreener": NasdaqNordicScreenerFetcher,
    "NasdaqNordicNews": NasdaqNordicNewsFetcher,
    "NasdaqNordicInfo": NasdaqNordicInfoFetcher,
    "NasdaqNordicFundamentals": NasdaqNordicFundamentalsFetcher,
    "NasdaqNordicDividends": NasdaqNordicDividendsFetcher,
    "NasdaqNordicHistorical": NasdaqNordicHistoricalFetcher,
    "NasdaqNordicHistoricalTrades": NasdaqNordicHistoricalTradesFetcher,
    "NasdaqNordicMovers": NasdaqNordicMoversFetcher,
    "NasdaqNordicKnockedOut": NasdaqNordicKnockedOutFetcher,
    "NasdaqNordicBondYields": NasdaqNordicBondYieldsFetcher,
    "NasdaqNordicIndexFactors": NasdaqNordicIndexFactorsFetcher,
    "NasdaqNordicMortgageRates": NasdaqNordicMortgageRatesFetcher,
    "NasdaqNordicTradingHours": NasdaqNordicTradingHoursFetcher,
    "NasdaqNordicHolidays": NasdaqNordicHolidaysFetcher,
}

nasdaq_provider = Provider(
    name="nasdaq",
    website="https://www.nasdaq.com",
    description="""Positioned at the nexus of technology and the capital markets, Nasdaq
provides premier platforms and services for global capital markets and beyond with
unmatched technology, insights and markets expertise.""",
    credentials=None,
    fetcher_dict=_fetcher_dict,
    repr_name="Nasdaq",
)

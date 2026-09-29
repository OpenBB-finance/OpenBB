"""TMX Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.balance_sheet import TmxBalanceSheetFetcher
from openbb_tmx.models.bond_prices import TmxBondPricesFetcher
from openbb_tmx.models.bond_trades import TmxBondTradesFetcher
from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher
from openbb_tmx.models.cash_flow import TmxCashFlowStatementFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.company_news import TmxCompanyNewsFetcher
from openbb_tmx.models.covered_call_screener import (
    TmxCoveredCallScreenerFetcher,
)
from openbb_tmx.models.currency_historical import TmxCurrencyHistoricalFetcher
from openbb_tmx.models.equity_historical import TmxEquityHistoricalFetcher
from openbb_tmx.models.equity_profile import TmxEquityProfileFetcher
from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher
from openbb_tmx.models.equity_search import TmxEquitySearchFetcher
from openbb_tmx.models.equity_short_interest import TmxShortInterestFetcher
from openbb_tmx.models.equity_trades import TmxEquityTradesFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.futures_historical import TmxFuturesHistoricalFetcher
from openbb_tmx.models.futures_instruments import TmxFuturesInstrumentsFetcher
from openbb_tmx.models.gainers import TmxGainersFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.historical_splits import TmxHistoricalSplitsFetcher
from openbb_tmx.models.income_statement import TmxIncomeStatementFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.index_documents import TmxIndexDocumentsFetcher
from openbb_tmx.models.index_historical import TmxIndexHistoricalFetcher
from openbb_tmx.models.index_info import TmxIndexInfoFetcher
from openbb_tmx.models.index_sectors import TmxIndexSectorsFetcher
from openbb_tmx.models.index_snapshots import TmxIndexSnapshotsFetcher
from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher
from openbb_tmx.models.insider_transactions import TmxInsiderTransactionsFetcher
from openbb_tmx.models.market_movers import TmxMarketMoversFetcher
from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher
from openbb_tmx.models.rankings import TmxRankingsFetcher
from openbb_tmx.models.symbol_reference import TmxSymbolReferenceFetcher
from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

EQUITY_INSTALLED = find_spec("openbb_equity") is not None
ETF_INSTALLED = find_spec("openbb_etf") is not None
INDEX_INSTALLED = find_spec("openbb_index") is not None
DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None
CHARTING_INSTALLED = find_spec("openbb_charting") is not None
CURRENCY_INSTALLED = find_spec("openbb_currency") is not None
FIXEDINCOME_INSTALLED = find_spec("openbb_fixedincome") is not None
NEWS_INSTALLED = find_spec("openbb_news") is not None


def _key(standard: str, alias: str, installed: bool) -> str:
    """Return the standard key when the extension owning it is installed, else the alias."""
    return standard if installed else alias


tmx_provider = Provider(
    name="tmx",
    website="https://www.tmx.com",
    description="""Unofficial TMX Data Provider Extension
    TMX Group Companies
        - Toronto Stock Exchange
        - TSX Venture Exchange
        - TSX Trust
        - Montréal Exchange
        - TSX Alpha Exchange
        - Shorcan
        - CDCC
        - CDS
        - TMX Datalinx
        - Trayport
    """,
    fetcher_dict={
        _key(
            "AvailableIndices", "TmxAvailableIndices", INDEX_INSTALLED
        ): TmxAvailableIndicesFetcher,
        _key(
            "BalanceSheet", "TmxBalanceSheet", EQUITY_INSTALLED
        ): TmxBalanceSheetFetcher,
        _key(
            "BondPrices", "TmxBondPrices", FIXEDINCOME_INSTALLED
        ): TmxBondPricesFetcher,
        _key(
            "BondTrades", "TmxBondTrades", FIXEDINCOME_INSTALLED
        ): TmxBondTradesFetcher,
        _key(
            "CalendarEarnings", "TmxCalendarEarnings", EQUITY_INSTALLED
        ): TmxCalendarEarningsFetcher,
        _key(
            "CashFlowStatement", "TmxCashFlowStatement", EQUITY_INSTALLED
        ): TmxCashFlowStatementFetcher,
        _key(
            "CompanyFilings", "TmxCompanyFilings", EQUITY_INSTALLED
        ): TmxCompanyFilingsFetcher,
        _key("CompanyNews", "TmxCompanyNews", NEWS_INSTALLED): TmxCompanyNewsFetcher,
        _key(
            "CurrencyHistorical", "TmxCurrencyHistorical", CURRENCY_INSTALLED
        ): TmxCurrencyHistoricalFetcher,
        "CoveredCallScreener": TmxCoveredCallScreenerFetcher,
        _key(
            "EquityHistorical", "TmxEquityHistorical", EQUITY_INSTALLED
        ): TmxEquityHistoricalFetcher,
        _key("EquityInfo", "TmxEquityInfo", EQUITY_INSTALLED): TmxEquityProfileFetcher,
        _key("EquityQuote", "TmxEquityQuote", EQUITY_INSTALLED): TmxEquityQuoteFetcher,
        _key("EquityScreener", "TmxEquityScreener", EQUITY_INSTALLED): (
            TmxEquityScreenerFetcher
        ),
        _key(
            "EquitySearch", "TmxEquitySearch", EQUITY_INSTALLED
        ): TmxEquitySearchFetcher,
        "SymbolReference": TmxSymbolReferenceFetcher,
        "EquityTrades": TmxEquityTradesFetcher,
        "ShortInterest": TmxShortInterestFetcher,
        _key("EtfSearch", "TmxEtfSearch", ETF_INSTALLED): TmxEtfSearchFetcher,
        _key(
            "FuturesHistorical", "TmxFuturesHistorical", DERIVATIVES_INSTALLED
        ): TmxFuturesHistoricalFetcher,
        _key(
            "FuturesInstruments", "TmxFuturesInstruments", DERIVATIVES_INSTALLED
        ): TmxFuturesInstrumentsFetcher,
        _key("EtfHoldings", "TmxEtfHoldings", ETF_INSTALLED): TmxEtfHoldingsFetcher,
        _key("EtfSectors", "TmxEtfSectors", ETF_INSTALLED): TmxEtfSectorsFetcher,
        _key("EtfCountries", "TmxEtfCountries", ETF_INSTALLED): TmxEtfCountriesFetcher,
        _key(
            "EtfHistorical", "TmxEtfHistorical", ETF_INSTALLED
        ): TmxEquityHistoricalFetcher,
        _key("EtfInfo", "TmxEtfInfo", ETF_INSTALLED): TmxEtfInfoFetcher,
        _key("EquityGainers", "TmxEquityGainers", EQUITY_INSTALLED): TmxGainersFetcher,
        _key(
            "HistoricalDividends", "TmxHistoricalDividends", EQUITY_INSTALLED
        ): TmxHistoricalDividendsFetcher,
        _key(
            "HistoricalSplits", "TmxHistoricalSplits", EQUITY_INSTALLED
        ): TmxHistoricalSplitsFetcher,
        _key(
            "IncomeStatement", "TmxIncomeStatement", EQUITY_INSTALLED
        ): TmxIncomeStatementFetcher,
        _key(
            "IndexConstituents", "TmxIndexConstituents", INDEX_INSTALLED
        ): TmxIndexConstituentsFetcher,
        "TmxIndexDocuments": TmxIndexDocumentsFetcher,
        _key(
            "IndexHistorical", "TmxIndexHistorical", INDEX_INSTALLED
        ): TmxIndexHistoricalFetcher,
        _key("IndexInfo", "TmxIndexInfo", INDEX_INSTALLED): TmxIndexInfoFetcher,
        _key(
            "IndexSectors", "TmxIndexSectors", INDEX_INSTALLED
        ): TmxIndexSectorsFetcher,
        _key(
            "IndexSnapshots", "TmxIndexSnapshots", INDEX_INSTALLED
        ): TmxIndexSnapshotsFetcher,
        _key(
            "InsiderTrading", "TmxInsiderTrading", EQUITY_INSTALLED
        ): TmxInsiderTradingFetcher,
        "TmxInsiderTransactions": TmxInsiderTransactionsFetcher,
        "TmxRankings": TmxRankingsFetcher,
        "MarketMovers": TmxMarketMoversFetcher,
        _key(
            "OptionsChains", "TmxOptionsChains", DERIVATIVES_INSTALLED
        ): TmxOptionsChainsFetcher,
        _key(
            "PriceTargetConsensus", "TmxPriceTargetConsensus", EQUITY_INSTALLED
        ): TmxPriceTargetConsensusFetcher,
        _key(
            "TreasuryPrices", "TmxTreasuryPrices", FIXEDINCOME_INSTALLED
        ): TmxTreasuryPricesFetcher,
    },
    repr_name="TMX",
)

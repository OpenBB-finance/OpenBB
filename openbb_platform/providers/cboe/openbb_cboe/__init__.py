"""OpenBB Cboe Provider Module."""

from __future__ import annotations

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_cboe.models.available_indices import CboeAvailableIndicesFetcher
from openbb_cboe.models.equity_historical import CboeEquityHistoricalFetcher
from openbb_cboe.models.equity_quote import CboeEquityQuoteFetcher
from openbb_cboe.models.equity_search import CboeEquitySearchFetcher
from openbb_cboe.models.futures_curve import CboeFuturesCurveFetcher
from openbb_cboe.models.futures_instruments import CboeFuturesInstrumentsFetcher
from openbb_cboe.models.futures_settlements import CboeFuturesSettlementsFetcher
from openbb_cboe.models.index_constituents import CboeIndexConstituentsFetcher
from openbb_cboe.models.index_documents import CboeIndexDocumentsFetcher
from openbb_cboe.models.index_historical import CboeIndexHistoricalFetcher
from openbb_cboe.models.index_search import CboeIndexSearchFetcher
from openbb_cboe.models.index_snapshots import CboeIndexSnapshotsFetcher
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher

EQUITY_INSTALLED = find_spec("openbb_equity") is not None
ETF_INSTALLED = find_spec("openbb_etf") is not None
INDEX_INSTALLED = find_spec("openbb_index") is not None
DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None
CHARTING_INSTALLED = find_spec("openbb_charting") is not None


def _key(standard: str, cboe_alias: str, installed: bool) -> str:
    """Return the standard key when the extension owning it is installed, else the Cboe alias."""
    return standard if installed else cboe_alias


_fetcher_dict: dict = {
    _key("AvailableIndices", "CboeAvailableIndices", INDEX_INSTALLED): (
        CboeAvailableIndicesFetcher
    ),
    _key("EquityHistorical", "CboeEquityHistorical", EQUITY_INSTALLED): (
        CboeEquityHistoricalFetcher
    ),
    _key("EquityQuote", "CboeEquityQuote", EQUITY_INSTALLED): CboeEquityQuoteFetcher,
    _key("EquitySearch", "CboeEquitySearch", EQUITY_INSTALLED): CboeEquitySearchFetcher,
    _key("FuturesCurve", "CboeFuturesCurve", DERIVATIVES_INSTALLED): (
        CboeFuturesCurveFetcher
    ),
    _key("FuturesInstruments", "CboeFuturesInstruments", DERIVATIVES_INSTALLED): (
        CboeFuturesInstrumentsFetcher
    ),
    "CboeFuturesSettlements": CboeFuturesSettlementsFetcher,
    _key("IndexConstituents", "CboeIndexConstituents", INDEX_INSTALLED): (
        CboeIndexConstituentsFetcher
    ),
    "CboeIndexDocuments": CboeIndexDocumentsFetcher,
    _key("IndexHistorical", "CboeIndexHistorical", INDEX_INSTALLED): (
        CboeIndexHistoricalFetcher
    ),
    _key("IndexSearch", "CboeIndexSearch", INDEX_INSTALLED): CboeIndexSearchFetcher,
    _key("IndexSnapshots", "CboeIndexSnapshots", INDEX_INSTALLED): (
        CboeIndexSnapshotsFetcher
    ),
    _key("OptionsChains", "CboeOptionsChains", DERIVATIVES_INSTALLED): (
        CboeOptionsChainsFetcher
    ),
}

if ETF_INSTALLED:
    _fetcher_dict["EtfHistorical"] = CboeEquityHistoricalFetcher

cboe_provider = Provider(
    name="cboe",
    website="https://www.cboe.com",
    description="""Cboe is the world's go-to derivatives and exchange network,
delivering cutting-edge trading, clearing and investment solutions to people
around the world.""",
    credentials=None,
    fetcher_dict=_fetcher_dict,
    repr_name="Chicago Board Options Exchange (CBOE)",
)

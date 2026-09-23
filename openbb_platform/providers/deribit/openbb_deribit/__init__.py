"""OpenBB Deribit Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_deribit.models.announcements import DeribitAnnouncementsFetcher
from openbb_deribit.models.apr_history import DeribitAprHistoryFetcher
from openbb_deribit.models.block_rfq_trades import DeribitBlockRfqTradesFetcher
from openbb_deribit.models.book_summary import DeribitBookSummaryFetcher
from openbb_deribit.models.combos import DeribitCombosFetcher
from openbb_deribit.models.currencies import DeribitCurrenciesFetcher
from openbb_deribit.models.delivery_prices import DeribitDeliveryPricesFetcher
from openbb_deribit.models.expirations import DeribitExpirationsFetcher
from openbb_deribit.models.funding_chart import DeribitFundingChartFetcher
from openbb_deribit.models.funding_rate_history import (
    DeribitFundingRateHistoryFetcher,
)
from openbb_deribit.models.futures_curve import DeribitFuturesCurveFetcher
from openbb_deribit.models.futures_historical import DeribitFuturesHistoricalFetcher
from openbb_deribit.models.futures_info import DeribitFuturesInfoFetcher
from openbb_deribit.models.futures_instruments import DeribitFuturesInstrumentsFetcher
from openbb_deribit.models.historical_volatility import (
    DeribitHistoricalVolatilityFetcher,
)
from openbb_deribit.models.index_historical import DeribitIndexHistoricalFetcher
from openbb_deribit.models.index_price import DeribitIndexPriceFetcher
from openbb_deribit.models.instruments import DeribitInstrumentsFetcher
from openbb_deribit.models.mark_price_history import DeribitMarkPriceHistoryFetcher
from openbb_deribit.models.options_chains import DeribitOptionsChainsFetcher
from openbb_deribit.models.order_book import DeribitOrderBookFetcher
from openbb_deribit.models.settlements import DeribitSettlementsFetcher
from openbb_deribit.models.ticker import DeribitTickerFetcher
from openbb_deribit.models.trade_volumes import DeribitTradeVolumesFetcher
from openbb_deribit.models.trades import DeribitTradesFetcher
from openbb_deribit.models.volatility_index import DeribitVolatilityIndexFetcher

DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None
CHARTING_INSTALLED = find_spec("openbb_charting") is not None


def _key(standard: str, alias: str, installed: bool) -> str:
    """Return the standard key when the extension owning it is installed, else the alias."""
    return standard if installed else alias


_fetcher_dict: dict = {
    "DeribitAnnouncements": DeribitAnnouncementsFetcher,
    "DeribitAprHistory": DeribitAprHistoryFetcher,
    "DeribitBlockRfqTrades": DeribitBlockRfqTradesFetcher,
    "DeribitBookSummary": DeribitBookSummaryFetcher,
    "DeribitCombos": DeribitCombosFetcher,
    "DeribitCurrencies": DeribitCurrenciesFetcher,
    "DeribitDeliveryPrices": DeribitDeliveryPricesFetcher,
    "DeribitExpirations": DeribitExpirationsFetcher,
    "DeribitFundingChart": DeribitFundingChartFetcher,
    "DeribitFundingRateHistory": DeribitFundingRateHistoryFetcher,
    "DeribitHistoricalVolatility": DeribitHistoricalVolatilityFetcher,
    "DeribitIndexHistorical": DeribitIndexHistoricalFetcher,
    "DeribitIndexPrice": DeribitIndexPriceFetcher,
    "DeribitInstruments": DeribitInstrumentsFetcher,
    "DeribitMarkPriceHistory": DeribitMarkPriceHistoryFetcher,
    "DeribitOrderBook": DeribitOrderBookFetcher,
    "DeribitSettlements": DeribitSettlementsFetcher,
    "DeribitTicker": DeribitTickerFetcher,
    "DeribitTradeVolumes": DeribitTradeVolumesFetcher,
    "DeribitTrades": DeribitTradesFetcher,
    "DeribitVolatilityIndex": DeribitVolatilityIndexFetcher,
    _key("FuturesCurve", "DeribitFuturesCurve", DERIVATIVES_INSTALLED): (
        DeribitFuturesCurveFetcher
    ),
    _key("FuturesHistorical", "DeribitFuturesHistorical", DERIVATIVES_INSTALLED): (
        DeribitFuturesHistoricalFetcher
    ),
    _key("FuturesInfo", "DeribitFuturesInfo", DERIVATIVES_INSTALLED): (
        DeribitFuturesInfoFetcher
    ),
    _key("FuturesInstruments", "DeribitFuturesInstruments", DERIVATIVES_INSTALLED): (
        DeribitFuturesInstrumentsFetcher
    ),
    _key("OptionsChains", "DeribitOptionsChains", DERIVATIVES_INSTALLED): (
        DeribitOptionsChainsFetcher
    ),
}

deribit_provider = Provider(
    name="deribit",
    website="https://deribit.com/",
    description="""Deribit is a crypto derivatives exchange listing futures, perpetuals,
options, and spot pairs. This extension covers its public market data API, which
needs no credentials and carries no trading.""",
    credentials=None,
    fetcher_dict=_fetcher_dict,
    repr_name="Deribit Public Data",
    instructions="This provider needs no credentials and is not meant for trading.",
)

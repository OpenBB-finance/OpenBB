"""Fixed enumerations and choice endpoints of the Deribit public API."""

from typing import Literal

from openbb_core.app.service.system_service import SystemService

API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

CURRENCY_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/reference/currency_choices"
INDEX_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/reference/index_choices"
INSTRUMENT_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/reference/instrument_choices"
COMBO_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/reference/combo_choices"
CURVE_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/futures/curve_choices"
PERPETUAL_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/futures/perpetual_choices"
UNDERLYING_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/options/underlying_choices"
EXPIRATION_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/options/expiration_choices"
STRATEGY_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/options/strategy_choices"
MARK_PRICE_CHOICES_ENDPOINT = f"{API_PREFIX}/deribit/market/mark_price_choices"

SYMBOL_STYLE = {"popupWidth": 600}

CURRENCIES = ("BTC", "ETH", "USDC", "USDT", "EURR")
Currencies = Literal["BTC", "ETH", "USDC", "USDT", "EURR"]
AnyCurrencies = Literal["BTC", "ETH", "USDC", "USDT", "EURR", "any"]

VOLATILITY_INDEX_CURRENCIES = ("BTC", "ETH")
REALIZED_VOLATILITY_CURRENCIES = ("BTC", "ETH", "EURR")

UNDERLYING_CURRENCIES = ("BTC", "ETH")
LISTING_CURRENCIES = ("BTC", "ETH", "USDC")
ListingCurrencies = Literal["BTC", "ETH", "USDC"]
AnyListingCurrencies = Literal["BTC", "ETH", "USDC", "any"]
OPTION_KINDS = ("option", "option_combo")

INSTRUMENT_KINDS = ("future", "option", "spot", "future_combo", "option_combo")
InstrumentKinds = Literal["future", "option", "spot", "future_combo", "option_combo"]
TradeKinds = Literal["future", "option", "future_combo", "option_combo", "combo"]
ROUTED_SPOT_ERROR = "not_supported_for_coinbase_routed_spot"
ExpirationKinds = Literal["future", "option", "any"]
ExpirationCurrencies = Literal["BTC", "ETH", "any", "grouped"]

SettlementTypes = Literal["settlement", "delivery", "bankruptcy"]
ComboStates = Literal["active", "inactive"]
IndexNameTypes = Literal["all", "spot", "derivative"]
Sorting = Literal["asc", "desc", "default"]
FundingLengths = Literal["8h", "24h", "1m"]
IndexChartRanges = Literal["1h", "1d", "2d", "1m", "1y", "all"]
AprCurrencies = Literal["usde", "steth", "usdc", "build"]

ORDER_BOOK_DEPTHS = ("1", "5", "10", "20", "50", "100", "1000", "10000")
OrderBookDepths = Literal["1", "5", "10", "20", "50", "100", "1000", "10000"]

INTERVALS = (
    "1m",
    "3m",
    "5m",
    "10m",
    "15m",
    "30m",
    "1h",
    "2h",
    "3h",
    "6h",
    "12h",
    "1d",
)
Intervals = Literal[
    "1m", "3m", "5m", "10m", "15m", "30m", "1h", "2h", "3h", "6h", "12h", "1d"
]
INTERVAL_MAP = {
    "1m": "1",
    "3m": "3",
    "5m": "5",
    "10m": "10",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "3h": "180",
    "6h": "360",
    "12h": "720",
    "1d": "1D",
}

VOLATILITY_RESOLUTIONS = ("1m", "1h", "12h", "1d")
VolatilityResolutions = Literal["1m", "1h", "12h", "1d"]
VOLATILITY_RESOLUTION_MAP = {
    "1m": "60",
    "1h": "3600",
    "12h": "43200",
    "1d": "1D",
}

BLOCK_RFQ_MIN_COUNT = 10
BLOCK_RFQ_MAX_COUNT = 50
MAX_TRADE_COUNT = 1000
MAX_SETTLEMENT_COUNT = 1000

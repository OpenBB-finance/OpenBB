"""Polygon WebSocket Connection Model."""

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_polygon.utils.constants import (
    CRYPTO_EXCHANGE_MAP,
    FX_EXCHANGE_MAP,
    STOCK_EXCHANGE_MAP,
    STOCK_QUOTE_CONDITIONS,
    STOCK_QUOTE_INDICATORS,
    STOCK_TRADE_CONDITIONS,
)
from openbb_polygon.utils.helpers import map_tape
from openbb_websockets.client import WebSocketClient
from openbb_websockets.models import (
    WebSocketConnection,
    WebSocketData,
    WebSocketQueryParams,
)
from pydantic import Field, field_validator, model_validator

URL_MAP = {
    "stock": "wss://socket.polygon.io/stocks",
    "stock_delayed": "wss://delayed.polygon.io/stocks",
    "index": "wss://socket.polygon.io/indices",
    "index_delayed": "wss://delayed.polygon.io/indices",
    "fx": "wss://socket.polygon.io/forex",
    "crypto": "wss://socket.polygon.io/crypto",
}

ASSET_CHOICES = ["stock", "stock_delayed", "fx", "crypto", "index", "index_delayed"]

FEED_MAP = {
    "crypto": {
        "aggs_min": "XA",
        "aggs_sec": "XAS",
        "trade": "XT",
        "quote": "XQ",
        "l2": "XL2",
        "fmv": "FMV",
    },
    "fx": {
        "aggs_min": "CA",
        "aggs_sec": "CAS",
        "quote": "C",
        "fmv": "FMV",
    },
    "stock": {
        "aggs_min": "AM",
        "aggs_sec": "AS",
        "trade": "T",
        "quote": "Q",
        "fmv": "FMV",
    },
    "stock_delayed": {
        "aggs_min": "AM",
        "aggs_sec": "AS",
        "trade": "T",
        "quote": "Q",
        "fmv": "FMV",
    },
    "index": {
        "aggs_min": "AM",
        "aggs_sec": "AS",
        "value": "V",
    },
    "index_delayed": {
        "aggs_min": "AM",
        "aggs_sec": "AS",
        "value": "V",
    },
}


def validate_date(cls, v):
    """Validate the date."""
    # pylint: disable=import-outside-toplevel
    from pytz import timezone

    try:
        dt = datetime.utcfromtimestamp(v / 1000).replace(tzinfo=timezone("UTC"))
        dt = dt.astimezone(timezone("America/New_York"))
        return dt
    except Exception:
        if isinstance(v, (int, float)):
            # Check if the timestamp is in nanoseconds and convert to seconds
            if v > 1e12:
                v = v / 1e9  # Convert nanoseconds to seconds
            dt = datetime.fromtimestamp(v, tz=timezone("UTC"))
            dt = dt.astimezone(timezone("America/New_York"))
            return dt


class PolygonWebSocketQueryParams(WebSocketQueryParams):
    """Polygon WebSocket query parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "asset_type": {
            "multiple_items_allowed": False,
            "choices": ASSET_CHOICES,
        },
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    asset_type: Literal[
        "stock", "stock_delayed", "fx", "crypto", "index", "index_delayed"
    ] = Field(
        default="crypto",
        description="The asset type associated with the symbol(s)."
        + " Choose from: stock, stock_delayed, fx, crypto.",
    )
    feed: Literal["aggs_min", "aggs_sec", "trade", "quote", "l2"] = Field(
        default="aggs_sec",
        description="The feed type to subscribe to. Choose from: aggs_min, aggs_sec, trade, quote, l2."
        + "l2 is only available for crypto.",
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_feed(cls, values):
        """Validate the feed."""
        feed = values.get("feed")
        asset_type = values.get("asset_type")
        if asset_type == "fx" and feed in ["trade", "l2"]:
            raise ValueError("FX does not support the trade or l2 feeds.")
        if asset_type in ["stock", "stock_delayed"] and feed == "l2":
            raise ValueError("Stock does not support the l2 feed.")
        if asset_type == "index" and feed in ["trade", "quote", "l2", "fmv"]:
            raise ValueError(
                "Index does not support the trade, quote, l2, or fmv feeds."
            )

        return values


class PolygonCryptoAggsWebSocketData(WebSocketData):
    """Polygon Crypto Aggregates WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "pair",
        "date": "e",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "vwap": "vw",
        "volume": "v",
        "avg_size": "z",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + "The end of the aggregate window.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    open: float = Field(
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: float = Field(
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: float = Field(
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: float = Field(
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    vwap: float = Field(
        description=DATA_DESCRIPTIONS.get("vwap", ""),
    )
    volume: float = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    avg_size: Optional[float] = Field(
        default=None,
        description="The average trade size for the aggregate window.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("s", None)
        return values


class PolygonCryptoTradeWebSocketData(WebSocketData):
    """Polygon Crypto WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "pair",
        "date": "t",
        "exchange": "x",
        "price": "p",
        "size": "s",
        "conditions": "c",
        "received_at": "r",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    received_at: datetime = Field(
        description="The time the data was received by Polygon.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    exchange: str = Field(
        default=None,
        description="The exchange of the data.",
    )
    conditions: Optional[str] = Field(
        default=None,
        description="The conditions of the trade. Either sellside or buyside, if available.",
    )
    price: float = Field(
        description="The price of the trade.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    size: float = Field(
        description="The size of the trade.",
    )

    @field_validator("conditions", mode="before", check_fields=False)
    @classmethod
    def _validate_conditions(cls, v):
        """Validate the conditions."""
        if v is None or isinstance(v, list) and v[0] == 0:
            return None
        elif isinstance(v, list) and v[0] == 1:
            return "sellside"
        elif isinstance(v, list) and v[0] == 2:
            return "buyside"
        return str(v)

    @field_validator("date", "received_at", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return CRYPTO_EXCHANGE_MAP.get(v, str(v))

    @model_validator(mode="before")
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("i", None)
        return values


class PolygonCryptoQuoteWebSocketData(WebSocketData):
    """Polygon Crypto Quote WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "pair",
        "date": "t",
        "exchange": "x",
        "bid": "bp",
        "bid_size": "bs",
        "ask": "ap",
        "ask_size": "as",
        "received_at": "r",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    received_at: datetime = Field(
        description="The time the data was received by Polygon.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    exchange: str = Field(
        default=None,
        description="The exchange of the data.",
    )
    bid_size: float = Field(
        description="The size of the bid.",
    )
    bid: float = Field(
        description="The bid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask: float = Field(
        description="The ask price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: float = Field(
        description="The size of the ask.",
    )

    @field_validator("date", "received_at", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return CRYPTO_EXCHANGE_MAP.get(v, str(v))

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        lp = values.pop("lp", None)
        ls = values.pop("ls", None)
        if lp:
            values["last_price"] = lp
        if ls:
            values["last_size"] = ls

        return values


class PolygonCryptoL2WebSocketData(WebSocketData):
    """Polygon Crypto L2 WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "pair",
        "date": "t",
        "exchange": "x",
        "bid": "b",
        "ask": "a",
        "received_at": "r",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    received_at: datetime = Field(
        description="The time the data was received by Polygon.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    exchange: str = Field(
        default=None,
        description="The exchange of the data.",
    )
    bid: list[list[float]] = Field(
        description="An array of bid prices, where each entry contains two elements:"
        + " the first is the bid price, and the second is the size, with a maximum depth of 100.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask: list[list[float]] = Field(
        description="An array of ask prices, where each entry contains two elements:"
        + " the first is the ask price, and the second is the size, with a maximum depth of 100.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )

    @field_validator("date", "received_at", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return CRYPTO_EXCHANGE_MAP.get(v, str(v))


class PolygonFXQuoteWebSocketData(WebSocketData):
    """Polygon FX Quote WebSocket data model."""

    __alias_dict__ = {
        "date": "t",
        "type": "ev",
        "symbol": "p",
        "exchange": "x",
        "ask": "a",
        "bid": "b",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    exchange: str = Field(
        default=None,
        description="The exchange of the data.",
    )
    bid: float = Field(
        description="The bid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask: float = Field(
        description="The ask price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return FX_EXCHANGE_MAP.get(v, str(v))


class PolygonStockAggsWebSocketData(WebSocketData):
    """Polygon Stock Aggregates WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "sym",
        "date": "e",
        "day_open": "op",
        "day_volume": "av",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "vwap": "vw",
        "day_vwap": "a",
        "volume": "v",
        "avg_size": "z",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + "The end of the aggregate window.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    day_open: float = Field(
        description="Today's official opening price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open: float = Field(
        description=DATA_DESCRIPTIONS.get("open", "")
        + " For the current aggregate window.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: float = Field(
        description=DATA_DESCRIPTIONS.get("high", "")
        + " For the current aggregate window.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: float = Field(
        description=DATA_DESCRIPTIONS.get("low", "")
        + " For the current aggregate window.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: float = Field(
        description=DATA_DESCRIPTIONS.get("close", "")
        + " For the current aggregate window.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    vwap: float = Field(
        description=DATA_DESCRIPTIONS.get("vwap", "")
        + " For the current aggregate window.",
    )
    day_vwap: float = Field(
        description="Today's volume weighted average price.",
    )
    volume: float = Field(
        description=DATA_DESCRIPTIONS.get("volume", "")
        + " For the current aggregate window.",
    )
    day_volume: float = Field(
        description="Today's accumulated volume.",
    )
    avg_size: Optional[float] = Field(
        default=None,
        description="The average trade size for the aggregate window.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("s", None)
        _ = values.pop("otc", None)
        if values.get("z") and values["z"] == 0 or not values.get("z"):
            _ = values.pop("z", None)
        return values


class PolygonStockTradeWebSocketData(WebSocketData):
    """Polygon Stock Trade WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "sym",
        "date": "t",
        "exchange": "x",
        "trf_id": "trfi",
        "tape": "z",
        "price": "p",
        "conditions": "c",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + "The end of the aggregate window.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    price: float = Field(
        description="The price of the trade.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    exchange: str = Field(
        description="The exchange where the trade originated.",
    )
    tape: str = Field(
        description="The tape where the trade occurred.",
    )
    conditions: Optional[str] = Field(
        default=None,
        description="The conditions of the trade.",
    )
    trf_id: Optional[str] = Field(
        default=None,
        description="The ID for the Trade Reporting Facility where the trade took place.",
    )
    trf_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of when the trade reporting facility received this trade.",
    )

    @field_validator("date", "trf_timestamp", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("tape", mode="before", check_fields=False)
    @classmethod
    def _validate_tape(cls, v):
        """Validate the tape."""
        return map_tape(v)

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return STOCK_EXCHANGE_MAP.get(v, str(v))

    @field_validator("conditions", mode="before", check_fields=False)
    @classmethod
    def _validate_conditions(cls, v):
        """Validate the conditions."""
        if v is None or not v:
            return None
        new_conditions: list = []
        if isinstance(v, list):
            for c in v:
                new_conditions.append(STOCK_TRADE_CONDITIONS.get(c, str(c)))
        elif isinstance(v, int):
            new_conditions.append(STOCK_TRADE_CONDITIONS.get(v, str(v)))

        if not new_conditions:
            return None
        return "; ".join(new_conditions)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("i", None)
        _ = values.pop("q", None)
        return values


class PolygonStockQuoteWebSocketData(WebSocketData):
    """Polygon Stock Quote WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "sym",
        "date": "t",
        "bid_exchange": "bx",
        "bid_size": "bs",
        "bid": "bp",
        "ask": "ap",
        "ask_size": "as",
        "ask_exchange": "ax",
        "tape": "z",
        "condition": "c",
        "indicators": "i",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + "The end of the aggregate window.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    bid_exchange: str = Field(
        description="The exchange where the bid originated.",
    )
    bid_size: float = Field(
        description="The size of the bid.",
    )
    bid: float = Field(
        description="The bid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask: float = Field(
        description="The ask price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: float = Field(
        description="The size of the ask.",
    )
    ask_exchange: str = Field(
        description="The exchange where the ask originated.",
    )
    tape: str = Field(
        description="The tape where the quote occurred.",
    )
    condition: Optional[str] = Field(
        default=None,
        description="The condition of the quote.",
    )
    indicators: Optional[str] = Field(
        default=None,
        description="The indicators of the quote.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @field_validator("bid_exchange", "ask_exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return STOCK_EXCHANGE_MAP.get(v, str(v))

    @field_validator("tape", mode="before", check_fields=False)
    @classmethod
    def _validate_tape(cls, v):
        """Validate the tape."""
        return map_tape(v)

    @field_validator("condition", mode="before", check_fields=False)
    @classmethod
    def _validate_condition(cls, v):
        """Validate the condition."""
        return STOCK_QUOTE_CONDITIONS.get(v, str(v))

    @field_validator("indicators", mode="before", check_fields=False)
    @classmethod
    def _validate_indicators(cls, v):
        """Validate the indicators."""
        if v is None or not v:
            return None
        new_indicators: list = []
        if isinstance(v, list):
            for c in v:
                new_indicators.append(STOCK_QUOTE_INDICATORS.get(c, str(c)))
        elif isinstance(v, int):
            new_indicators.append(STOCK_QUOTE_INDICATORS.get(v, str(v)))

        if not new_indicators:
            return None
        return "; ".join(new_indicators)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("q", None)
        return values


class PolygonIndexAggsWebSocketData(WebSocketData):
    """Polygon Index Aggregates WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "sym",
        "date": "e",
        "day_open": "op",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + "The end of the aggregate window.",
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    day_open: float = Field(
        description="Today's official opening level.",
    )
    open: float = Field(
        description=DATA_DESCRIPTIONS.get("open", "")
        + " For the current aggregate window.",
    )
    high: float = Field(
        description=DATA_DESCRIPTIONS.get("high", "")
        + " For the current aggregate window.",
    )
    low: float = Field(
        description=DATA_DESCRIPTIONS.get("low", "")
        + " For the current aggregate window.",
    )
    close: float = Field(
        description=DATA_DESCRIPTIONS.get("close", "")
        + " For the current aggregate window.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        _ = values.pop("s", None)
        return values


class PolygonIndexValueWebSocketData(WebSocketData):
    """Polygon Index Value WebSocket data model."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "T",
        "date": "t",
        "value": "val",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    value: float = Field(
        description="The value of the index.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        return validate_date(cls, v)


class PolygonFairMarketValueData(WebSocketData):
    """Polygon Fair Market Value WebSocket Data."""

    __alias_dict__ = {
        "type": "ev",
        "symbol": "sym",
        "date": "t",
        "fair_market_value": "fmv",
    }

    type: str = Field(
        description="The type of data.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    fair_market_value: float = Field(
        description="Polygon proprietary algorithm determining real-time, accurate,"
        + " fair market value of a tradable security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )


MODEL_MAP = {
    "XT": PolygonCryptoTradeWebSocketData,
    "XQ": PolygonCryptoQuoteWebSocketData,
    "XL2": PolygonCryptoL2WebSocketData,
    "XA": PolygonCryptoAggsWebSocketData,
    "XAS": PolygonCryptoAggsWebSocketData,
    "FMV": PolygonFairMarketValueData,
    "CA": PolygonCryptoAggsWebSocketData,
    "CAS": PolygonCryptoAggsWebSocketData,
    "C": PolygonFXQuoteWebSocketData,
    "AM": PolygonStockAggsWebSocketData,
    "AS": PolygonStockAggsWebSocketData,
    "T": PolygonStockTradeWebSocketData,
    "Q": PolygonStockQuoteWebSocketData,
    "A": PolygonIndexAggsWebSocketData,
    "V": PolygonIndexValueWebSocketData,
}


class PolygonWebSocketData(Data):
    """Polygon WebSocket data model."""

    def __new__(cls, **data):
        """Create new instance of appropriate model type."""
        index_symbol = data.get("sym", "").startswith("I:") or data.get(
            "symbol", ""
        ).startswith("I:")
        model = (
            MODEL_MAP["A"]
            if index_symbol
            else MODEL_MAP.get(data.get("ev")) or MODEL_MAP.get(data.get("type"))
        )
        if not model:
            return super().__new__(cls)

        return model.model_validate(data)


class PolygonWebSocketConnection(WebSocketConnection):
    """Polygon WebSocket connection model."""


class PolygonWebSocketFetcher(
    Fetcher[PolygonWebSocketQueryParams, PolygonWebSocketConnection]
):
    """Polygon WebSocket Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> PolygonWebSocketQueryParams:
        """Transform the query parameters."""
        return PolygonWebSocketQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonWebSocketQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> WebSocketClient:
        """Extract data from the WebSocket."""
        # pylint: disable=import-outside-toplevel
        import time

        api_key = credentials.get("polygon_api_key") if credentials else ""
        url = URL_MAP[query.asset_type]

        symbol = query.symbol.upper()

        kwargs = {
            "url": url,
            "asset_type": query.asset_type,
            "feed": query.feed,
            "api_key": api_key,
            "connect_kwargs": query.connect_kwargs,
        }

        client = WebSocketClient(
            name=query.name,
            module="openbb_polygon.utils.websocket_client",
            symbol=symbol,
            limit=query.limit,
            results_file=query.results_file,
            table_name=query.table_name,
            save_results=query.save_results,
            data_model=PolygonWebSocketData,
            sleep_time=query.sleep_time,
            broadcast_host=query.broadcast_host,
            broadcast_port=query.broadcast_port,
            auth_token=query.auth_token,
            **kwargs,
        )

        try:
            client.connect()
        except Exception as e:
            client.disconnect()
            raise OpenBBError(e) from e

        time.sleep(1)

        if client._exception:
            raise client._exception from client._exception

        if client.is_running:
            return client

        raise OpenBBError("Failed to connect to the WebSocket.")

    @staticmethod
    def transform_data(
        data: WebSocketClient,
        query: PolygonWebSocketQueryParams,
        **kwargs: Any,
    ) -> PolygonWebSocketConnection:
        """Return the client as an instance of Data."""
        return PolygonWebSocketConnection(client=data)

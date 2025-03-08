"""Tiingo WebSocket model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.websockets.client import WebSocketClient
from openbb_core.provider.utils.websockets.models import (
    WebSocketConnection,
    WebSocketData,
    WebSocketQueryParams,
)
from pydantic import Field, field_validator, model_validator

# These are the data array order of definitions.
IEX_FIELDS = [
    "type",
    "tiingo_date",
    "timestamp",
    "symbol",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_price",
    "ask_size",
    "last_price",
    "last_size",
    "halted",
    "after_hours",
    "sweep_order",
    "oddlot",
    "nms_rule",
]
FX_FIELDS = [
    "type",
    "symbol",
    "tiingo_date",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_price",
    "ask_size",
    "ask_price",
]
CRYPTO_TRADE_FIELDS = [
    "type",
    "symbol",
    "tiingo_date",
    "exchange",
    "last_size",
    "last_price",
]
CRYPTO_QUOTE_FIELDS = [
    "type",
    "symbol",
    "tiingo_date",
    "exchange",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_size",
    "ask_price",
]


class TiingoWebSocketQueryParams(WebSocketQueryParams):
    """Tiingo WebSocket query parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "asset_type": {
            "multiple_items_allowed": False,
            "choices": ["stock", "fx", "crypto"],
        },
        "feed": {
            "multiple_items_allowed": False,
            "choices": ["trade", "trade_and_quote"],
        },
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " Use '*' for all symbols.",
    )
    asset_type: Literal["stock", "fx", "crypto"] = Field(
        default="crypto",
        description="The asset type for the feed. Choices are 'stock', 'fx', or 'crypto'.",
    )
    feed: Literal["trade", "trade_and_quote"] = Field(
        default="trade",
        description="The asset type associated with the symbol. Choices are 'trade' or 'trade_and_quote'."
        + " FX only supports quote.",
    )


class TiingoWebSocketData(WebSocketData):
    """Tiingo WebSocket data model."""

    timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the data.",
    )
    type: Literal["quote", "trade", "break"] = Field(
        description="The type of data.",
    )
    exchange: Optional[str] = Field(
        default=None,
        description="The exchange of the data. Only for crypto.",
    )
    bid_size: Optional[float] = Field(
        default=None,
        description="The size of the bid.",
    )
    bid_price: Optional[float] = Field(
        default=None,
        description="The price of the bid.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    mid_price: Optional[float] = Field(
        default=None,
        description="The mid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_price: Optional[float] = Field(
        default=None,
        description="The price of the ask.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: Optional[float] = Field(
        default=None,
        description="The size of the ask.",
    )
    last_price: Optional[float] = Field(
        default=None,
        description="The last trade price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: Optional[float] = Field(
        default=None,
        description="The size of the trade.",
    )
    halted: Optional[bool] = Field(
        default=None,
        description="If the asset is halted. Only for stock.",
    )
    after_hours: Optional[bool] = Field(
        default=None,
        description="If the data is after hours. Only for stock.",
    )
    sweep_order: Optional[bool] = Field(
        default=None,
        description="If the order is an intermarket sweep order. Only for stock.",
    )
    oddlot: Optional[bool] = Field(
        default=None,
        description="If the order is an oddlot. Only for stock.",
    )
    nms_rule: Optional[bool] = Field(
        default=None,
        description="True if the order is not subject to NMS Rule 611. Only for stock.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        return v.upper()

    @field_validator("type", mode="before", check_fields=False)
    @classmethod
    def _valiidate_data_type(cls, v):
        """Validate the data type."""
        return (
            "quote" if v == "Q" else "trade" if v == "T" else "break" if v == "B" else v
        )

    @field_validator("date", "timestamp", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime  # noqa
        from pytz import timezone, UTC

        if isinstance(v, str):
            dt = to_datetime(v, utc=True).tz_convert(timezone("America/New_York"))
        else:
            try:
                dt = datetime.fromtimestamp(v / 1000, UTC)
                dt = dt.astimezone(timezone("America/New_York"))
            except Exception:
                if isinstance(v, (int, float)):
                    # Check if the timestamp is in nanoseconds and convert to seconds
                    if v > 1e12:
                        v = v / 1e9  # Convert nanoseconds to seconds
                    dt = datetime.fromtimestamp(v, UTC)
                    dt = dt.astimezone(timezone("America/New_York"))
                else:
                    dt = v
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f%z")

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""

        return values


class TiingoWebSocketConnection(WebSocketConnection):
    """Tiingo WebSocket connection model."""


class TiingoWebSocketFetcher(
    Fetcher[TiingoWebSocketQueryParams, TiingoWebSocketConnection]
):
    """Tiingo WebSocket model."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TiingoWebSocketQueryParams:
        """Transform the query parameters."""
        asset_type = params.get("asset_type")
        feed = params.get("feed")

        if asset_type == "fx" and feed == "trade":
            raise ValueError("FX only supports quote feed.")

        return TiingoWebSocketQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TiingoWebSocketQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Initiailze the WebSocketClient and connect."""
        # pylint: disable=import-outside-toplevel
        from asyncio import sleep

        api_key = credentials.get("tiingo_token") if credentials else ""

        symbol = query.symbol.lower()

        kwargs = {
            "api_key": api_key,
            "asset_type": query.asset_type,
            "feed": query.feed,
            "connect_kwargs": query.connect_kwargs,
        }

        client = WebSocketClient(
            name=query.name,
            module="openbb_tiingo.utils.websocket_client",
            symbol=symbol,
            limit=query.limit,
            results_file=query.results_file,
            table_name=query.table_name,
            save_database=query.save_database,
            data_model=TiingoWebSocketData,
            prune_interval=query.prune_interval,
            export_interval=query.export_interval,
            export_directory=query.export_directory,
            compress_export=query.compress_export,
            sleep_time=query.sleep_time,
            broadcast_host=query.broadcast_host,
            broadcast_port=query.broadcast_port,
            auth_token=query.auth_token,
            **kwargs,
        )

        try:
            client.connect()
        except OpenBBError as e:
            if client.is_running:
                client.disconnect()
            raise e from e

        await sleep(1)

        if getattr(client, "_exception", None):
            exc = client._exception  # pylint: disable=protected-access
            client._exception = None  # pylint: disable=protected-access
            raise OpenBBError(exc)

        if client.is_running:
            return {"client": client}

        client.disconnect()
        raise OpenBBError("Failed to connect to the WebSocket.")

    @staticmethod
    def transform_data(
        data: dict,
        query: TiingoWebSocketQueryParams,
        **kwargs: Any,
    ) -> TiingoWebSocketConnection:
        """Return the client as an instance of Data."""
        return TiingoWebSocketConnection(client=data["client"])

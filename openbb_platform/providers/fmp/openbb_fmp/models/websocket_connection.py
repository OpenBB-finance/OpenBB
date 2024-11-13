"""FMP WebSocket model."""

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_websockets.client import WebSocketClient
from openbb_websockets.models import (
    WebSocketConnection,
    WebSocketData,
    WebSocketQueryParams,
)
from pydantic import Field, field_validator

URL_MAP = {
    "stock": "wss://websockets.financialmodelingprep.com",
    "fx": "wss://forex.financialmodelingprep.com",
    "crypto": "wss://crypto.financialmodelingprep.com",
}


class FmpWebSocketQueryParams(WebSocketQueryParams):
    """FMP WebSocket query parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "asset_type": {
            "multiple_items_allowed": False,
            "choices": ["stock", "fx", "crypto"],
        },
    }

    symbol: str = Field(
        description="The FMP symbol to get data for.",
    )
    asset_type: Literal["stock", "fx", "crypto"] = Field(
        default="crypto",
        description="The asset type associated with the symbol.",
    )


class FmpWebSocketData(WebSocketData):
    """FMP WebSocket data model."""

    __alias_dict__ = {
        "symbol": "s",
        "date": "t",
        "exchange": "e",
        "type": "type",
        "bid_size": "bs",
        "bid_price": "bp",
        "ask_size": "as",
        "ask_price": "ap",
        "last_price": "lp",
        "last_size": "ls",
    }

    exchange: Optional[str] = Field(
        default=None,
        description="The exchange of the data.",
    )
    type: Literal["quote", "trade", "break"] = Field(
        description="The type of data.",
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

    @field_validator("symbol", mode="before")
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        return v.upper()

    @field_validator("type", mode="before", check_fields=False)
    def _valiidate_data_type(cls, v):
        """Validate the data type."""
        return (
            "quote" if v == "Q" else "trade" if v == "T" else "break" if v == "B" else v
        )

    @field_validator("date", mode="before", check_fields=False)
    def _validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pytz import timezone

        if isinstance(v, str):
            dt = datetime.fromisoformat(v)
        try:
            dt = datetime.fromtimestamp(v / 1000)
        except Exception:  # pylint: disable=broad-except
            if isinstance(v, (int, float)):
                # Check if the timestamp is in nanoseconds and convert to seconds
                if v > 1e12:
                    v = v / 1e9  # Convert nanoseconds to seconds
                dt = datetime.fromtimestamp(v)

        return dt.astimezone(timezone("America/New_York"))


class FmpWebSocketConnection(WebSocketConnection):
    """FMP WebSocket connection model."""


class FmpWebSocketFetcher(Fetcher[FmpWebSocketQueryParams, FmpWebSocketConnection]):
    """FMP WebSocket model."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FmpWebSocketQueryParams:
        """Transform the query parameters."""
        return FmpWebSocketQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FmpWebSocketQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> WebSocketClient:
        """Extract data from the WebSocket."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = URL_MAP[query.asset_type]

        symbol = query.symbol.lower()

        kwargs = {
            "url": url,
            "api_key": api_key,
            "connect_kwargs": query.connect_kwargs,
        }

        client = WebSocketClient(
            name=query.name,
            module="openbb_fmp.utils.websocket_client",
            symbol=symbol,
            limit=query.limit,
            results_file=query.results_file,
            table_name=query.table_name,
            save_results=query.save_results,
            data_model=FmpWebSocketData,
            sleep_time=query.sleep_time,
            broadcast_host=query.broadcast_host,
            broadcast_port=query.broadcast_port,
            auth_token=query.auth_token,
            **kwargs,
        )

        try:
            client.connect()
            await asyncio.sleep(2)
            if client._exception:
                raise client._exception
        except OpenBBError as e:
            if client.is_running:
                client.disconnect()
            raise e from e

        if client.is_running:
            return client

        raise OpenBBError("Failed to connect to the WebSocket.")

    @staticmethod
    def transform_data(
        data: WebSocketClient,
        query: FmpWebSocketQueryParams,
        **kwargs: Any,
    ) -> FmpWebSocketConnection:
        """Return the client as an instance of Data."""
        return FmpWebSocketConnection(client=data)

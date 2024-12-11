"""Intrinio WebSocket model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_intrinio.utils.references import TRADE_CONDITIONS, VENUES
from openbb_websockets.client import WebSocketClient
from openbb_websockets.models import (
    WebSocketConnection,
    WebSocketData,
    WebSocketQueryParams,
)
from pydantic import Field, field_validator, model_validator


class IntrinioWebSocketQueryParams(WebSocketQueryParams):
    """Intrinio WebSocket query parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "asset_type": {
            "multiple_items_allowed": False,
            "choices": ["stock"],
        },
        "feed": {
            "multiple_items_allowed": False,
            "choices": ["realtime", "delayed_sip", "nasdaq_basic"],
        },
    }

    symbol: str = Field(
        description="The Intrinio symbol to get data for.",
    )
    asset_type: Literal["stock"] = Field(
        default="stock",
        description="The asset type associated with the symbol.",
    )
    feed: Literal["realtime", "delayed_sip", "nasdaq_basic"] = Field(
        default="realtime",
        description="The feed to get data from.",
    )
    trades_only: bool = Field(
        default=False,
        description="Whether to only get trade data.",
    )


class IntrinioWebSocketData(WebSocketData):
    """Intrinio WebSocket data model."""

    __alias_dict__ = {
        "date": "timestamp",
        "feed": "subprovider",
        "exchange": "market_center",
        "volume": "total_volume",
    }

    exchange: Optional[str] = Field(
        default=None,
        description="The exchange of the data.",
    )
    type: Literal["bid", "ask", "trade"] = Field(
        description="The type of data.",
    )
    price: Optional[float] = Field(
        default=None,
        description="The price of the trade or quote.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    size: Optional[int] = Field(
        default=None,
        description="The size of the trade or quote.",
    )
    volume: Optional[int] = Field(
        default=None,
        description="The total volume of the trade or quote.",
    )
    conditions: Optional[str] = Field(
        default=None,
        description="The condition attached to the trade or quote.",
    )
    is_darkpool: Optional[bool] = Field(
        default=None,
        description="Flag if the trade is reported from an unlit venue.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
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

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def _validate_exchange(cls, v):
        """Validate the exchange."""
        return VENUES.get(v, v)

    @model_validator(mode="before")
    @classmethod
    def _validate_conditions(cls, values):
        """Validate the exchange."""
        new_values = values.copy()
        trade_type = new_values.get("type")
        conditions = new_values.pop("condition", None)

        if trade_type == "trade":
            if not conditions:
                return new_values

            new_conditions = []
            conditions = conditions.replace(" ", "")

            for char in range(  # pylint: disable=consider-using-enumerate
                len(conditions)
            ):
                if trade_type == "trade":
                    new_conditions.append(
                        TRADE_CONDITIONS.get(conditions[char], conditions[char])
                    )

            new_values["conditions"] = "; ".join(new_conditions)
        else:
            new_values["conditions"] = conditions if conditions else None

        return new_values


class IntrinioWebSocketConnection(WebSocketConnection):
    """Intrinio WebSocket connection model."""


class IntrinioWebSocketFetcher(
    Fetcher[IntrinioWebSocketQueryParams, IntrinioWebSocketConnection]
):
    """Intrinio WebSocket Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> IntrinioWebSocketQueryParams:
        """Transform the query parameters."""
        return IntrinioWebSocketQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioWebSocketQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract data from the WebSocket."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        kwargs = {
            "api_key": api_key,
            "feed": query.feed or "realtime",
            "connect_kwargs": query.connect_kwargs,
        }

        client = WebSocketClient(
            name=query.name,
            module="openbb_intrinio.utils.websocket_client",
            symbol=query.symbol,
            limit=query.limit,
            results_file=query.results_file,
            table_name=query.table_name,
            save_results=query.save_results,
            data_model=IntrinioWebSocketData,
            sleep_time=query.sleep_time,
            broadcast_host=query.broadcast_host,
            broadcast_port=query.broadcast_port,
            auth_token=query.auth_token,
            **kwargs,
        )

        try:
            client.connect()
            await asyncio.sleep(2)
            if client._exception:  # pylint: disable=protected-access
                raise client._exception  # pylint: disable=protected-access
        except OpenBBError as e:
            if client.is_running:
                client.disconnect()
            raise e from e

        if client.is_running:
            return {"client": client}

        raise OpenBBError("Failed to connect to the WebSocket.")

    @staticmethod
    def transform_data(
        data: dict,
        query: IntrinioWebSocketQueryParams,
        **kwargs: Any,
    ) -> IntrinioWebSocketConnection:
        """Return the client as an instance of Data."""
        return IntrinioWebSocketConnection(client=data["client"])

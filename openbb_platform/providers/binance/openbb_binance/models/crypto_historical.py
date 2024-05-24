"""Binance Crypto Historical WS Data."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from pydantic import Field
import websockets

from openbb_platform.core.openbb_core.provider.abstract.fetcher import (
    # StreamFetcher,
    Fetcher,
)

# pylint: disable=unused-kwargs


class BinanceCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Binance Crypto Historical Query Params"""

    lifetime: Optional[int] = Field(
        default=60, description="Lifetime of WebSocket in seconds"
    )


class BinanceCryptoHistoricalData(CryptoHistoricalData):
    """Binance Crypto Historical Data."""

    __alias_dict__ = {
        "symbol": "s",
        "close": "c",
        "open": "o",
        "high": "h",
        "low": "l",
        "volume": "v",
    }
    event_type: Optional[str] = Field(
        default=None,
        description="Event type",
        alias="e",
    )
    quote_asset_volume: Optional[str] = Field(
        default=None,
        description="Total traded quote asset volume",
        alias="q",
    )


class BinanceCryptoHistoricalFetcher(Fetcher):
    """Define Binance Crypto Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BinanceCryptoHistoricalQueryParams:
        """Transform the query params."""
        return BinanceCryptoHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BinanceCryptoHistoricalQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> BinanceCryptoHistoricalData:
        """Return the raw data from the Binance endpoint."""
        async with websockets.connect(
            f"wss://stream.binance.com:9443/ws/{query.symbol.lower()}@miniTicker"
        ) as websocket:
            print("Connected to WebSocket server.")
            end_time = datetime.now() + timedelta(seconds=query.lifetime)
            try:
                while datetime.now() < end_time:
                    message = await websocket.recv()
                    data = json.loads(message)
                    transformed_data = BinanceCryptoHistoricalFetcher.transform_data(
                        query, data
                    )
                    # print(transformed_data)
                    yield transformed_data
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")
            finally:
                print("WebSocket connection closed.")

    @staticmethod
    def transform_data(
        query: BinanceCryptoHistoricalQueryParams,
        data: Dict[str, Any],
    ) -> BinanceCryptoHistoricalData:
        """Return the transformed data."""
        data["date"] = (
            datetime.now().isoformat() if "date" not in data else data["date"]
        )
        return BinanceCryptoHistoricalData(**data)


# class BinanceStreamFetcher(StreamFetcher):
#     """Define Binance Stream Fetcher."""

#     @staticmethod
#     def transform_data(data: Dict[str, Any], **kwargs) -> BinanceCryptoHistoricalData:
#         """Transform the incoming data."""
#         if "date" not in data:
#             data["date"] = datetime.now().isoformat()
#         return BinanceCryptoHistoricalData(**data)

#     @classmethod
#     async def process_message(
#         cls, message: str, **kwargs
#     ) -> Optional[BinanceCryptoHistoricalData]:
#         """Process incoming WebSocket messages."""
#         try:
#             json_data = json.loads(message)
#             transformed_data = cls.transform_data(json_data)
#             return transformed_data
#         except Exception as e:
#             print(f"Error processing message from Binance: {e}")
#             return None

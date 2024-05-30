"""Binance Crypto Historical WS Data."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, AsyncIterator, Dict, Literal, Optional

import websockets
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from pydantic import Field

# pylint: disable=unused-argument, arguments-differ

logger = logging.getLogger(__name__)


class BinanceCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Binance Crypto Historical Query Params."""

    tld: Optional[Literal["us", "com"]] = Field(
        default="us", description="Top-level domain of the Binance endpoint."
    )
    lifetime: Optional[int] = Field(
        default=60, description="Lifetime of WebSocket in seconds."
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
    ) -> AsyncGenerator[dict, None]:
        """Return the raw data from the Binance endpoint."""
        async with websockets.connect(
            f"wss://stream.binance.{query.tld}:9443/ws/{query.symbol.lower()}@miniTicker"
        ) as websocket:
            logger.info("Connected to WebSocket server.")
            end_time = datetime.now() + timedelta(seconds=query.lifetime)
            print("Connected to WebSocket server.")
            try:
                chunk = await websocket.recv()
                print(f"Chunk me baby: {chunk}")
                while datetime.now() < end_time:
                    chunk = await websocket.recv()
                    yield json.loads(chunk)
            except websockets.exceptions.ConnectionClosed as e:
                logger.error("WebSocket connection closed.")
                raise e
            finally:
                logger.info("WebSocket connection closed.")

    @staticmethod
    async def atransform_data(
        query: BinanceCryptoHistoricalQueryParams,
        data: Dict[str, Any],
    ) -> AsyncIterator[str]:
        """Return the transformed data."""
        async for chunk in data:
            chunk["date"] = (
                datetime.now().isoformat() if "date" not in chunk else chunk["date"]
            )
            result = BinanceCryptoHistoricalData(**chunk)
            yield result.model_dump_json() + "\n"

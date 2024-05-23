"""Binance Crypto Historical WS Data."""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
)
from pydantic import Field

from openbb_platform.core.openbb_core.provider.abstract.fetcher import StreamFetcher

# pylint: disable=unused-kwargs


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


class BinanceStreamFetcher(StreamFetcher):
    """Define Binance Stream Fetcher."""

    @staticmethod
    def transform_data(data: Dict[str, Any], **kwargs) -> BinanceCryptoHistoricalData:
        """Transform the incoming data."""
        if "date" not in data:
            data["date"] = datetime.now().isoformat()
        return BinanceCryptoHistoricalData(**data)

    @classmethod
    async def process_message(
        cls, message: str, **kwargs
    ) -> Optional[BinanceCryptoHistoricalData]:
        """Process incoming WebSocket messages."""
        try:
            json_data = json.loads(message)
            transformed_data = cls.transform_data(json_data)
            return transformed_data
        except Exception as e:
            print(f"Error processing message from Binance: {e}")
            return None

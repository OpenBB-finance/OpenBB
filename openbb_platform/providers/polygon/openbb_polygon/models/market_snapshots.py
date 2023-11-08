"""Polygon Market Snapshots fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.market_snapshots import (
    MarketSnapshotsData,
    MarketSnapshotsQueryParams,
)
from pydantic import Field, field_validator
from openbb_polygon.utils.helpers import get_data


class PolygonMarketSnapshotsQueryParams(MarketSnapshotsQueryParams):
    """Polygon Market Snapshots Query.

    Source: https://polygon.io/docs/stocks/get_v2_snapshot_locale_us_markets_stocks_tickers
    """


class PolygonMarketSnapshotsData(MarketSnapshotsData):
    """Polygon Market Snapshots Data."""

    vwap: float = Field(
        description="The volume weighted average price of the stock on the current trading day.",
        default=None,
    )
    prev_open: float = Field(
        description="The previous trading session opening price.", default=None
    )
    prev_high: float = Field(
        description="The previous trading session high price.", default=None
    )
    prev_low: float = Field(
        description="The previous trading session low price.", default=None
    )
    prev_volume: float = Field(
        description="The previous trading session volume.", default=None
    )
    prev_vwap: float = Field(
        description="The previous trading session VWAP.", default=None
    )
    last_updated: Optional[datetime] = Field(
        description="The last time the data was updated."
    )
    bid: Optional[float] = Field(description="The current bid price.", default=None)
    bid_size: Optional[int] = Field(description="The current bid size.", default=None)
    ask_size: Optional[int] = Field(description="The current ask size.", default=None)
    ask: Optional[float] = Field(description="The current ask price.", default=None)
    quote_timestamp: Optional[datetime] = Field(
        description="The timestamp of the last quote.", default=None
    )
    last_trade_price: Optional[float] = Field(
        description="The last trade price.", default=None
    )
    last_trade_size: Optional[int] = Field(
        description="The last trade size.", default=None
    )
    last_trade_conditions: Optional[List[int]] = Field(
        description="The last trade condition codes.", default=None
    )
    last_trade_exchange: Optional[int] = Field(
        description="The last trade exchange ID code.", default=None
    )
    last_trade_timestamp: Optional[datetime] = Field(
        description="The last trade timestamp.", default=None
    )

    @field_validator(
        "last_updated",
        "quote_timestamp",
        "last_trade_timestamp",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v):
        """Return formatted datetime."""
        return (
            pd.to_datetime(v, unit="ns", origin="unix", utc=True).tz_convert(
                "US/Eastern"
            )
            if v
            else None
        )


class PolygonMarketSnapshotsFetcher(
    Fetcher[
        PolygonMarketSnapshotsQueryParams,
        List[PolygonMarketSnapshotsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonMarketSnapshotsQueryParams:
        return PolygonMarketSnapshotsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonMarketSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={api_key}"
        response = get_data(url, **kwargs)["tickers"]

        data = []

        # Process and flatten the response from a nested dictionary
        for response_item in response:
            last_quote = response_item.get("lastQuote", {})
            last_trade = response_item.get("lastTrade", {})
            day_data = response_item.get("day", {})
            prev_day = response_item.get("prevDay", {})

            market_data: Dict[str, List[Any]] = {
                "symbol": response_item["ticker"],
                "bid": last_quote.get("p"),
                "ask": last_quote.get("P"),
                "bid_size": last_quote.get("s"),
                "ask_size": last_quote.get("S"),
                "last_trade_price": last_trade.get("p"),
                "last_trade_size": last_trade.get("s"),
                "last_trade_conditions": last_trade.get("c"),
                "last_trade_exchange": last_trade.get("x"),
                "open": day_data.get("o"),
                "high": day_data.get("h"),
                "low": day_data.get("l"),
                "close": day_data.get("c"),
                "change": response_item.get("todaysChange"),
                "change_percent": response_item.get("todaysChangePerc"),
                "volume": day_data.get("v"),
                "vwap": day_data.get("vw"),
                "prev_open": prev_day.get("o"),
                "prev_high": prev_day.get("h"),
                "prev_low": prev_day.get("l"),
                "prev_close": prev_day.get("c"),
                "prev_volume": prev_day.get("v"),
                "prev_vwap": prev_day.get("vw"),
                "last_updated": response_item.get("updated"),
                "quote_timestamp": last_quote.get("t"),
                "last_trade_timestamp": last_trade.get("t"),
            }

            data.append(market_data)

        return data

    @staticmethod
    def transform_data(
        query: PolygonMarketSnapshotsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonMarketSnapshotsData]:
        return [PolygonMarketSnapshotsData.model_validate(d) for d in data]

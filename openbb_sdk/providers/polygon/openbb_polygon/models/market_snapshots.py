"""Polygon Market Snapshots fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.market_snapshots import (
    MarketSnapshotsData,
    MarketSnapshotsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class PolygonMarketSnapshotsQueryParams(MarketSnapshotsQueryParams):
    """Polygon Market Snapshots Query.

    Source: https://polygon.io/docs/stocks/get_v2_snapshot_locale_us_markets_stocks_tickers
    """


class PolygonMarketSnapshotsData(MarketSnapshotsData):
    """Polygon Market Snapshots Data."""

    vwap: Optional[float] = Field(
        description="The volume weighted average price of the stock on the current trading day."
    )
    prev_open: Optional[float] = Field(
        description="The previous trading session opening price."
    )
    prev_high: Optional[float] = Field(
        description="The previous trading session high price."
    )
    prev_low: Optional[float] = Field(
        description="The previous trading session low price."
    )
    prev_volume: Optional[int] = Field(
        description="The previous trading session volume."
    )
    prev_vwap: Optional[float] = Field(description="The previous trading session VWAP.")
    last_updated: Optional[datetime] = Field(
        description="The last time the data was updated."
    )
    bid: Optional[float] = Field(description="The current bid price.")
    bid_size: Optional[int] = Field(description="The current bid size.")
    ask_size: Optional[int] = Field(description="The current ask size.")
    ask: Optional[float] = Field(description="The current ask price.")
    quote_timestamp: Optional[datetime] = Field(
        description="The timestamp of the last quote."
    )
    last_trade_price: Optional[float] = Field(description="The last trade price.")
    last_trade_size: Optional[int] = Field(description="The last trade size.")
    last_trade_conditions: Optional[List[int]] = Field(
        description="The last trade condition codes."
    )
    last_trade_exchange: Optional[int] = Field(
        description="The last trade exchange ID code."
    )
    last_trade_timestamp: Optional[datetime] = Field(
        description="The last trade timestamp."
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

        response = {}
        r = make_request(url)
        if r.status_code == 200 and r.json()["status"] == "OK":
            response = r.json()["tickers"]

        results = pd.DataFrame()

        symbol: List[str] = []
        bid: List[float] = []
        ask: List[float] = []
        bid_size: List[float] = []
        ask_size: List[float] = []
        last_trade_price: List[float] = []
        last_trade_size: List[int] = []
        last_trade_conditions: List[List[int]] = []
        last_trade_exchange: List[int] = []
        open: List[float] = []
        high: List[float] = []
        low: List[float] = []
        close: List[float] = []
        change: List[float] = []
        change_percent: List[float] = []
        volume: List[int] = []
        vwap: List[float] = []
        prev_open: List[float] = []
        prev_high: List[float] = []
        prev_low: List[float] = []
        prev_close: List[float] = []
        prev_volume: List[int] = []
        prev_vwap: List[float] = []
        last_updated: List[int] = []
        quote_timestamp: List[int] = []
        last_trade_timestamp: List[int] = []

        # This process conditionally flattens the response from a nested dictionary.
        if len(response) > 0:
            for i in range(len(response)):
                symbol.append(response[i]["ticker"])
                if (
                    "lastQuote" in response[i]
                ):  # Only returned if the subscription includes quotes
                    bid.append(response[i]["lastQuote"]["p"])
                    ask.append(response[i]["lastQuote"]["P"])
                    bid_size.append(response[i]["lastQuote"]["s"])
                    ask_size.append(response[i]["lastQuote"]["S"])
                    quote_timestamp.append(response[i]["lastQuote"]["t"])
                if (
                    "lastTrade" in response[i]
                ):  # Only returned if the subscription includes trades
                    last_trade_price.append(response[i]["lastTrade"]["p"])
                    last_trade_size.append(response[i]["lastTrade"]["s"])
                    last_trade_conditions.append(response[i]["lastTrade"]["c"])
                    last_trade_exchange.append(response[i]["lastTrade"]["x"])
                    last_trade_timestamp.append(response[i]["lastTrade"]["t"])
                open.append(response[i]["day"]["o"])
                high.append(response[i]["day"]["h"])
                low.append(response[i]["day"]["l"])
                close.append(response[i]["day"]["c"])
                volume.append(response[i]["day"]["v"])
                vwap.append(response[i]["day"]["vw"])
                change_percent.append(response[i]["todaysChangePerc"])
                change.append(response[i]["todaysChange"])
                prev_open.append(response[i]["prevDay"]["o"])
                prev_high.append(response[i]["prevDay"]["h"])
                prev_low.append(response[i]["prevDay"]["l"])
                prev_close.append(response[i]["prevDay"]["c"])
                prev_volume.append(response[i]["prevDay"]["v"])
                prev_vwap.append(response[i]["prevDay"]["vw"])
                last_updated.append(response[i]["updated"])

            columns_standard = [
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "change",
                "change_percent",
                "volume",
                "vwap",
                "prev_open",
                "prev_high",
                "prev_low",
                "prev_close",
                "prev_volume",
                "prev_vwap",
                "last_updated",
            ]
            data_standard = [
                symbol,
                open,
                high,
                low,
                close,
                change,
                change_percent,
                volume,
                vwap,
                prev_open,
                prev_high,
                prev_low,
                prev_close,
                prev_volume,
                prev_vwap,
                last_updated,
            ]
            columns_quote = ["bid", "bid_size", "ask_size", "ask", "quote_timestamp"]
            data_quote = [bid, bid_size, ask_size, ask, quote_timestamp]
            columns_trade = [
                "last_trade_price",
                "last_trade_size",
                "last_trade_conditions",
                "last_trade_exchange",
                "last_trade_timestamp",
            ]
            data_trade = [
                last_trade_price,
                last_trade_size,
                last_trade_conditions,
                last_trade_exchange,
                last_trade_timestamp,
            ]

            data = data_standard
            columns = columns_standard

            if "lastQuote" in response[0]:
                data = data + data_quote
                columns = columns + columns_quote

            if "lastTrade" in response[0]:
                data = data + data_trade
                columns = columns + columns_trade

            results = pd.DataFrame(data=data).transpose()
            results.columns = columns
            results["last_updated"] = pd.DatetimeIndex(
                results["last_updated"], tz="UTC"
            ).values.astype("datetime64[s]")
            results["last_trade_timestamp"] = pd.DatetimeIndex(
                results["last_trade_timestamp"], tz="UTC"
            ).values.astype("datetime64[s]")
            results["quote_timestamp"] = pd.DatetimeIndex(
                results["quote_timestamp"], tz="UTC"
            ).values.astype("datetime64[s]")

        return results.sort_values(by="change_percent", ascending=False).to_dict(
            "records"
        )

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonMarketSnapshotsData]:
        return [PolygonMarketSnapshotsData.parse_obj(d) for d in data]

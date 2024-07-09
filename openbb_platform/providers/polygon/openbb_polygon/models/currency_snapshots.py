"""Polygon Currency Snapshots."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_snapshots import (
    CurrencySnapshotsData,
    CurrencySnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class PolygonCurrencySnapshotsQueryParams(CurrencySnapshotsQueryParams):
    """Polygon Currency Snapshots Query Parameters.

    Source: https://polygon.io/docs/forex/get_v2_snapshot_locale_global_markets_forex_tickers
    """

    __json_schema_extra__ = {"base": {"multiple_items_allowed": True}}


class PolygonCurrencySnapshotsData(CurrencySnapshotsData):
    """Polygon Currency Snapshots Data."""

    vwap: Optional[float] = Field(
        description="The volume-weighted average price.", default=None
    )
    change: Optional[float] = Field(
        description="The change in price from the previous day.",
        default=None,
    )
    change_percent: Optional[float] = Field(
        description="The percentage change in price from the previous day.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    prev_open: Optional[float] = Field(
        description="The previous day's opening price.", default=None
    )
    prev_high: Optional[float] = Field(
        description="The previous day's high price.", default=None
    )
    prev_low: Optional[float] = Field(
        description="The previous day's low price.", default=None
    )
    prev_volume: Optional[float] = Field(
        description="The previous day's volume.", default=None
    )
    prev_vwap: Optional[float] = Field(
        description="The previous day's VWAP.", default=None
    )
    bid: Optional[float] = Field(description="The current bid price.", default=None)
    ask: Optional[float] = Field(description="The current ask price.", default=None)
    minute_open: Optional[float] = Field(
        description="The open price from the most recent minute bar.", default=None
    )
    minute_high: Optional[float] = Field(
        description="The high price from the most recent minute bar.", default=None
    )
    minute_low: Optional[float] = Field(
        description="The low price from the most recent minute bar.", default=None
    )
    minute_close: Optional[float] = Field(
        description="The close price from the most recent minute bar.", default=None
    )
    minute_volume: Optional[float] = Field(
        description="The volume from the most recent minute bar.", default=None
    )
    minute_vwap: Optional[float] = Field(
        description="The VWAP from the most recent minute bar.", default=None
    )
    minute_transactions: Optional[float] = Field(
        description="The number of transactions in the most recent minute bar.",
        default=None,
    )
    quote_timestamp: Optional[datetime] = Field(
        description="The timestamp of the last quote.", default=None
    )
    minute_timestamp: Optional[datetime] = Field(
        description="The timestamp for the start of the most recent minute bar.",
        default=None,
    )
    last_updated: Optional[datetime] = Field(
        description="The last time the data was updated."
    )


class PolygonCurrencySnapshotsFetcher(
    Fetcher[
        PolygonCurrencySnapshotsQueryParams,
        List[PolygonCurrencySnapshotsData],
    ]
):
    """Polygon Currency Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCurrencySnapshotsQueryParams:
        """Transform the query params."""
        return PolygonCurrencySnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonCurrencySnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        api_key = credentials.get("polygon_api_key") if credentials else ""
        url = f"https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers?apiKey={api_key}"
        results = await amake_request(url, **kwargs)
        if results.get("status") != "OK":  # type: ignore[union-attr]
            raise OpenBBError(f"Error: {results.get('status')}")  # type: ignore[union-attr]
        return results.get("tickers", [])  # type: ignore[union-attr]

    @staticmethod
    def transform_data(  # pylint: disable=too-many-locals, too-many-statements
        query: PolygonCurrencySnapshotsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonCurrencySnapshotsData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from openbb_core.provider.utils.helpers import safe_fromtimestamp  # noqa
        from pandas import DataFrame, concat  # noqa

        if not data:
            raise EmptyDataError("No data returned.")
        counter_currencies = (
            query.counter_currencies.upper().split(",")  # type: ignore[union-attr]
            if query.counter_currencies
            else []
        )

        # Filter the data only for the symbols requested.
        df = DataFrame(data)
        df.ticker = df.ticker.str.replace("C:", "")
        new_df = DataFrame()
        for symbol in query.base.split(","):
            temp = (
                df.loc[df["ticker"].str.startswith(symbol)].copy()
                if query.quote_type == "indirect"
                else df.loc[df["ticker"].str.endswith(symbol)].copy()
            )
            temp["base_currency"] = symbol
            temp["counter_currency"] = (
                [d[3:] for d in temp["ticker"]]
                if query.quote_type == "indirect"
                else [d[:3] for d in temp["ticker"]]
            )
            # Filter for the counter currencies, if requested.
            if query.counter_currencies is not None:
                counter_currencies = (  # noqa: F841  # pylint: disable=unused-variable
                    query.counter_currencies
                    if isinstance(query.counter_currencies, list)
                    else query.counter_currencies.split(",")
                )
                temp = (
                    temp.query("`counter_currency`.isin(@counter_currencies)")
                    .set_index("counter_currency")
                    # Sets the counter currencies in the order they were requested.
                    .filter(items=counter_currencies, axis=0)
                    .reset_index()
                )
            # If there are no records, don't concatenate.
            if len(temp) > 0:
                new_df = concat([new_df, temp])
        filtered_data = new_df.to_dict(orient="records")

        if len(filtered_data) == 0 or not filtered_data:
            raise EmptyDataError("No results were found with the parameters requested.")

        results: List[PolygonCurrencySnapshotsData] = []
        # Now unpack the nested object for the filtered results only.
        for item in filtered_data:
            new_item = {}
            new_item["base_currency"] = item.get("base_currency")
            new_item["counter_currency"] = item.get("counter_currency") or item.get(
                "index"
            )
            new_item["change"] = item.get("todaysChange", None)
            change_percent = item.get("todaysChangePerc", None)
            new_item["change_percent"] = (
                change_percent / 100 if change_percent else None
            )
            updated = item.get("updated")
            new_item["last_updated"] = (
                safe_fromtimestamp(updated / 1e9, tz=timezone.utc) if updated else None
            )
            day = item.get("day", {})
            if day:
                new_item["last_rate"] = day.get("c", None)
                new_item["open"] = day.get("o", None)
                new_item["high"] = day.get("h", None)
                new_item["low"] = day.get("l", None)
                new_item["volume"] = day.get("v", None)
                new_item["vwap"] = day.get("vw", None)
            prev_day = item.get("prevDay", {})
            if prev_day:
                new_item["prev_open"] = prev_day.get("o", None)
                new_item["prev_high"] = prev_day.get("h", None)
                new_item["prev_low"] = prev_day.get("l", None)
                new_item["prev_close"] = prev_day.get("c", None)
                new_item["prev_volume"] = prev_day.get("v", None)
                new_item["prev_vwap"] = prev_day.get("vw", None)
            minute = item.get("min", {})
            if minute:
                new_item["minute_open"] = minute.get("o", None)
                new_item["minute_high"] = minute.get("h", None)
                new_item["minute_low"] = minute.get("l", None)
                new_item["minute_close"] = minute.get("c", None)
                new_item["minute_volume"] = minute.get("v", None)
                new_item["minute_transactions"] = minute.get("n", None)
                new_item["minute_vwap"] = minute.get("vw", None)
                min_updated = minute.get("t")
                new_item["minute_timestamp"] = (
                    safe_fromtimestamp(min_updated / 1000, tz=timezone.utc)
                    if min_updated
                    else None
                )
            quote = item.get("lastQuote", {})
            if quote:
                new_item["bid"] = quote.get("b", None)
                new_item["ask"] = quote.get("a", None)
                quote_time = quote.get("t")
                new_item["quote_timestamp"] = (
                    safe_fromtimestamp(quote_time / 1000, tz=timezone.utc)
                    if quote_time
                    else None
                )
            if new_item:
                results.append(PolygonCurrencySnapshotsData.model_validate(new_item))

        return results

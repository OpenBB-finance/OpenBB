"""Tradier Equity Historical Model."""

# pylint: disable = unused-argument

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request, safe_fromtimestamp
from openbb_tradier.utils.constants import INTERVALS_DICT
from pandas import to_datetime
from pydantic import Field
from pytz import timezone


class TradierEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Tradier Equity Historical Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal["1m", "5m", "15m", "1d", "1W", "1M"] = Field(
        description=QUERY_DESCRIPTIONS.get("interval", ""),
        default="1d",
    )
    extended_hours: bool = Field(
        default=False,
        description="Include Pre and Post market data.",
    )


class TradierEquityHistoricalData(EquityHistoricalData):
    """Tradier Equity Historical Data."""

    __alias_dict__ = {"date": "timestamp", "last_price": "price"}

    last_price: Optional[float] = Field(
        default=None, description="The last price of the equity."
    )


class TradierEquityHistoricalFetcher(
    Fetcher[TradierEquityHistoricalQueryParams, List[TradierEquityHistoricalData]]
):
    """Tradier Equity Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TradierEquityHistoricalQueryParams:
        """Transform the query."""
        if params.get("interval") in ["1d", "1W", "1M"]:
            if params.get("start_date") is None:
                params["start_date"] = (datetime.now() - timedelta(days=365)).date()
            if params.get("end_date") is None:
                params["end_date"] = datetime.now().date()

        if params.get("interval") in ["1m", "5m", "15m"]:
            interval_dict = {
                "1m": 20,
                "5m": 55,
                "15m": 55,
            }
            params["start_date"] = (
                datetime.now() - timedelta(days=interval_dict[params["interval"]])
            ).strftime(  # type: ignore
                "%Y-%m-%d"
            )
            params["end_date"] = datetime.now().strftime("%Y-%m-%d")

        return TradierEquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TradierEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tradier endpoint."""
        api_key = credentials.get("tradier_api_key") if credentials else ""
        sandbox = True

        if api_key and credentials.get("tradier_account_type") not in ["sandbox", "live"]:  # type: ignore
            raise ValueError(
                "Invalid account type for Tradier. Must be either 'sandbox' or 'live'."
            )

        if api_key:
            sandbox = (
                credentials.get("tradier_account_type") == "sandbox"
                if credentials
                else False
            )

        BASE_URL = (
            "https://api.tradier.com/"
            if sandbox is False
            else "https://sandbox.tradier.com/"
        )
        HEADERS = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        session_filter = "all" if query.extended_hours is True else "open"
        interval = INTERVALS_DICT[query.interval]
        end_point = "timesales" if query.interval in ["1m", "5m", "15m"] else "history"
        results = []
        start_time = "09:30" if query.extended_hours is False else "00:00"
        end_time = "16:00" if query.extended_hours is False else "20:00"

        async def get_one(symbol):
            """Get data for one symbol."""
            result = []

            url = (
                f"{BASE_URL}v1/markets/{end_point}?symbol={symbol}&interval={interval}"
            )

            if query.interval in ["1m", "5m", "15m"]:
                url += (
                    f"&start={query.start_date}%20{start_time}"  # type: ignore
                    f"&end={query.end_date}%20{end_time}&session_filter={session_filter}"  # type: ignore
                )
            if query.interval in ["1d", "1W", "1M"]:
                url += f"&start={query.start_date}&end={query.end_date}"

            data = await amake_request(url, headers=HEADERS)

            if interval in ["daily", "weekly", "monthly"] and data.get("history"):  # type: ignore
                result = data["history"].get("day")  # type: ignore
                if len(query.symbol.split(",")) > 1:
                    for r in result:
                        r["symbol"] = symbol

            if interval in ["1min", "5min", "15min"] and data.get("series"):  # type: ignore
                result = data["series"].get("data")  # type: ignore
                for r in result:
                    if len(query.symbol.split(",")) > 1:
                        r["symbol"] = symbol
                    _ = r.pop("time")
                    r["timestamp"] = (
                        safe_fromtimestamp(r.get("timestamp"))
                        .replace(microsecond=0)
                        .astimezone(timezone("America/New_York"))
                    )

            if result != []:
                results.extend(result)
            if result == []:
                warn(f"No data found for {symbol}.")

        symbols = query.symbol.split(",")
        tasks = [get_one(symbol) for symbol in symbols]
        await asyncio.gather(*tasks)

        if len(results) == 0:
            raise EmptyDataError("No results found.")

        return results

    @staticmethod
    def transform_data(
        query: TradierEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TradierEquityHistoricalData]:
        """Transform and validate the data."""
        interval = "timestamp" if query.interval in ["1m", "5m", "15m"] else "date"
        return [
            TradierEquityHistoricalData.model_validate(d)
            for d in sorted(data, key=lambda x: x[interval])
            if query.start_date <= to_datetime(d[interval]).date() <= query.end_date
        ]

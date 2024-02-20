"""TMX Equity Historical Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

import pytz
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils.helpers import (
    get_daily_price_history,
    get_intraday_price_history,
    get_weekly_or_monthly_price_history,
)
from pandas import DataFrame, to_datetime
from pydantic import Field, field_validator

_warn = warnings.warn


class TmxEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """
    TMX Equity Historical Query Params.

    Ticker symbols are assumed to be Canadian listings when no suffix is provided.
    ".TO" or ."TSX" are accepted but will automatically be removed.

    US tickers are supported via their composite format: "AAPL:US"

    Canadian Depositary Receipts (CDRs) are: "AAPL:AQL"

    CDRs are the underlying asset for CAD-hedged assets.

    source: https://money.tmx.com
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Union[
        Literal["1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "1W", "1M"], str, int
    ] = Field(
        description=QUERY_DESCRIPTIONS.get("interval", "")
        + " Or, any integer (entered as a string) representing the number of minutes."
        + " Default is daily data."
        + " There is no extended hours data, and intraday data is limited to after April 12 2022.",
        default="day",
    )
    adjustment: Literal["splits_only", "splits_and_dividends", "unadjusted"] = Field(
        description="The adjustment factor to apply. Only valid for daily data.",
        default="splits_only",
    )

    @field_validator("interval", mode="after", check_fields=False)
    @classmethod
    def validate_interval(cls, v):  # pylint: disable=R0911
        """Validate the interval to be valid for the TMX request."""
        if v is None or v == "day":
            return "day"
        if v in ("1M", "1mo", "month"):
            return "month"
        if "m" in v:
            return int(v.replace("m", ""))
        if "h" in v:
            return int(v.replace("h", "")) * 60
        if v == "1d":
            return "day"
        if v in ("1W", "1w", "week"):
            return "week"
        if v.isnumeric():
            return int(v)
        raise ValueError(f"Invalid interval: {v}")


class TmxEquityHistoricalData(EquityHistoricalData):
    """TMX Equity Historical Data."""

    __alias_dict__ = {
        "date": "datetime",
        "open": "openPrice",
        "close": "closePrice",
        "transactions_value": "tradeValue",
        "transactions": "numberOfTrade",
        "change_percent": "changePercent",
    }

    vwap: Optional[float] = Field(
        description="Volume weighted average price for the day.", default=None
    )
    change: Optional[float] = Field(description="Change in price.", default=None)
    change_percent: Optional[float] = Field(
        description="Change in price, as a normalized percentage.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    transactions: Optional[int] = Field(
        description="Total number of transactions recorded.", default=None
    )
    transactions_value: Optional[float] = Field(
        description="Nominal value of recorded transactions.", default=None
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=W0221
        """Validate the datetime format."""
        try:
            dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S%z")
            return dt.astimezone(pytz.timezone("America/New_York"))
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d")


class TmxEquityHistoricalFetcher(
    Fetcher[TmxEquityHistoricalQueryParams, List[TmxEquityHistoricalData]]
):
    """TMX Equity Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEquityHistoricalQueryParams:
        """Transform the query."""
        adjustment = params.get("adjustment")
        if (
            adjustment is not None
            and adjustment != "splits_only"
            and params.get("interval") not in ["day", "1d"]
        ):
            _warn("Adjustment parameter is only available for daily data.")
        return TmxEquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results: List[Dict] = []
        symbols = query.symbol.split(",")

        async def create_task(symbol, results):
            """Makes a POST request to the TMX GraphQL endpoint for a single ticker."""
            data: List[Dict] = []
            # A different request is used for each type of interval.
            if query.interval == "day":
                data = await get_daily_price_history(
                    symbol,
                    start_date=query.start_date,
                    end_date=query.end_date,
                    adjustment=query.adjustment,
                )
            if query.interval in ("week", "month"):
                data = await get_weekly_or_monthly_price_history(
                    symbol,
                    start_date=query.start_date,
                    end_date=query.end_date,
                    interval=query.interval,  # type: ignore
                )
            if isinstance(query.interval, int):
                data = await get_intraday_price_history(
                    symbol,
                    interval=query.interval,
                    start_date=query.start_date,
                    end_date=query.end_date,
                )

            if data != []:
                # Add the symbol to the data for multi-ticker support.
                data = [{**d, "symbol": symbol} for d in data]
                results.extend(data)

            if data == []:
                _warn(f"No data found for {symbol}.")

            return results

        tasks = [create_task(symbol, results) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: TmxEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxEquityHistoricalData]:
        """Return the transformed data."""

        results = DataFrame(data)
        if results.empty or len(results) == 0:
            raise EmptyDataError()

        # Handle the date formatting differences.
        results = results.rename(columns={"dateTime": "datetime"})
        if query.interval != "day":
            results["datetime"] = to_datetime(results["datetime"], utc=True)
            if query.interval in ("week", "month"):
                results["datetime"] = results["datetime"].dt.strftime("%Y-%m-%d")
            else:
                results["datetime"] = results["datetime"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S%z"
                )
        if query.interval == "day":
            results["datetime"] = to_datetime(results["datetime"]).dt.strftime(
                "%Y-%m-%d"
            )

        symbols = query.symbol.split(",")
        # If there are multiple symbols, sort the data by datetime and symbol.
        if len(symbols) > 1:
            results = results.set_index(["datetime", "symbol"]).sort_index()
            results = results.reset_index()
        # If there is only one symbol, drop the symbol column.
        if len(symbols) == 1:
            results = results.drop(columns=["symbol"])
        # Normalizes the percent change values.
        if "changePercent" in results.columns:
            results["changePercent"] = results["changePercent"].astype(float) / 100
        # For the week beginning 2011-09-12 replace the openPrice NaN with 0 because of 9/11.
        if query.interval == "week":
            results["open"] = results["open"].fillna(0)
        # Convert any NaN values to None.
        results = results.fillna(value="N/A").replace("N/A", None)

        return [
            TmxEquityHistoricalData.model_validate(d)
            for d in results.to_dict("records")
        ]

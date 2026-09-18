"""TMX Equity Historical Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import literal_choices


class TmxEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """TMX Equity Historical Query Params."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "adjustment": {
            "x-widget_config": {
                "options": literal_choices(
                    ("splits_only", "splits_and_dividends", "unadjusted")
                )
            }
        },
    }

    interval: (
        Literal["1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "1W", "1M"]
        | str
        | int
    ) = Field(
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
        raise OpenBBError(f"Invalid interval: {v}")


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

    high: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("high", "")
        + " The feed leaves it empty on a handful of historical foreign bars.",
    )
    low: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("low", "")
        + " The feed leaves it empty on a handful of historical foreign bars.",
    )
    vwap: float | None = Field(
        description="Volume weighted average price for the day.", default=None
    )
    change: float | None = Field(description="Change in price.", default=None)
    change_percent: float | None = Field(
        description="Change in price, as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    transactions: int | None = Field(
        description="Total number of transactions recorded.", default=None
    )
    transactions_value: float | None = Field(
        description="Nominal value of recorded transactions.", default=None
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=W0221
        """Validate the datetime format."""
        # pylint: disable=import-outside-toplevel
        from zoneinfo import ZoneInfo

        if isinstance(v, (datetime, dateType)):
            return v if v.hour != 0 and v.minute != 0 and v.second != 0 else v.date()
        try:
            dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S%z")
            return dt.astimezone(ZoneInfo("America/New_York"))
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d")


class TmxEquityHistoricalFetcher(
    Fetcher[TmxEquityHistoricalQueryParams, list[TmxEquityHistoricalData]]
):
    """TMX Equity Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquityHistoricalQueryParams:
        """Transform the query."""
        adjustment = params.get("adjustment")
        if (
            adjustment is not None
            and adjustment != "splits_only"
            and params.get("interval") not in ["day", "1d"]
        ):
            warn("Adjustment parameter is only available for daily data.")
        return TmxEquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_tmx.utils.helpers import (  # noqa
            get_daily_price_history,
            get_intraday_price_history,
            get_weekly_or_monthly_price_history,
        )

        results: list[dict] = []
        symbols = query.symbol.split(",")

        async def create_task(symbol, results):
            """Make a POST request to the TMX GraphQL endpoint for a single ticker."""
            data: list[dict] = []
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
                    interval=query.interval,
                )
            if isinstance(query.interval, int):
                data = await get_intraday_price_history(
                    symbol,
                    interval=query.interval,
                    start_date=query.start_date,
                    end_date=query.end_date,
                )

            if data != []:
                data = [{**d, "symbol": symbol} for d in data]
                results.extend(data)

            if data == []:
                warn(f"No data found for {symbol}.")

            return results

        tasks = [create_task(symbol, results) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: TmxEquityHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquityHistoricalData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, to_datetime

        results = DataFrame(data)
        if results.empty or len(results) == 0:
            raise EmptyDataError()

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
        if len(symbols) > 1:
            results = results.set_index(["datetime", "symbol"]).sort_index()
            results = results.reset_index()
        if len(symbols) == 1:
            results = results.drop(columns=["symbol"])
        if "changePercent" in results.columns:
            results["changePercent"] = results["changePercent"].astype(float) / 100
        if query.interval == "week":
            results["open"] = results["open"].fillna(0)
        from openbb_tmx.utils.helpers import purge_nulls

        results = purge_nulls(results)

        return [
            TmxEquityHistoricalData.model_validate(d)
            for d in results.to_dict("records")
        ]

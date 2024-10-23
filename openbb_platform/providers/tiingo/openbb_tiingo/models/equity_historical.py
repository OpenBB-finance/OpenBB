"""Tiingo Equity Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional, Union
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
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field


class TiingoEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Tiingo Equity Historical Price Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    __alias_dict__ = {
        "start_date": "startDate",
        "end_date": "endDate",
    }
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {
            "choices": [
                "1m",
                "5m",
                "15m",
                "30m",
                "90m",
                "1h",
                "2h",
                "4h",
                "1d",
                "1W",
                "1M",
                "1Y",
            ]
        },
    }

    interval: Union[
        Literal[
            "1m", "5m", "15m", "30m", "90m", "1h", "2h", "4h", "1d", "1W", "1M", "1Y"
        ],
        str,
    ] = Field(default="1d", description=QUERY_DESCRIPTIONS.get("interval", ""))


class TiingoEquityHistoricalData(EquityHistoricalData):
    """Tiingo Equity Historical Price Data."""

    __alias_dict__ = {
        "adj_open": "adjOpen",
        "adj_high": "adjHigh",
        "adj_low": "adjLow",
        "adj_close": "adjClose",
        "adj_volume": "adjVolume",
        "split_ratio": "splitFactor",
        "dividend": "divCash",
    }

    adj_open: Optional[float] = Field(
        default=None,
        description="The adjusted open price.",
    )
    adj_high: Optional[float] = Field(
        default=None,
        description="The adjusted high price.",
    )
    adj_low: Optional[float] = Field(
        default=None,
        description="The adjusted low price.",
    )
    adj_close: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("adj_close", ""),
    )
    adj_volume: Optional[float] = Field(
        default=None,
        description="The adjusted volume.",
    )
    split_ratio: Optional[float] = Field(
        default=None,
        description="Ratio of the equity split, if a split occurred.",
    )
    dividend: Optional[float] = Field(
        default=None,
        description="Dividend amount, if a dividend was paid.",
    )


class TiingoEquityHistoricalFetcher(
    Fetcher[
        TiingoEquityHistoricalQueryParams,
        list[TiingoEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TiingoEquityHistoricalQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoEquityHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    async def aextract_data(
        query: TiingoEquityHistoricalQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Tiingo endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_tiingo.utils.helpers import get_data

        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = (
            "https://api.tiingo.com/tiingo/daily"
            if query.interval in ["1d", "1W", "1M", "1Y"]
            else "https://api.tiingo.com/iex"
        )
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "interval"]
        )
        frequency_dict = {
            "1d": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "1Y": "annually",
        }
        frequency = (
            frequency_dict.get(query.interval, "")
            if query.interval in frequency_dict
            else query.interval
        )
        cols_str = "&columns=open,high,low,close,volume"

        if frequency.endswith("m"):
            frequency = f"{frequency[:-1]}min"
            query_str = query_str + cols_str
        elif frequency == "h":
            frequency = f"{frequency[:-1]}hour"
            query_str = query_str + cols_str

        results: list = []
        messages: list = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = f"{base_url}/{symbol}/prices?{query_str}&resampleFreq={frequency}&token={api_key}"
            data = None
            try:
                data = await get_data(url)
            except UnauthorizedError as e:
                raise e from e
            except OpenBBError as e:
                if (
                    e.original
                    and isinstance(e.original, str)
                    and "ticker" in e.original.lower()
                ):
                    messages.append(e.original)
                else:
                    messages.append(f"{symbol}: {e.original}")

            if isinstance(data, list):
                if "," in query.symbol:
                    for d in data:
                        d["symbol"] = symbol
                results.extend(data)

        symbols = query.symbol.split(",")
        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results and messages:
            raise OpenBBError(f"{messages}")

        if not results and not messages:
            raise EmptyDataError("The request was returned empty.")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: TiingoEquityHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TiingoEquityHistoricalData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime
        from pytz import timezone

        results: list[TiingoEquityHistoricalData] = []
        for item in data:
            # If the data is intraday, it comes from IEX and the TZ should be localized to America/New_York
            if query.interval in ["1d", "1W", "1M", "1Y"]:
                item["date"] = to_datetime(item["date"]).date()
            else:
                item["date"] = to_datetime(item["date"], utc=True).tz_convert(
                    timezone("America/New_York")
                )

            results.append(TiingoEquityHistoricalData.model_validate(item))

        return results

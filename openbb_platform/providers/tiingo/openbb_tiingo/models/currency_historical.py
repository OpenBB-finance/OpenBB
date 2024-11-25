"""Tiingo Currency Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field


class TiingoCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Tiingo Currency Historical Price Query.

    Source: https://www.tiingo.com/documentation/forex
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
                "5d",
                "21d",
            ]
        },
    }

    interval: Union[
        Literal[
            "1m",
            "5m",
            "15m",
            "30m",
            "90m",
            "1h",
            "2h",
            "4h",
            "1d",
            "5d",
            "21d",
        ],
        str,
    ] = Field(default="1d", description=QUERY_DESCRIPTIONS.get("interval", ""))


class TiingoCurrencyHistoricalData(CurrencyHistoricalData):
    """Tiingo Currency Historical Price Data."""

    __alias_dict__ = {"symbol": "ticker"}


class TiingoCurrencyHistoricalFetcher(
    Fetcher[
        TiingoCurrencyHistoricalQueryParams,
        list[TiingoCurrencyHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TiingoCurrencyHistoricalQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TiingoCurrencyHistoricalQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Tiingo endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_tiingo.utils.helpers import get_data
        from pandas import to_datetime

        api_key = credentials.get("tiingo_token") if credentials else ""
        base_url = "https://api.tiingo.com/tiingo/fx"
        query_str = get_querystring(
            query.model_dump(by_alias=False), ["tickers", "resampleFreq"]
        )

        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "interval"]
        )

        if query.interval.endswith("m"):
            frequency = f"{query.interval[:-1]}min"
        elif query.interval.endswith("h"):
            frequency = f"{query.interval[:-1]}hour"
        elif query.interval.endswith("d"):
            frequency = f"{query.interval[:-1]}day"
        else:
            frequency = "1day"

        results: list = []
        messages: list = []
        symbols = query.symbol.split(",")

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
                for d in data:
                    ticker = d.pop("ticker", None)
                    if ticker and len(symbols) > 1:
                        d["ticker"] = d["ticker"].upper()

                    if query.interval.endswith("d"):
                        d["date"] = to_datetime(d["date"]).date()
                    else:
                        d["date"] = to_datetime(d["date"], utc=True)

                results.extend(data)

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
        query: TiingoCurrencyHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TiingoCurrencyHistoricalData]:
        """Return the transformed data."""
        return sorted(
            [TiingoCurrencyHistoricalData.model_validate(d) for d in data],
            key=lambda x: x.date,
        )

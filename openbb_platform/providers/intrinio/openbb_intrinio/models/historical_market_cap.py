"""Intrinio Historical Market Cap Model."""

# pylint: disable=unused-argument
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_market_cap import (
    HistoricalMarketCapData,
    HistoricalMarketCapQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class IntrinioHistoricalMarketCapQueryParams(HistoricalMarketCapQueryParams):
    """Intrinio Historical MarketCap Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_historical_data_v2
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {
            "multiple_items_allowed": False,
            "choices": ["day", "week", "month", "quarter", "year"],
        },
    }

    interval: Literal["day", "week", "month", "quarter", "year"] = Field(
        default="day",
    )


class IntrinioHistoricalMarketCapData(HistoricalMarketCapData):
    """Intrinio Historical MarketCap Data."""

    __alias_dict__ = {
        "market_cap": "value",
    }


class IntrinioHistoricalMarketCapFetcher(
    Fetcher[
        IntrinioHistoricalMarketCapQueryParams,
        list[IntrinioHistoricalMarketCapData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: dict[str, Any]
    ) -> IntrinioHistoricalMarketCapQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = datetime(
                2007,
                1,
                1,
            ).date()
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioHistoricalMarketCapQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioHistoricalMarketCapQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  #  noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_intrinio.utils.helpers import response_callback
        from warnings import warn

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com/historical_data/"
        frequency = f"frequency={query.interval}ly&" if query.interval != "day" else ""
        start_date = query.start_date
        end_date = query.end_date
        results: list = []
        messages: list = []
        symbols = query.symbol.split(",")

        async def get_one(symbol):
            """Get data for one symbol."""
            url_params = (
                f"{symbol}/marketcap?{frequency}start_date={start_date}"
                f"&end_date={end_date}&page_size=10000"
                f"&api_key={api_key}"
            )
            url = f"{base_url}{url_params}"
            try:
                response = await amake_request(url, response_callback=response_callback)
            except OpenBBError as e:
                if "Cannot look up this item/identifier combination" in str(e):
                    msg = f"Symbol not found: {symbol}"
                    messages.append(msg)
                    return
                raise e from e

            if not isinstance(response, dict):
                raise OpenBBError(
                    f"Unexpected response format, expected a dictionary, got {response.__class__.__name__}"
                )

            if not response:
                msg = f"No data found for symbol: {symbol}"
                messages.append(msg)

            if response.get("historical_data"):
                data = response.get("historical_data", {})
                result = [
                    {"symbol": symbol, **item} for item in data if item.get("value")
                ]
                results.extend(result)

            return

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if messages and not results:
            raise OpenBBError(messages)

        if messages and results:
            for message in messages:
                warn(message)

        if not results:
            raise EmptyDataError("The response was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: IntrinioHistoricalMarketCapQueryParams, data: list[dict], **kwargs: Any
    ) -> list[IntrinioHistoricalMarketCapData]:
        """Return the transformed data."""
        return [
            IntrinioHistoricalMarketCapData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"])
        ]

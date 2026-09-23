"""Cboe Index Historical Model."""

from typing import Any, Literal
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_cboe.utils.constants import INDEX_CHOICES_ENDPOINT


class CboeIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """Cboe Index Historical Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INDEX_CHOICES_ENDPOINT,
                "style": {"popupWidth": 600},
            },
        },
        "interval": {"choices": ["1m", "1d"]},
    }

    interval: Literal["1m", "1d"] = Field(
        default="1d",
        description=(
            QUERY_DESCRIPTIONS.get("interval", "")
            + " The most recent trading day is not including in daily historical data."
            + " Intraday data is only available for the most recent trading day at 1 minute intervals."
        ),
    )
    use_cache: bool = Field(
        default=True,
        description="When True, the company directories will be cached for 24 hours and are used to validate symbols."
        + " The results of the function are not cached. Set as False to bypass.",
    )


class CboeIndexHistoricalData(IndexHistoricalData):
    """Cboe Index Historical Data."""

    __alias_dict__ = {
        "volume": "stock_volume",
    }

    calls_volume: float | None = Field(
        default=None,
        description="Number of calls traded during the most recent trading period. Only valid if interval is 1m.",
    )
    puts_volume: float | None = Field(
        default=None,
        description="Number of puts traded during the most recent trading period. Only valid if interval is 1m.",
    )
    total_options_volume: float | None = Field(
        default=None,
        description="Total number of options traded during the most recent trading period. Only valid if interval is 1m.",
    )


class CboeIndexHistoricalFetcher(
    Fetcher[
        CboeIndexHistoricalQueryParams,
        list[CboeIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeIndexHistoricalQueryParams:
        """Transform the query."""
        from datetime import timedelta

        from openbb_cboe.utils.helpers import ny_now

        transformed_params = params.copy()
        now = ny_now()

        if (
            len(params.get("symbol", "").split(",")) > 1
            and params.get("start_date") is None
        ):
            transformed_params["start_date"] = (now - timedelta(days=720)).strftime(
                "%Y-%m-%d"
            )

        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = "1950-01-01"

        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = now.strftime("%Y-%m-%d")

        return CboeIndexHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Cboe endpoint."""
        from asyncio import gather

        from openbb_core.provider.utils.helpers import amake_requests

        from openbb_cboe.utils.helpers import (
            TICKER_EXCEPTIONS,
            get_index_directory,
            get_index_history,
        )

        symbols = query.symbol.split(",")

        if query.interval == "1d":
            histories = await gather(
                *[
                    get_index_history(symbol, use_cache=query.use_cache)
                    for symbol in symbols
                ]
            )

            return [
                {"symbol": symbol, "data": history}
                for symbol, history in zip(symbols, histories)
            ]

        indexes = await get_index_directory(use_cache=query.use_cache)
        indexes = indexes.set_index("index_symbol")
        eu_indexes = indexes[indexes["source"] == "eu_proprietary_index"]

        def _generate_intraday_url(symbol: str) -> str:
            """Generate the intraday chart URL for the data."""
            if symbol.replace("^", "") in TICKER_EXCEPTIONS:
                warn(
                    "Only the most recent trading day is available for this ticker, "
                    + symbol
                )

            if symbol.replace("^", "") in eu_indexes.index:
                return (
                    "https://cdn.cboe.com/api/global/european_indices/"
                    + f"intraday_chart_data/{symbol.replace('^', '')}.json"
                )

            base_url = "https://cdn.cboe.com/api/global/delayed_quotes/charts/intraday"

            return (
                base_url + f"/_{symbol.replace('^', '')}.json"
                if symbol.replace("^", "") in TICKER_EXCEPTIONS
                or symbol.replace("^", "") in indexes.index
                else base_url + f"/{symbol.replace('^', '')}.json"
            )

        urls = [_generate_intraday_url(symbol) for symbol in symbols]

        return await amake_requests(urls, **kwargs)

    @staticmethod
    def transform_data(
        query: CboeIndexHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[CboeIndexHistoricalData]:
        """Transform the data to the standard format."""
        from datetime import timedelta

        from pandas import DataFrame, Series, concat, to_datetime

        if not data:
            raise EmptyDataError()

        results = DataFrame()
        symbols = query.symbol.split(",")

        for i, item in enumerate(data):
            _symbol = symbols[i]
            _temp = item["data"]

            if query.interval == "1d":
                result = DataFrame(_temp)
                result["date"] = to_datetime(
                    result["date"], format="%m/%d/%Y"
                ).dt.strftime("%Y-%m-%d")
            else:
                _datetime = Series([d["datetime"] for d in _temp]).rename("date")
                _price = DataFrame(d["price"] for d in _temp)
                result = _price.join(_datetime)

            if "volume" in result.columns:
                result = result.drop(columns="volume")

            result["symbol"] = _symbol.replace("_", "").replace("^", "")
            result = result.set_index("date")
            results = concat([results, result])

        results = results.set_index("symbol", append=True).sort_index()

        for c in ["open", "high", "low", "close"]:
            if c in results.columns:
                results[c] = results[c].astype(float).replace(0, None)

        output = results.dropna(how="all", axis=1).reset_index()

        if len(symbols) == 1:
            output = output.drop(columns="symbol")

        output = output[
            (to_datetime(output["date"]) >= to_datetime(query.start_date))  # ty: ignore[no-matching-overload]
            & (
                to_datetime(output["date"])
                <= to_datetime(query.end_date + timedelta(days=1))  # ty: ignore[unsupported-operator]
            )
        ]

        return [
            CboeIndexHistoricalData.model_validate(d) for d in output.to_dict("records")
        ]

"""Cboe Market Indices Model."""

import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_index_directory,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_requests
from pandas import DataFrame, Series, concat, to_datetime
from pydantic import Field

_warn = warnings.warn


class CboeIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """CBOE Market Indices Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

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
    """CBOE Market Indices Data."""

    __alias_dict__ = {
        "volume": "stock_volume",
    }

    calls_volume: Optional[float] = Field(
        default=None,
        description="Number of calls traded during the most recent trading period. Only valid if interval is 1m.",
    )
    puts_volume: Optional[float] = Field(
        default=None,
        description="Number of puts traded during the most recent trading period. Only valid if interval is 1m.",
    )
    total_options_volume: Optional[float] = Field(
        default=None,
        description="Total number of options traded during the most recent trading period. Only valid if interval is 1m.",
    )


class CboeIndexHistoricalFetcher(
    Fetcher[
        CboeIndexHistoricalQueryParams,
        List[CboeIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeIndexHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        now = datetime.now()
        if (
            len(params.get("symbol", "").split(",")) > 1
            and params.get("start_date") is None
        ):
            transformed_params["start_date"] = (
                transformed_params["start_date"]
                if transformed_params["start_date"]
                else (now - timedelta(days=720)).strftime("%Y-%m-%d")
            )
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                transformed_params["start_date"]
                if transformed_params.get("start_date")
                else "1950-01-01"
            )
        if params.get("end_date") is None:
            transformed_params["end_date"] = (
                transformed_params["end_date"]
                if transformed_params.get("end_date")
                else now.strftime("%Y-%m-%d")
            )

        return CboeIndexHistoricalQueryParams(**transformed_params)

    # pylint: disable=unused-argument
    @staticmethod
    async def aextract_data(
        query: CboeIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Cboe endpoint."""
        symbols = query.symbol.split(",")
        INDEXES = await get_index_directory(use_cache=query.use_cache)
        INDEXES = INDEXES.set_index("index_symbol")
        # Create a list of European indices.
        EU_INDEXES = INDEXES[INDEXES["source"] == "eu_proprietary_index"]

        INTERVAL_DICT = {"1m": "intraday", "1d": "historical"}

        def _generate_historical_prices_url(
            symbol,
            interval_type: Literal["intraday", "historical"] = "historical",
        ) -> str:
            """Generate the URL for the data."""
            if symbol.replace("^", "") in TICKER_EXCEPTIONS:
                interval_type = "intraday" if len(symbols) == 1 else "historical"
                _warn(
                    "Only the most recent trading day is available for this ticker, "
                    + symbol
                )
            if symbol.replace("^", "") in EU_INDEXES.index:
                base_url = "https://cdn.cboe.com/api/global/european_indices/"
                url = (
                    base_url + "index_history/"
                    if interval_type == "historical"
                    else base_url + "intraday_chart_data/"
                )
                url += f"{symbol.replace('^', '')}.json"
            else:
                base_url: str = (
                    f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{interval_type}"
                )
                url = (
                    base_url + f"/_{symbol.replace('^', '')}.json"
                    if symbol.replace("^", "") in TICKER_EXCEPTIONS
                    or symbol.replace("^", "") in INDEXES.index
                    else base_url + f"/{symbol.replace('^', '')}.json"
                )

            return url

        urls = [
            _generate_historical_prices_url(symbol, INTERVAL_DICT[query.interval])
            for symbol in symbols
        ]

        return await amake_requests(urls, **kwargs)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: CboeIndexHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeIndexHistoricalData]:
        """Transform the data to the standard format."""
        if not data:
            raise EmptyDataError()
        results = DataFrame()
        symbols = query.symbol.split(",")
        # Results will be different depending on the interval.
        # We will also parse the output from multiple symbols.
        for i, item in enumerate(data):
            result = DataFrame()
            _symbol = symbols[i]
            _temp = item["data"]
            if query.interval == "1d":
                result = DataFrame(_temp)
                result["symbol"] = _symbol.replace("_", "").replace("^", "")
                result = result.set_index("date")
                # Remove the volume column if it exists because volume will a string 0.
                if "volume" in result.columns:
                    result = result.drop(columns="volume")
                results = concat([results, result])
            if query.interval == "1m":
                _datetime = Series([d["datetime"] for d in _temp]).rename("date")
                _price = DataFrame(d["price"] for d in _temp)
                result = _price.join(_datetime)
                result["symbol"] = _symbol.replace("_", "").replace("^", "")
                result = result.set_index("date")
                results = concat([results, result])
        results = results.set_index("symbol", append=True).sort_index()

        for c in ["open", "high", "low", "close"]:
            if c in results.columns:
                results[c] = results[c].astype(float).replace(0, None)

        output = results.dropna(how="all", axis=1).reset_index()

        # When there is only one ticker symbol, the symbol column is redundant.
        if len(query.symbol.split(",")) == 1:
            output = output.drop(columns="symbol")
        # Finally, we apply the user-specified date range because it is not filtered at the source.
        output = output[
            (to_datetime(output["date"]) >= to_datetime(query.start_date))
            & (
                to_datetime(output["date"])
                <= to_datetime(query.end_date + timedelta(days=1))
            )
        ]
        return [
            CboeIndexHistoricalData.model_validate(d) for d in output.to_dict("records")
        ]

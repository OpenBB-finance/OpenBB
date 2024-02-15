"""Cboe Equity Historical Price Model."""

import contextlib
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_index_directory,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_requests
from pandas import DataFrame, Series, concat, to_datetime
from pydantic import Field

_warn = warnings.warn


class CboeEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """
    Cboe Equity Historical Price Query

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


class CboeEquityHistoricalData(EquityHistoricalData):
    """Cboe Equity Historical Price Data."""

    __alias_dict__ = {
        "volume": "stock_volume",
    }

    calls_volume: Optional[int] = Field(
        default=None,
        description="Number of calls traded during the most recent trading period. Only valid if interval is 1m.",
    )
    puts_volume: Optional[int] = Field(
        default=None,
        description="Number of puts traded during the most recent trading period. Only valid if interval is 1m.",
    )
    total_options_volume: Optional[int] = Field(
        default=None,
        description="Total number of options traded during the most recent trading period. Only valid if interval is 1m.",
    )


class CboeEquityHistoricalFetcher(
    Fetcher[
        CboeEquityHistoricalQueryParams,
        List[CboeEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEquityHistoricalQueryParams:
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

        return CboeEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: CboeEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Cboe endpoint."""

        symbols = query.symbol.split(",")
        INDEXES = await get_index_directory(use_cache=query.use_cache)
        INDEXES = INDEXES.set_index("index_symbol")
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

    @staticmethod
    def transform_data(
        query: CboeEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeEquityHistoricalData]:
        """Transform the data to the standard format."""
        if not data:
            raise EmptyDataError()
        results = DataFrame()
        # Results will be different depending on the interval.
        # We will also parse the output from multiple symbols.
        for item in data:
            result = DataFrame()
            _symbol = item["symbol"]
            _temp = item["data"]
            if query.interval == "1d":
                result = DataFrame(_temp)
                result["symbol"] = _symbol.replace("_", "").replace("^", "")
                result = result.set_index("date")
                results = concat([results, result])
            if query.interval == "1m":
                _datetime = Series([d["datetime"] for d in _temp]).rename("date")
                _price = DataFrame(d["price"] for d in _temp)
                _volume = DataFrame(d["volume"] for d in _temp)
                result = _price.join([_volume, _datetime])
                result["symbol"] = _symbol.replace("_", "").replace("^", "")
                result = result.set_index("date")
                results = concat([results, result])
        results = results.set_index("symbol", append=True).sort_index()
        # There are some bad data points in the open/high/low results that will break things.
        for c in results.columns:
            # Some symbols do not have volume data, and some intraday symbols don't have options.
            if c in ["volume", "puts_volume", "calls_volume", "total_options_volume"]:
                results[c] = results[c].astype(float).astype("int64")
                results = (
                    results.drop(columns=c)
                    if results[c].sum() == 0 and c != "volume"
                    else results
                )
            # Sub-penny prices are not warranted for any of the assets returned.
            if c in ["open", "high", "low", "close"]:
                with contextlib.suppress(Exception):
                    results[c] = results[c].astype(float)
                    results[c] = round(results[c], 2)
        output = results.dropna(how="all", axis=1).reset_index()
        output = output[output["open"] > 0]
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
            CboeEquityHistoricalData.model_validate(d)
            for d in output.to_dict("records")
        ]

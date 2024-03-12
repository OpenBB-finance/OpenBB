"""FMP Index Historical Model."""

# pylint: disable=unused-argument

import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
    get_querystring,
)
from openbb_fmp.utils.helpers import get_interval
from pydantic import Field

_warn = warnings.warn


class FMPIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """FMP Index Historical Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class FMPIndexHistoricalData(IndexHistoricalData):
    """FMP Index Historical Data."""

    vwap: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close, as a normalized percent.",
        alias="changeOverTime",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPIndexHistoricalFetcher(
    Fetcher[
        FMPIndexHistoricalQueryParams,
        List[FMPIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIndexHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPIndexHistoricalQueryParams.model_validate(transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        interval = get_interval(query.interval)

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol"])

        def get_url_params(symbol: str) -> str:
            url_params = f"{symbol}?{query_str}&apikey={api_key}"
            url = f"{base_url}/historical-chart/{interval}/{url_params}"
            if interval == "1day":
                url = f"{base_url}/historical-price-full/{url_params}"
            return url

        # if there are more than 20 symbols, we need to increase the timeout
        if len(query.symbol.split(",")) > 20:
            kwargs.update({"preferences": {"request_timeout": 30}})

        async def callback(response: ClientResponse, _: Any) -> List[Dict]:
            data = await response.json()
            symbol = response.url.parts[-1]
            results = []
            if not data:
                _warn(f"No data found the the symbol: {symbol}")
                return results

            if isinstance(data, dict):
                results = data.get("historical", [])
            if isinstance(data, list):
                results = data

            if "," in query.symbol:
                for d in results:
                    d["symbol"] = symbol
            return results

        urls = [get_url_params(symbol) for symbol in query.symbol.split(",")]
        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIndexHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPIndexHistoricalData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError()

        # Get rid of duplicate fields.
        to_pop = ["label", "changePercent", "unadjustedVolume", "adjClose"]
        results: List[FMPIndexHistoricalData] = []

        for d in sorted(data, key=lambda x: x["date"], reverse=False):
            _ = [d.pop(pop) for pop in to_pop if pop in d]
            if d.get("volume") == 0:
                _ = d.pop("volume")
            results.append(FMPIndexHistoricalData.model_validate(d))

        return results

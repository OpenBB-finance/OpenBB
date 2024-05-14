"""Intrinio Index Historical Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_requests, get_querystring
from pydantic import Field


class IntrinioIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """Intrinio Index Historical Query.

    Source:
    https://docs.intrinio.com/documentation/web_api/get_stock_market_index_historical_data_v2
    """

    __alias_dict__ = {"limit": "page_size", "sort": "sort_order"}
    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class IntrinioIndexHistoricalData(IndexHistoricalData):
    """Intrinio Index Historical Data."""

    __alias_dict__ = {"close": "value"}


class IntrinioIndexHistoricalFetcher(
    Fetcher[
        IntrinioIndexHistoricalQueryParams,
        List[IntrinioIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioIndexHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioIndexHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        results = []
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        symbols = query.symbol.replace("$", "").replace("^", "").split(",")
        base_url = "https://api-v2.intrinio.com/indices/stock_market"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])
        urls = [
            f"{base_url}/${symbol}/historical_data/level?{query_str}&api_key={api_key}"
            for symbol in symbols
        ]

        async def callback(response, _) -> List[Dict]:
            """Response callback."""
            _response = await response.json()
            data = _response.get("historical_data")
            symbol = _response["index"].get("symbol").replace("$", "")
            data = [d for d in data if d.get("value") is not None]
            data = [{"symbol": symbol, **d} for d in data] if len(symbols) > 1 else data
            return results.extend(data) if len(data) > 0 else results  # type: ignore

        await amake_requests(urls, callback, **kwargs)

        if len(results) == 0:
            raise EmptyDataError()
        return results

    @staticmethod
    def transform_data(
        query: IntrinioIndexHistoricalQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioIndexHistoricalData]:
        """Return the transformed data."""
        return [IntrinioIndexHistoricalData.model_validate(d) for d in data]

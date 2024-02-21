"""Trading Economics Economic Calendar Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_historical import (
    MarketHistoricalData,
    MarketHistoricalQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_request,
    get_querystring,
)
from pandas import to_datetime
from pydantic import field_validator


class TEMarketHistoricalQueryParams(MarketHistoricalQueryParams):
    """Trading Economics Market Historical Query.

    Source: https://docs.tradingeconomics.com/markets/historical/
    """

    __alias_dict__ = {"start_date": "d1", "end_date": "d2"}
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class TEMarketHistorical(MarketHistoricalData):
    """Trading Economics Market Historical Data."""

    __alias_dict__ = {
        "symbol": "Symbol",
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
    }

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: str) -> datetime:
        """Return formatted datetime."""
        return to_datetime(v, utc=True, dayfirst=True)


class TEMarketHistoricalFetcher(
    Fetcher[
        TEMarketHistoricalQueryParams,
        List[TEMarketHistorical],
    ]
):
    """Transform the query, extract and transform the data from the Trading Economics endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TEMarketHistoricalQueryParams:
        """Transform the query params."""
        return TEMarketHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TEMarketHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Union[dict, List[dict]]:
        """Return the raw data from the TE endpoint."""
        api_key = credentials.get("tradingeconomics_api_key") if credentials else ""

        base_url = "https://api.tradingeconomics.com/markets/historical"
        query_str = get_querystring(query.model_dump(), ["symbol"])
        url = f"{base_url}/{query.symbol}?{query_str}&c={api_key}"

        async def callback(response: ClientResponse, _: Any) -> Union[dict, List[dict]]:
            """Return the response."""
            if response.status != 200:
                raise RuntimeError(f"Error in TE request -> {await response.text()}")
            return await response.json()

        return await amake_request(url, response_callback=callback, **kwargs)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TEMarketHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TEMarketHistorical]:
        """Return the transformed data."""
        return [TEMarketHistorical.model_validate(d) for d in data]

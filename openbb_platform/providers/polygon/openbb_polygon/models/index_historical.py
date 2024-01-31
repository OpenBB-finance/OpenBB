"""Polygon Index Historical Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_polygon.utils.helpers import get_data_many
from pydantic import Field, PositiveInt


class PolygonIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """Polygon Index Historical Query.

    Source: https://polygon.io/docs/indices/getting-started
    """

    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] = (
        Field(default="day", description="Timespan of the data.")
    )
    sort: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order of the data."
    )
    limit: PositiveInt = Field(
        default=49999, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    adjusted: bool = Field(default=True, description="Whether the data is adjusted.")
    multiplier: PositiveInt = Field(
        default=1, description="Multiplier of the timespan."
    )


class PolygonIndexHistoricalData(IndexHistoricalData):
    """Polygon Index Historical Data."""

    __alias_dict__ = {
        "date": "t",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
        "vwap": "vw",
    }

    transactions: Optional[PositiveInt] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
        alias="n",
    )


class PolygonIndexHistoricalFetcher(
    Fetcher[
        PolygonIndexHistoricalQueryParams,
        List[PolygonIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Polygon endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonIndexHistoricalQueryParams:
        """Transform the query params."""
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return PolygonIndexHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: PolygonIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract raw data from the Polygon endpoint."""
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"I:{query.symbol}/range/{query.multiplier}/{query.timespan}/"
            f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
            f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
        )
        data = await get_data_many(request_url, "results", **kwargs)

        for d in data:
            d["t"] = datetime.fromtimestamp(d["t"] / 1000)
            if query.timespan not in ["minute", "hour"]:
                d["t"] = d["t"].date()

        return data

    @staticmethod
    def transform_data(
        query: PolygonIndexHistoricalQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> List[PolygonIndexHistoricalData]:
        """Transform the data."""
        return [PolygonIndexHistoricalData.model_validate(d) for d in data]

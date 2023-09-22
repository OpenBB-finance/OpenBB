"""Polygon major indices end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_polygon.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_historical import (
    MajorIndicesHistoricalData,
    MajorIndicesHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PositiveInt


class PolygonMajorIndicesHistoricalQueryParams(MajorIndicesHistoricalQueryParams):
    """Polygon major indices end of day Query.

    Source: https://polygon.io/docs/indices/getting-started
    """

    timespan: Literal[
        "minute", "hour", "day", "week", "month", "quarter", "year"
    ] = Field(default="day", description="Timespan of the data.")
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


class PolygonMajorIndicesHistoricalData(MajorIndicesHistoricalData):
    """Polygon major indices end of day Data."""

    class Config:
        fields = {
            "date": "t",
            "open": "o",
            "high": "h",
            "low": "l",
            "close": "c",
        }

    transactions: Optional[PositiveInt] = Field(
        description="Number of transactions for the symbol in the time period.",
        alias="n",
    )


class PolygonMajorIndicesHistoricalFetcher(
    Fetcher[
        PolygonMajorIndicesHistoricalQueryParams,
        List[PolygonMajorIndicesHistoricalData],
    ]
):
    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> PolygonMajorIndicesHistoricalQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return PolygonMajorIndicesHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: PolygonMajorIndicesHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"I:{query.symbol}/range/{query.multiplier}/{query.timespan}/"
            f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
            f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
        )
        data = get_data_many(request_url, "results", **kwargs)

        for d in data:
            d["t"] = datetime.fromtimestamp(d["t"] / 1000)
            if query.timespan not in ["minute", "hour"]:
                d["t"] = d["t"].date()

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonMajorIndicesHistoricalData]:
        return [PolygonMajorIndicesHistoricalData.parse_obj(d) for d in data]

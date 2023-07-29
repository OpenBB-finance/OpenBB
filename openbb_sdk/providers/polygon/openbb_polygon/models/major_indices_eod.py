"""Polygon major indices end of day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.metadata import QUERY_DESCRIPTIONS
from openbb_provider.models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from pydantic import Field, PositiveFloat, PositiveInt, validator

from openbb_polygon.utils.helpers import get_data


class PolygonMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """Polygon major indices end of day Query.

    Source: https://polygon.io/docs/indices/getting-started
    """

    timespan: Literal[
        "minute", "hour", "day", "week", "month", "quarter", "year"
    ] = Field(default="day", description="The timespan of the data.")
    sort: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order of the data."
    )
    limit: PositiveInt = Field(
        default=49999, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    adjusted: bool = Field(default=True, description="Whether the data is adjusted.")
    multiplier: PositiveInt = Field(
        default=1, description="The multiplier of the timespan."
    )


class PolygonMajorIndicesEODData(MajorIndicesEODData):
    """Polygon major indices end of day Data."""

    class Config:
        fields = {
            "open": "o",
            "high": "h",
            "low": "l",
            "close": "c",
            "volume": "v",
        }

    t: datetime = Field(description="The timestamp of the data.")
    n: PositiveInt = Field(
        description="The number of transactions for the symbol in the time period."
    )
    vw: PositiveFloat = Field(
        description="The volume weighted average price of the symbol."
    )

    @validator("t", pre=True, check_fields=False)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v / 1000)


class PolygonMajorIndicesEODFetcher(
    Fetcher[
        MajorIndicesEODQueryParams,
        MajorIndicesEODData,
        PolygonMajorIndicesEODQueryParams,
        PolygonMajorIndicesEODData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonMajorIndicesEODQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=7)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return PolygonMajorIndicesEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: PolygonMajorIndicesEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[PolygonMajorIndicesEODData]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"I:{query.symbol}/range/1/{query.timespan}/"
            f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
            f"&sort={query.sort}&limit={query.limit}&multiplier={query.multiplier}"
            f"&apiKey={api_key}"
        )

        data = get_data(request_url)
        if isinstance(data, list):
            raise ValueError("Expected a dict, got a list")

        if "results" not in data.keys() or len(data["results"]) == 0:
            raise RuntimeError("No results found. Please change your query parameters.")

        data = data["results"]
        return [PolygonMajorIndicesEODData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[PolygonMajorIndicesEODData],
    ) -> List[PolygonMajorIndicesEODData]:
        return data

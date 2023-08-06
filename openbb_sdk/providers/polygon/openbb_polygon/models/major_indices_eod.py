"""Polygon major indices end of day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PositiveInt, validator

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
            "date": "t",
            "open": "o",
            "high": "h",
            "low": "l",
            "close": "c",
            "volume": "v",
            "vwap": "vw",
        }

    n: PositiveInt = Field(
        description="The number of transactions for the symbol in the time period."
    )

    @validator("t", pre=True, check_fields=False)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v / 1000)


class PolygonMajorIndicesEODFetcher(
    Fetcher[
        MajorIndicesEODQueryParams,
        List[MajorIndicesEODData],
        PolygonMajorIndicesEODQueryParams,
        List[PolygonMajorIndicesEODData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonMajorIndicesEODQueryParams:
        now = datetime.now().date()
        start_date = params.pop("start_date", now - timedelta(days=7))
        end_date = params.pop("end_date", now)
        return PolygonMajorIndicesEODQueryParams(
            **params, start_date=start_date, end_date=end_date
        )

    @staticmethod
    def extract_data(
        query: PolygonMajorIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[PolygonMajorIndicesEODData]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"I:{query.symbol}/range/{query.multiplier}/{query.timespan}/"
            f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
            f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
        )

        data = get_data(request_url, **kwargs)
        if isinstance(data, list):
            raise ValueError("Expected a dict, got a list")

        if "results" not in data or len(data["results"]) == 0:
            raise RuntimeError("No results found. Please change your query parameters.")

        return [
            PolygonMajorIndicesEODData.parse_obj(d) for d in data.get("results", [])
        ]

    @staticmethod
    def transform_data(
        data: List[PolygonMajorIndicesEODData],
    ) -> List[MajorIndicesEODData]:
        return [MajorIndicesEODData.parse_obj(d.dict()) for d in data]

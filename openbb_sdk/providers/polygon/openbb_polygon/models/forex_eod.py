"""Polygon forex end of day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_eod import ForexEODData, ForexEODQueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PositiveInt, validator

from openbb_polygon.utils.helpers import get_data


class PolygonForexEODQueryParams(ForexEODQueryParams):
    """Polygon forex end of day Query.

    Source: https://polygon.io/docs/forex/get_v2_aggs_ticker__forexticker__range__multiplier___timespan___from___to
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


class PolygonForexEODData(ForexEODData):
    """Polygon forex end of day Data."""

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


class PolygonForexEODFetcher(
    Fetcher[
        PolygonForexEODQueryParams,
        PolygonForexEODData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonForexEODQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=7)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return PolygonForexEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: PolygonForexEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[PolygonForexEODData]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"C:{query.symbol}/range/1/{query.timespan}/"
            f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
            f"&sort={query.sort}&limit={query.limit}&multiplier={query.multiplier}"
            f"&apiKey={api_key}"
        )

        data = get_data(request_url, **kwargs)
        if isinstance(data, list):
            raise ValueError("Expected a dict, got a list")

        if "results" not in data or len(data["results"]) == 0:
            raise RuntimeError("No results found. Please change your query parameters.")

        data = data["results"]
        return [PolygonForexEODData(**d) for d in data]

    @staticmethod
    def transform_data(data: List[PolygonForexEODData]) -> List[PolygonForexEODData]:
        return data

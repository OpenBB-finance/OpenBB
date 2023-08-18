"""Polygon stocks end of day fetcher."""


from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import repeat
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_eod import StockEODData, StockEODQueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PositiveInt, validator

from openbb_polygon.utils.helpers import get_data


class PolygonStockEODQueryParams(StockEODQueryParams):
    """Polygon stocks end of day Query.

    Source: https://polygon.io/docs/stocks/getting-started
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


class PolygonStockEODData(StockEODData):
    """Polygon stocks end of day Data."""

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

    n: Optional[PositiveInt] = Field(
        description="Number of transactions for the symbol in the time period."
    )

    @validator("t", pre=True, check_fields=False)
    def t_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v / 1000)


class PolygonStockEODFetcher(
    Fetcher[
        PolygonStockEODQueryParams,
        List[PolygonStockEODData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonStockEODQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return PolygonStockEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: PolygonStockEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        data: list = []

        def multiple_symbols(symbol: str, data: List[PolygonStockEODData]) -> None:
            request_url = (
                f"https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{query.multiplier}/{query.timespan}/"
                f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
                f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
            )
            results = get_data(request_url, **kwargs).get("results", [])

            if "," in query.symbol:
                results = [dict(symbol=symbol, **d) for d in results]

            return data.extend([PolygonStockEODData.parse_obj(d) for d in results])

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        data.sort(key=lambda x: x.date)
        if query.timespan == "day":
            for d in data:
                d.date = datetime.replace(d.date, hour=0, minute=0)

        return data

    @staticmethod
    def transform_data(data: List[dict]) -> List[PolygonStockEODData]:
        return [PolygonStockEODData.parse_obj(d) for d in data]

"""Polygon stocks end of day fetcher."""


from datetime import datetime, timedelta
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.stock_eod import StockEODData, StockEODQueryParams
from pydantic import Field, NonNegativeFloat, PositiveFloat, PositiveInt

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import BaseStockData, BaseStockQueryParams


class PolygonStockEODQueryParams(BaseStockQueryParams):
    """Polygon stocks end of day query.

    Source: https://polygon.io/docs/stocks/getting-started

    Parameters
    ----------
    symbol : str
        The symbol of the stocks to fetch.
    start_date : Union[date, datetime]
        The start date of the query.
    end_date : Union[date, datetime]
        The end date of the query.
    timespan : Timespan, optional
        The timespan of the query, by default Timespan.day
    sort : Literal["asc", "desc"], optional
        The sort order of the query, by default "desc"
    limit : PositiveInt, optional
        The limit of the query, by default 49999
    adjusted : bool, optional
        Whether the query is adjusted, by default True
    multiplier : PositiveInt, optional
        The multiplier of the query, by default 1
    """


class PolygonStockEODData(BaseStockData):
    v: NonNegativeFloat = Field(alias="volume")
    n: PositiveInt
    vw: Optional[PositiveFloat]


class PolygonStockEODFetcher(
    Fetcher[
        StockEODQueryParams,
        StockEODData,
        PolygonStockEODQueryParams,
        PolygonStockEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockEODQueryParams, extra_params: Optional[Dict] = None
    ) -> PolygonStockEODQueryParams:
        now = datetime.now()
        start_date = query.start_date or (now - timedelta(days=5)).date()
        end_date = query.end_date or now.date()
        return PolygonStockEODQueryParams(
            symbol=query.symbol,
            start_date=start_date,
            end_date=end_date,
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: PolygonStockEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[PolygonStockEODData]:
        if credentials:
            api_key = credentials.get("polygon_api_key")

        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"{query.stocksTicker.upper()}/range/1/{str(query.timespan.value)}/"
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
        return [PolygonStockEODData(**d) for d in data]

    @staticmethod
    def transform_data(data: List[PolygonStockEODData]) -> List[StockEODData]:
        return data_transformer(data, StockEODData)

"""Polygon Forex Price fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeFloat, PositiveFloat, PositiveInt

from builtin_providers.polygon.helpers import get_data
from builtin_providers.polygon.types import BaseStockData, BaseStockQueryParams

# IMPORT INTERNAL
from openbb_provider.model.data.forex_price import ForexPriceData, ForexPriceQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class PolygonForexPriceQueryParams(BaseStockQueryParams):
    """Polygon forex price query.

    Source: https://polygon.io/docs/forex/get_v2_aggs_ticker__forexticker__range__multiplier___timespan___from___to

    Parameters
    ----------
    stocksTicker : str
        The ticker symbol of the stocks to fetch.
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

    __name__ = "PolygonForexPriceQueryParams"


class PolygonForexPriceData(BaseStockData):
    __name__ = "PolygonPriceForexData"
    v: NonNegativeFloat = Field(alias="volume")
    n: PositiveInt
    vw: Optional[PositiveFloat]


class PolygonForexPriceFetcher(
    Fetcher[
        ForexPriceQueryParams,
        ForexPriceData,
        PolygonForexPriceQueryParams,
        PolygonForexPriceData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexPriceQueryParams, extra_params: Optional[Dict] = None
    ) -> PolygonForexPriceQueryParams:
        return PolygonForexPriceQueryParams(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date if query.end_date else datetime.now(),
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: PolygonForexPriceQueryParams, api_key: str
    ) -> List[PolygonForexPriceData]:
        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"C:{query.stocksTicker.upper()}/range/1/{query.timespan}/"
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
        return [PolygonForexPriceData(**d) for d in data]

    @staticmethod
    def transform_data(data: List[PolygonForexPriceData]) -> List[ForexPriceData]:
        return data_transformer(data, ForexPriceData)

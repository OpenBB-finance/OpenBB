"""Polygon crypto end of day fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

from builtin_providers.polygon.helpers import get_data
from builtin_providers.polygon.types import BaseStockData, BaseStockQueryParams

# IMPORT INTERNAL
from openbb_provider.model.data.crypto_eod import CryptoEODData, CryptoEODQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeFloat, PositiveFloat, PositiveInt


class PolygonCryptoEODQueryParams(BaseStockQueryParams):
    """Polygon crypto end of day query.

    Source: https://polygon.io/docs/crypto/get_v2_aggs_ticker__cryptoticker__range__multiplier___timespan___from___to

    Parameters
    ----------
    symbol : str
        The symbol symbol of the stocks to fetch.
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


class PolygonCryptoEODData(BaseStockData):
    v: NonNegativeFloat = Field(alias="volume")
    n: PositiveInt
    vw: PositiveFloat


class PolygonCryptoEODFetcher(
    Fetcher[
        CryptoEODQueryParams,
        CryptoEODData,
        PolygonCryptoEODQueryParams,
        PolygonCryptoEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: CryptoEODQueryParams, extra_params: Optional[Dict] = None
    ) -> PolygonCryptoEODQueryParams:
        return PolygonCryptoEODQueryParams(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date if query.end_date else datetime.now(),
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: PolygonCryptoEODQueryParams, api_key: str
    ) -> List[PolygonCryptoEODData]:
        request_url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"X:{query.stocksTicker.upper()}/range/1/{query.timespan}/"
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
        return [PolygonCryptoEODData(**d) for d in data]

    @staticmethod
    def transform_data(data: List[PolygonCryptoEODData]) -> List[CryptoEODData]:
        return data_transformer(data, CryptoEODData)

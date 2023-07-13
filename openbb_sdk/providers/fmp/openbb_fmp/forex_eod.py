"""FMP Forex end of day fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol
from openbb_provider.model.data.forex_eod import ForexEODData, ForexEODQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field, validator

from .helpers import get_data_many


class FMPForexEODQueryParams(QueryParams):
    """FMP Forex end of day query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    symbol: str = Field(min_length=1)


class FMPForexEODData(Data):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adjClose: float = Field(alias="adj_close")
    volume: float
    unadjustedVolume: float
    change: float
    changePercent: float
    vwap: Optional[float]
    label: str
    changeOverTime: float

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPForexEODFetcher(
    Fetcher[
        ForexEODQueryParams,
        ForexEODData,
        FMPForexEODQueryParams,
        FMPForexEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPForexEODQueryParams:
        return FMPForexEODQueryParams(
            symbol=query.symbol,
            **extra_params or {},
        )

    @staticmethod
    def extract_data(
        query: FMPForexEODQueryParams, api_key: str
    ) -> List[FMPForexEODData]:
        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/historical-price-full/forex/{query.symbol}?&apikey={api_key}"
        return get_data_many(url, FMPForexEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPForexEODData]) -> List[ForexEODData]:
        return data_transformer(data, ForexEODData)

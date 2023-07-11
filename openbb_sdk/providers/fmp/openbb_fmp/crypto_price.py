"""FMP Crypto Price fetcher."""

# IMPORT STANDARD
from enum import Enum
from typing import Dict, List, Optional

from builtin_providers.fmp.helpers import BaseStockPriceData, create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import QueryParams
from openbb_provider.model.data.crypto_price import (
    CryptoPriceData,
    CryptoPriceQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field


class Interval(str, Enum):
    oneminute = "1min"
    fiveminute = "5min"
    fifteenminute = "15min"
    thirtyminute = "30min"
    onehour = "1hour"
    fourhour = "4hour"


class FMPCryptoPriceQueryParams(QueryParams):
    """FMP Crypto Price query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Cryptocurrencies

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    interval : Enum of ["1min", "5min", "15min", "30min", "1hour", "4hour"] (default: "1hour")
        The interval of the data.
    """

    symbol: str = Field(min_length=1)
    interval: Interval = Field(default=Interval.onehour)


class FMPCryptoPriceData(BaseStockPriceData):
    """FMP Crypto Price data."""


class FMPCryptoPriceFetcher(
    Fetcher[
        CryptoPriceQueryParams,
        CryptoPriceData,
        FMPCryptoPriceQueryParams,
        FMPCryptoPriceData,
    ]
):
    @staticmethod
    def transform_query(
        query: CryptoPriceQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPCryptoPriceQueryParams:
        return FMPCryptoPriceQueryParams(
            symbol=query.symbol, **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPCryptoPriceQueryParams, api_key: str
    ) -> List[FMPCryptoPriceData]:
        url = create_url(
            3, f"historical-chart/{query.interval}/{query.symbol}", api_key
        )
        return get_data_many(url, FMPCryptoPriceData)

    @staticmethod
    def transform_data(data: List[FMPCryptoPriceData]) -> List[CryptoPriceData]:
        return data_transformer(data, CryptoPriceData)

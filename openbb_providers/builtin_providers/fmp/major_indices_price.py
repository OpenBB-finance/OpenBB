"""FMP Major Indices Price fetcher."""

# IMPORT STANDARD
from enum import Enum
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import QueryParams
from openbb_provider.model.data.major_indices_price import (
    MajorIndicesPriceData,
    MajorIndicesPriceQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field

from builtin_providers.fmp.helpers import BaseStockPriceData, create_url, get_data_many


class Interval(str, Enum):
    oneminute = "1min"
    fiveminute = "5min"
    fifteenminute = "15min"
    thirtyminute = "30min"
    onehour = "1hour"
    fourhour = "4hour"


class FMPMajorIndicesPriceQueryParams(QueryParams):
    """FMP MajorIndices Price query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    interval : Enum of ["1min", "5min", "15min", "30min", "1hour", "4hour"] (default: "1hour")
        The interval of the data.
    """

    symbol: str = Field(min_length=1)
    interval: Interval = Field(default=Interval.onehour)


class FMPMajorIndicesPriceData(BaseStockPriceData):
    """FMP MajorIndices Price data."""


class FMPMajorIndicesPriceFetcher(
    Fetcher[
        MajorIndicesPriceQueryParams,
        MajorIndicesPriceData,
        FMPMajorIndicesPriceQueryParams,
        FMPMajorIndicesPriceData,
    ]
):
    @staticmethod
    def transform_query(
        query: MajorIndicesPriceQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPMajorIndicesPriceQueryParams:
        return FMPMajorIndicesPriceQueryParams(
            symbol=query.symbol, **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesPriceQueryParams, api_key: str
    ) -> List[FMPMajorIndicesPriceData]:
        url = create_url(
            3, f"historical-chart/{query.interval}/{query.symbol}", api_key
        )
        return get_data_many(url, FMPMajorIndicesPriceData)

    @staticmethod
    def transform_data(
        data: List[FMPMajorIndicesPriceData],
    ) -> List[MajorIndicesPriceData]:
        return data_transformer(data, MajorIndicesPriceData)

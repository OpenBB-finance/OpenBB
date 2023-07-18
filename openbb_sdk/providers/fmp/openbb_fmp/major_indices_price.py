"""FMP Major Indices Price fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import QueryParams
from openbb_provider.models.base import BaseSymbol
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.major_indices_price import (
    MajorIndicesPriceData,
    MajorIndicesPriceQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field

from .helpers import BaseStockPriceData, create_url, get_data_many


class FMPMajorIndicesPriceQueryParams(QueryParams, BaseSymbol):
    """FMP MajorIndices Price query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices

    Parameter
    ---------
    symbol : str
        The symbol of the index.
    interval : str (default = "1hour")
        The interval of the index data to fetch. Possible values include "1min", "5min",
        "15min", "30min", "1hour", "4hour".
    """

    interval: str = Field(default="1hour")


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
            symbol=query.symbol,
            **extra_params or {},
        )

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesPriceQueryParams, api_key: str
    ) -> List[FMPMajorIndicesPriceData]:
        url = create_url(
            3, f"historical-chart/{query.interval}/%5E{query.symbol}", api_key
        )
        return get_data_many(url, FMPMajorIndicesPriceData)

    @staticmethod
    def transform_data(
        data: List[FMPMajorIndicesPriceData],
    ) -> List[MajorIndicesPriceData]:
        return data_transformer(data, MajorIndicesPriceData)

"""FMP Stock Price fetcher."""

# IMPORT STANDARD
from enum import Enum
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import QueryParams
from openbb_provider.model.data.stock_price import StockPriceData, StockPriceQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field

from openbb_fmp.helpers import BaseStockPriceData, create_url, get_data_many


class Interval(str, Enum):
    oneminute = "1min"
    fiveminute = "5min"
    fifteenminute = "15min"
    thirtyminute = "30min"
    onehour = "1hour"
    fourhour = "4hour"


class FMPStockPriceQueryParams(QueryParams):
    """FMP Stock Price query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Historical-Price

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    interval : Enum of ["1min", "5min", "15min", "30min", "1hour", "4hour"] (default: "1hour")
        The interval of the data.
    """

    symbol: str = Field(min_length=1)
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = "1hour"


class FMPStockPriceData(BaseStockPriceData):
    """FMP Stock Price data."""


class FMPStockPriceFetcher(
    Fetcher[
        StockPriceQueryParams,
        StockPriceData,
        FMPStockPriceQueryParams,
        FMPStockPriceData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockPriceQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockPriceQueryParams:
        return FMPStockPriceQueryParams(
            symbol=query.symbol, **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPStockPriceQueryParams, api_key: str
    ) -> List[FMPStockPriceData]:
        url = create_url(
            3, f"historical-chart/{query.interval}/{query.symbol}", api_key
        )
        return get_data_many(url, FMPStockPriceData)

    @staticmethod
    def transform_data(data: List[FMPStockPriceData]) -> List[StockPriceData]:
        return data_transformer(data, StockPriceData)

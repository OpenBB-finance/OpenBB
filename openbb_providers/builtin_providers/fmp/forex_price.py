"""FMP Forex Price fetcher."""

# IMPORT STANDARD
from enum import Enum
from typing import Dict, List, Literal, Optional

# IMPORT THIRD-PARTY
from pydantic import Field

from builtin_providers.fmp.helpers import BaseStockPriceData, create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import QueryParams
from openbb_provider.model.data.forex_price import ForexPriceData, ForexPriceQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class Interval(str, Enum):
    oneminute = "1min"
    fiveminute = "5min"
    fifteenminute = "15min"
    thirtyminute = "30min"
    onehour = "1hour"
    fourhour = "4hour"


class FMPForexPriceQueryParams(QueryParams):
    """FMP Forex Price query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Forex-Historical-Price

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    interval : Enum of ["1min", "5min", "15min", "30min", "1hour", "4hour"] (default: "1hour")
        The interval of the data.
    """

    __name__ = "FMPForexPriceQueryParams"
    symbol: str = Field(min_length=1)
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = "1hour"


class FMPForexPriceData(BaseStockPriceData):
    __name__ = "FMPForexPriceData"


class FMPForexPriceFetcher(
    Fetcher[
        ForexPriceQueryParams,
        ForexPriceData,
        FMPForexPriceQueryParams,
        FMPForexPriceData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexPriceQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPForexPriceQueryParams:
        return FMPForexPriceQueryParams(
            symbol=query.symbol, **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPForexPriceQueryParams, api_key: str
    ) -> List[FMPForexPriceData]:
        url = create_url(
            3, f"historical-chart/{query.interval}/{query.symbol}", api_key
        )
        return get_data_many(url, FMPForexPriceData)

    @staticmethod
    def transform_data(data: List[FMPForexPriceData]) -> List[ForexPriceData]:
        return data_transformer(data, ForexPriceData)

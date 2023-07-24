"""FMP Forex Price fetcher."""


from enum import Enum
from typing import Dict, List, Literal, Optional

from openbb_provider.abstract.data import QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.forex_price import ForexPriceData, ForexPriceQueryParams

# IMPORT THIRD-PARTY
from pydantic import Field

from openbb_fmp.utils.helpers import BaseStockPriceData, create_url, get_data_many


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

    symbol: str = Field(min_length=1)
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = "1hour"


class FMPForexPriceData(BaseStockPriceData):
    """FMP Forex Price data."""


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
        query: FMPForexPriceQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPForexPriceData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            3, f"historical-chart/{query.interval}/{query.symbol}", api_key
        )
        return get_data_many(url, FMPForexPriceData)

    @staticmethod
    def transform_data(data: List[FMPForexPriceData]) -> List[ForexPriceData]:
        return data_transformer(data, ForexPriceData)

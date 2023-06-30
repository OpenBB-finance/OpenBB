"""FMP Stocks end of day fetcher."""

# IMPORT STANDARD
from datetime import date, datetime
from typing import Dict, List, Literal, Optional

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, validator

from builtin_providers.fmp.helpers import get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.stock_eod import StockEODData, StockEODQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer, get_querystring


class FMPStockEODQueryParams(QueryParams):
    """FMP Stock end of day query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    start_date : date
        The start date of the stock data from which to retrieve the data.
    end_date : date
        The end date of the stock data up to which to retrieve the data.
    timeseries : Optional[int]
        The number of days to look back.
    serietype : Optional[Literal["line"]]
        The type of the series. Only "line" is supported.
    """

    __name__ = "FMPStockEODQueryParams"
    symbol: str = Field(min_length=1)
    serietype: Optional[Literal["line"]]
    start_date: date
    end_date: date
    timeseries: Optional[NonNegativeInt]  # Number of days to looks back


class FMPStockEODData(Data):
    __name__ = "FMPStockEODData"
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
    vwap: float
    label: str
    changeOverTime: float

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPStockEODFetcher(
    Fetcher[
        StockEODQueryParams,
        StockEODData,
        FMPStockEODQueryParams,
        FMPStockEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockEODQueryParams:
        raw_end = query.end_date if query.end_date else datetime.now()
        return FMPStockEODQueryParams(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=raw_end,
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: FMPStockEODQueryParams, api_key: str
    ) -> List[FMPStockEODData]:
        base_url = "https://financialmodelingprep.com/api/v3/"
        query_str = get_querystring(query.dict(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}historical-price-full/{query.symbol}?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPStockEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPStockEODData]) -> List[StockEODData]:
        return data_transformer(data, StockEODData)

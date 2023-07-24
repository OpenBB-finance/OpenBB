"""FMP Stock News fetcher."""


from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.stock_news import StockNewsData, StockNewsQueryParams

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockNewsQueryParams(QueryParams):
    """FMP Stock News query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-news-api/

    Parameter
    ---------
    symbols : str
        The symbols of the companies.
    page : int (default: 0)
        The page of the data to retrieve.
    limit : Optional[int]
        The limit of the data to retrieve.
    """

    tickers: str = Field(min_length=1, alias="symbols")
    page: int = Field(default=0)
    limit: Optional[NonNegativeInt]


class FMPStockNewsData(Data):
    symbol: str
    publishedDate: datetime = Field(alias="date")
    title: str
    image: Optional[str]
    text: str
    url: str
    site: str


class FMPStockNewsFetcher(
    Fetcher[
        StockNewsQueryParams,
        StockNewsData,
        FMPStockNewsQueryParams,
        FMPStockNewsData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockNewsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockNewsQueryParams:
        return FMPStockNewsQueryParams(
            symbols=query.symbols,
            page=query.page,
            **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPStockNewsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockNewsData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(3, "stock_news", api_key, query)
        return get_data_many(url, FMPStockNewsData)

    @staticmethod
    def transform_data(data: List[FMPStockNewsData]) -> List[StockNewsData]:
        return data_transformer(data, StockNewsData)

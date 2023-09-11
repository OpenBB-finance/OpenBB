"""yfinance Stock News fetcher."""


import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from pydantic import Field, validator
from yfinance import Ticker


class YFinanceStockNewsQueryParams(StockNewsQueryParams):
    """YFinance Stock News Query.

    Source: https://finance.yahoo.com/news/
    """


class YFinanceStockNewsData(StockNewsData):
    """YFinance Stock News Data."""

    class Config:
        fields = {
            "date": "providerPublishTime",
            "url": "link",
        }

    uuid: str = Field(description="Unique identifier for the news article")
    publisher: str = Field(description="Publisher of the news article")
    type: str = Field(description="Type of the news article")
    thumbnail: Optional[List] = Field(
        description="Thumbnail related data to the ticker news article."
    )
    relatedTickers: str = Field(description="Tickers related to the news article.")

    @validator("providerPublishTime", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v)

    @validator("relatedTickers", pre=True, check_fields=False)
    def related_tickers_string(cls, v):  # pylint: disable=E0213
        return ", ".join(v)

    @validator("thumbnail", pre=True, check_fields=False)
    def thumbnail_list(cls, v):  # pylint: disable=E0213
        return v["resolutions"]


class YFinanceStockNewsFetcher(
    Fetcher[
        YFinanceStockNewsQueryParams,
        List[YFinanceStockNewsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceStockNewsQueryParams:
        return YFinanceStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        data = Ticker(query.symbols).get_news()
        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[YFinanceStockNewsData]:
        return [YFinanceStockNewsData.parse_obj(d) for d in data]

"""Polygon Stock News Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.stock_news import StockNewsData, StockNewsQueryParams
from pydantic import BaseModel, Field

from openbb_polygon.utils.helpers import get_data


class PolygonStockNewsQueryParams(StockNewsQueryParams):
    """Polygon stock news query.

    Source: https://polygon.io/docs/stocks/get_v2_reference_news

    ticker_lt : str, optional
        Less than, by default None
    ticker_lte : str, optional
        Less than or equal, by default None
    ticker_gt : str, optional
        Greater than, by default None
    ticker_gte : str, optional
        Greater than or equal, by default None
    published_utc : str, optional
        The published date of the query, by default None
    published_utc_lt : str, optional
        Less than, by default None
    published_utc_lte : str, optional
        Less than or equal, by default None
    published_utc_gt : str, optional
        Greater than, by default None
    published_utc_gte : str, optional
        Greater than or equal, by default None
    order : Literal["asc", "desc"], optional
        The sort order of the query, by default None
    sort : str, optional
        The sort of the query, by default None
    """

    class Config:
        fields = {"symbols": "ticker"}

    ticker_lt: Optional[str] = Field(alias="ticker.lt", default=None)
    ticker_lte: Optional[str] = Field(alias="ticker.lte", default=None)
    ticker_gt: Optional[str] = Field(alias="ticker.gt", default=None)
    ticker_gte: Optional[str] = Field(alias="ticker.gte", default=None)
    published_utc: Optional[str] = None
    published_utc_lt: Optional[str] = Field(alias="published_utc.lt", default=None)
    published_utc_lte: Optional[str] = Field(alias="published_utc.lte", default=None)
    published_utc_gt: Optional[str] = Field(alias="published_utc.gt", default=None)
    published_utc_gte: Optional[str] = Field(alias="published_utc.gte", default=None)
    order: Optional[Literal["asc", "desc"]] = None
    sort: Optional[str] = None


class PolygonPublisher(BaseModel):
    favicon_url: str
    homepage_url: str
    logo_url: str
    name: str


class PolygonStockNewsData(Data):
    """Source: https://polygon.io/docs/stocks/get_v2_reference_news"""

    amp_url: Optional[str]
    article_url: str = Field(alias="url")
    author: Optional[str]
    description: Optional[str] = Field(alias="text")
    id: str
    image_url: Optional[str]
    keywords: Optional[List[str]]
    published_utc: datetime = Field(alias="date")
    publisher: PolygonPublisher = Field(alias="image")
    tickers: List[str]
    title: str


class PolygonStockNewsFetcher(
    Fetcher[
        StockNewsQueryParams,
        StockNewsData,
        PolygonStockNewsQueryParams,
        PolygonStockNewsData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonStockNewsQueryParams:
        return PolygonStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[PolygonStockNewsData]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/v2/reference/news"
        querystring = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{querystring}&apiKey={api_key}"
        data = get_data(request_url, **kwargs)["results"]

        if len(data) == 0:
            raise RuntimeError("No news found")

        return [PolygonStockNewsData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[PolygonStockNewsData],
    ) -> List[StockNewsData]:
        processors = {"publisher": lambda x: x.favicon_url}
        return data_transformer(data, StockNewsData, processors)

"""Polygon Stock News Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import BaseModel, Field

from openbb_polygon.utils.helpers import get_data


class PolygonStockNewsQueryParams(StockNewsQueryParams):
    """Polygon stock news query.

    Source: https://polygon.io/docs/stocks/get_v2_reference_news
    """

    class Config:
        fields = {"symbols": "ticker"}

    ticker_lt: Optional[str] = Field(
        default=None, description="Less than, by default None"
    )
    ticker_lte: Optional[str] = Field(
        default=None, description="Less than or equal, by default None"
    )
    ticker_gt: Optional[str] = Field(
        default=None, description="Greater than, by default None"
    )
    ticker_gte: Optional[str] = Field(
        default=None, description="Greater than or equal, by default None"
    )
    published_utc: Optional[str] = Field(
        default=None, description="Published date of the query, by default None"
    )
    published_utc_lt: Optional[str] = Field(
        default=None, description="Less than, by default None"
    )
    published_utc_lte: Optional[str] = Field(
        default=None, description="Less than or equal, by default None"
    )
    published_utc_gt: Optional[str] = Field(
        default=None, description="Greater than, by default None"
    )
    published_utc_gte: Optional[str] = Field(
        default=None, description="Greater than or equal, by default None"
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        default=None, description="Sort order of the query, by default None"
    )
    sort: Optional[str] = Field(
        default=None, description="Sort of the query, by default None"
    )


class PolygonPublisher(BaseModel):
    favicon_url: str = Field(description="Favicon URL.")
    homepage_url: str = Field(description="Homepage URL.")
    logo_url: str = Field(description="Logo URL.")
    name: str = Field(description="Publisher Name.")


class PolygonStockNewsData(StockNewsData):
    """Source: https://polygon.io/docs/stocks/get_v2_reference_news"""

    class Config:
        fields = {
            "url": "article_url",
            "text": "description",
            "date": "published_utc",
        }

    amp_url: Optional[str] = Field(description="AMP URL.")
    author: Optional[str] = Field(description="Author of the article.")
    id: str = Field(description="Article ID.")
    image_url: Optional[str] = Field(description="Image URL.")
    keywords: Optional[List[str]] = Field(description="Keywords in the article")
    publisher: PolygonPublisher = Field(description="Publisher of the article.")
    tickers: List[str] = Field(description="Tickers covered in the article.")


class PolygonStockNewsFetcher(
    Fetcher[
        PolygonStockNewsQueryParams,
        List[PolygonStockNewsData],
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
    ) -> dict:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/v2/reference/news"
        querystring = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{querystring}&apiKey={api_key}"
        data = get_data(request_url, **kwargs)["results"]

        if len(data) == 0:
            raise RuntimeError("No news found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonStockNewsData]:
        return [PolygonStockNewsData(**d) for d in data]

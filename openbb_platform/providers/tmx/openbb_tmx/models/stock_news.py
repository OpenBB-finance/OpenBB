"""TMX Stock News model."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from openbb_tmx.utils.helpers import get_news_and_events
from pydantic import Field


class TmxStockNewsQueryParams(StockNewsQueryParams):
    """TMX Stock News query."""

    __alias_dict__ = {"symbols": "symbol"}

    page: Optional[int] = Field(
        default=1, description="The page number to start from. Use with limit."
    )


class TmxStockNewsData(StockNewsData):
    """TMX Stock News Data"""

    __alias_dict__ = {
        "date": "datetime",
        "title": "headline",
        "text": "summary",
    }

    source: Optional[str] = Field(description="Source of the news.", default=None)
    newsid: Optional[int] = Field(
        description="Unique ID number of the article", default=None
    )


class TmxStockNewsFetcher(
    Fetcher[TmxStockNewsQueryParams, List[TmxStockNewsData]],
):
    """TMX Stock News Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxStockNewsQueryParams:
        """Transform the query."""
        params["symbols"] = (
            params["symbols"]
            .upper()
            .replace(".TO", "")
            .replace(".TSX", "")
            .replace("-", ".")
        )
        return TmxStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = get_news_and_events(
            symbol=query.symbols,
            page=query.page,
            limit=query.limit,
        )

        return sorted(results, key=lambda d: d["datetime"], reverse=True)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxStockNewsData]:
        """Return the transformed data."""
        return [TmxStockNewsData(**d) for d in data]

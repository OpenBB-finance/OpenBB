"""Yahoo Finance Company News Model."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field, field_validator
from yfinance import Ticker  # type: ignore


class YFinanceCompanyNewsQueryParams(CompanyNewsQueryParams):
    """YFinance Company News Query.

    Source: https://finance.yahoo.com/news/
    """


class YFinanceCompanyNewsData(CompanyNewsData):
    """YFinance Company News Data."""

    __alias_dict__ = {
        "symbols": "relatedTickers",
        "date": "providerPublishTime",
        "url": "link",
    }

    uuid: str = Field(description="Unique identifier for the news article")
    publisher: str = Field(description="Publisher of the news article")
    type: str = Field(description="Type of the news article")
    thumbnail: Optional[List] = Field(
        default=None, description="Thumbnail related data to the ticker news article."
    )

    @field_validator("symbols", mode="before", check_fields=False)
    @classmethod
    def symbols_string(cls, v):
        """Symbols string validator."""
        return ",".join(v)

    @field_validator("providerPublishTime", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Date validator."""
        return datetime.fromtimestamp(v)

    @field_validator("relatedTickers", mode="before", check_fields=False)
    @classmethod
    def related_tickers_string(cls, v):
        """Related tickers string validator."""
        return ", ".join(v)

    @field_validator("thumbnail", mode="before", check_fields=False)
    @classmethod
    def thumbnail_list(cls, v):
        """Thumbnail list validator."""
        return v["resolutions"]


class YFinanceCompanyNewsFetcher(
    Fetcher[
        YFinanceCompanyNewsQueryParams,
        List[YFinanceCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceCompanyNewsQueryParams:
        """Transform query params."""
        return YFinanceCompanyNewsQueryParams(**params)

    @staticmethod
    def extract_data(  # pylint: disable=unused-argument
        query: YFinanceCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        data = Ticker(query.symbols).get_news()
        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        query: YFinanceCompanyNewsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCompanyNewsData]:
        """Transform data."""
        return [YFinanceCompanyNewsData.model_validate(d) for d in data]

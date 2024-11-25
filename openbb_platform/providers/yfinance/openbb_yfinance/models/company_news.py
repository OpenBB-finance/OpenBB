"""Yahoo Finance Company News Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field, field_validator


class YFinanceCompanyNewsQueryParams(CompanyNewsQueryParams):
    """YFinance Company News Query.

    Source: https://finance.yahoo.com/news/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise ValueError("Required field missing -> symbol")
        return v


class YFinanceCompanyNewsData(CompanyNewsData):
    """YFinance Company News Data."""

    __alias_dict__ = {
        "symbols": "relatedTickers",
        "date": "providerPublishTime",
        "url": "link",
        "images": "thumbnail",
        "source": "publisher",
    }

    source: str = Field(description="Source of the news article")

    @field_validator("symbols", mode="before", check_fields=False)
    @classmethod
    def symbols_string(cls, v):
        """Symbols string validator."""
        return ",".join(v)


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
    async def aextract_data(
        query: YFinanceCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        from yfinance import Ticker  # pylint: disable=import-outside-toplevel

        results = []
        symbols = query.symbol.split(",")  # type: ignore

        async def get_one(symbol):
            data = Ticker(symbol).get_news()
            for d in data:
                images = None
                if d.get("thumbnail"):
                    images = d["thumbnail"].get("resolutions")
                _ = d.pop("uuid")
                _ = d.pop("type")
                d["date"] = datetime.utcfromtimestamp(d["providerPublishTime"])
                d["images"] = (
                    [{k: str(v) for k, v in img.items()} for img in images]
                    if images
                    else None
                )
            results.extend(data)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceCompanyNewsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCompanyNewsData]:
        """Transform data."""
        return [YFinanceCompanyNewsData.model_validate(d) for d in data]

"""Yahoo Finance Company News Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

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

    source: Optional[str] = Field(
        default=None, description="Source of the news article"
    )


class YFinanceCompanyNewsFetcher(
    Fetcher[
        YFinanceCompanyNewsQueryParams,
        list[YFinanceCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceCompanyNewsQueryParams:
        """Transform query params."""
        return YFinanceCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceCompanyNewsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from yfinance import Ticker

        results: list = []
        symbols = query.symbol.split(",")  # type: ignore
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        async def get_one(symbol):
            data = Ticker(symbol, session=session).get_news(
                count=query.limit,
                tab="all",
            )
            for d in data:
                new_content: dict = {}
                content = d.get("content")
                if not content:
                    continue
                if thumbnail := content.get("thumbnail"):
                    images = thumbnail.get("resolutions")
                    if images:
                        new_content["images"] = [
                            {k: str(v) for k, v in img.items()} for img in images
                        ]
                new_content["url"] = content.get("canonicalUrl", {}).get("url")
                new_content["source"] = content.get("provider", {}).get("displayName")
                new_content["title"] = content.get("title")
                new_content["date"] = content.get("pubDate")
                description = content.get("description")
                summary = content.get("summary")

                if description:
                    new_content["text"] = description
                elif summary:
                    new_content["text"] = summary

                results.append(new_content)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError("No data was returned for the given symbol(s)")

        return results

    @staticmethod
    def transform_data(
        query: YFinanceCompanyNewsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceCompanyNewsData]:
        """Transform data."""
        return [YFinanceCompanyNewsData.model_validate(d) for d in data]

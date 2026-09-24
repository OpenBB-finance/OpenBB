"""TMX Stock News model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field, field_validator


class TmxCompanyNewsQueryParams(CompanyNewsQueryParams):
    """TMX Stock News query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    page: int | None = Field(
        default=1, description="The page number to start from. Use with limit."
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def symbols_validate(cls, v):
        """Validate the symbols."""
        if v is None:
            raise OpenBBError("Symbol is a required field for TMX.")
        return v


class TmxCompanyNewsData(CompanyNewsData):
    """TMX Stock News Data."""

    __alias_dict__ = {
        "date": "datetime",
        "title": "headline",
    }

    source: str | None = Field(description="Source of the news.", default=None)

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Validate the datetime format."""
        # pylint: disable=import-outside-toplevel
        from zoneinfo import ZoneInfo

        dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(ZoneInfo("America/New_York"))


class TmxCompanyNewsFetcher(
    Fetcher[TmxCompanyNewsQueryParams, list[TmxCompanyNewsData]],
):
    """TMX Stock News Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxCompanyNewsQueryParams:
        """Transform the query."""
        return TmxCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxCompanyNewsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbols = query.symbol.split(",")  # type: ignore
        results: list[dict] = []

        async def create_task(symbol, results):
            """Fetch the news and events for a single symbol."""
            symbol = normalize_symbol(symbol)
            data = (
                await amake_gql_request(
                    "getNewsAndEvents",
                    gql.NEWS_AND_EVENTS,
                    {
                        "symbol": symbol,
                        "page": query.page or 1,
                        "limit": query.limit or 100,
                        "locale": "en",
                    },
                    symbol=symbol,
                )
                or {}
            )

            if data.get("news") is not None:
                news = data["news"]
                for i in range(len(news)):  # pylint: disable=C0200
                    url = f"https://money.tmx.com/quote/{symbol.upper()}/news/{news[i]['newsid']}"
                    news[i]["url"] = url
                    news[i].pop("newsid", None)
                    news[i].pop("summary", None)
                    news[i]["symbols"] = symbol
                results.extend(news)

            return results

        tasks = [create_task(symbol, results) for symbol in symbols]

        await asyncio.gather(*tasks)

        return sorted(results, key=lambda d: d["datetime"], reverse=True)

    @staticmethod
    def transform_data(
        query: TmxCompanyNewsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TmxCompanyNewsData]:
        """Return the transformed data."""
        return [TmxCompanyNewsData.model_validate(d) for d in data]

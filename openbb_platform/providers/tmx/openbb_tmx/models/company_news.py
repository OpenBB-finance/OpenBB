"""TMX Stock News model."""

# pylint: disable=unused-argument
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field, field_validator


class TmxCompanyNewsQueryParams(CompanyNewsQueryParams):
    """TMX Stock News query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    page: Optional[int] = Field(
        default=1, description="The page number to start from. Use with limit."
    )


class TmxCompanyNewsData(CompanyNewsData):
    """TMX Stock News Data"""

    __alias_dict__ = {
        "date": "datetime",
        "title": "headline",
    }

    source: Optional[str] = Field(description="Source of the news.", default=None)

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Validate the datetime format."""
        dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(pytz.timezone("America/New_York"))


class TmxCompanyNewsFetcher(
    Fetcher[TmxCompanyNewsQueryParams, List[TmxCompanyNewsData]],
):
    """TMX Stock News Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxCompanyNewsQueryParams:
        """Transform the query."""
        return TmxCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        user_agent = get_random_agent()
        symbols = query.symbol.split(",")
        results = []

        async def create_task(symbol, results):
            """Makes a POST request to the TMX GraphQL endpoint for a single symbol."""

            symbol = (
                symbol.upper().replace(".TO", "").replace(".TSX", "").replace("-", ".")
            )
            payload = gql.get_company_news_events_payload
            payload["variables"]["symbol"] = symbol
            payload["variables"]["page"] = query.page
            payload["variables"]["limit"] = query.limit
            payload["variables"]["locale"] = "en"
            url = "https://app-money.tmx.com/graphql"
            data = {}
            response = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )
            data = response["data"] if response.get("data") else data
            if data.get("news") is not None:
                news = data["news"]
                for i in range(len(news)):  # pylint: disable=C0200
                    url = f"https://money.tmx.com/quote/{symbol.upper()}/news/{news[i]['newsid']}"
                    news[i]["url"] = url
                    # The newsid was used to create the URL, so we drop it.
                    news[i].pop("newsid", None)
                    # The summary is a duplicated headline, so we drop it.
                    news[i].pop("summary", None)
                    # Add the symbol to the data for multi-ticker support.
                    news[i]["symbols"] = symbol
                results.extend(news)

            return results

        tasks = [create_task(symbol, results) for symbol in symbols]

        await asyncio.gather(*tasks)

        return sorted(results, key=lambda d: d["datetime"], reverse=True)

    @staticmethod
    def transform_data(
        query: TmxCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TmxCompanyNewsData]:
        """Return the transformed data."""
        return [TmxCompanyNewsData.model_validate(d) for d in data]

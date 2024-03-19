"""Intrinio Company News Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
    filter_by_dates,
    get_querystring,
)
from pydantic import Field, field_validator


class IntrinioCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Intrinio Company News Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_news_v2
    """

    __alias_dict__ = {"symbol": "symbols", "limit": "page_size"}
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class IntrinioCompanyNewsData(CompanyNewsData):
    """Intrinio Company News Data."""

    __alias_dict__ = {
        "symbols": "symbol",
        "date": "publication_date",
        "text": "summary",
    }

    id: str = Field(description="Article ID.")

    @field_validator("publication_date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.000Z")


class IntrinioCompanyNewsFetcher(
    Fetcher[
        IntrinioCompanyNewsQueryParams,
        List[IntrinioCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCompanyNewsQueryParams:
        """Transform the query params."""
        return IntrinioCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbols", "page"]
        )

        async def callback(response: ClientResponse, _: Any) -> List[Dict]:
            """Return the response."""
            if response.status != 200:
                return []

            symbol = response.url.parts[-2]
            data = await response.json()

            return [{**d, "symbol": symbol} for d in data.get("news", [])]

        urls = [
            f"{base_url}/{symbol}/news?{query_str}&api_key={api_key}"
            for symbol in [s.strip() for s in query.symbol.split(",")]
        ]

        return await amake_requests(urls, callback, **kwargs)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: IntrinioCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCompanyNewsData]:
        """Return the transformed data."""
        modeled_data = [IntrinioCompanyNewsData.model_validate(d) for d in data]
        return filter_by_dates(modeled_data, query.start_date, query.end_date)  # type: ignore

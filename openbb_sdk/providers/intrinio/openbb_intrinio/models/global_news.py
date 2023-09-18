"""Intrinio Global News fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_intrinio.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator


class IntrinioGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Intrinio Global News query.

    Source: https://docs.intrinio.com/documentation/web_api/get_all_company_news_v2
    """

    next_page: str = Field(
        default=None,
        description="Token to get the next page of data from a previous API call.",
    )
    limit: Optional[int] = Field(
        default=10, description="The number of data entries to return."
    )
    all_pages: Optional[bool] = Field(
        default=False,
        description="Returns all pages of data from the API call at once.",
    )


class IntrinioGlobalNewsData(GlobalNewsData):
    """Intrinio Global News Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "date": "publication_date",
            "text": "summary",
        }

    id: str = Field(description="Article ID.")
    company: Dict[str, Any] = Field(
        description="Company details related to the news article."
    )

    @validator("publication_date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.000Z")


class IntrinioGlobalNewsFetcher(
    Fetcher[
        IntrinioGlobalNewsQueryParams,
        List[IntrinioGlobalNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioGlobalNewsQueryParams:
        """Transform the query params."""

        return IntrinioGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.dict(by_alias=True), ["all_pages", "page"])
        query_str = query_str.replace("limit", "page_size")
        url = f"{base_url}/companies/news?{query_str}&api_key={api_key}"

        data = get_data_one(url, **kwargs)

        if query.all_pages:
            all_data = data["news"]
            next_page = data["next_page"]

            while next_page:
                query_str = get_querystring(
                    query.dict(by_alias=True), ["page", "next_page", "all_pages"]
                )
                query_str = query_str.replace("limit", "page_size")
                url = (
                    f"{base_url}/companies/news?{query_str}&next_page={next_page}"
                    f"&api_key={api_key}"
                )

                data = get_data_one(url, **kwargs)
                all_data.extend(data.get("news", []))

                next_page = data.get("next_page", None)

            return all_data["news"]

        return data.get("news", [])

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioGlobalNewsData]:
        """Return the transformed data."""

        return [IntrinioGlobalNewsData(**d) for d in data]

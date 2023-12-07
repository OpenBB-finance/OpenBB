"""Intrinio Company News Model."""


from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many
from pydantic import Field, field_validator


class IntrinioCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Intrinio Company News Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_news_v2
    """

    __alias_dict__ = {"page": "next_page", "limit": "page_size"}

    symbols: str = Field(
        description="A comma separated list of Company identifiers (Ticker, CIK, LEI, Intrinio ID)."
    )


class IntrinioCompanyNewsData(CompanyNewsData):
    """Intrinio Company News Data."""

    __alias_dict__ = {
        "symbols": "symbol",
        "date": "publication_date",
        "text": "summary",
    }

    id: str = Field(description="Intrinio ID for the article.")

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
    def extract_data(
        query: IntrinioCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        results: List[Dict] = []

        def get_data(symbol):
            base_url = "https://api-v2.intrinio.com/companies"
            query_str = get_querystring(query.model_dump(by_alias=True), ["symbols"])
            url = f"{base_url}/{symbol}/news?{query_str}&api_key={api_key}"
            data = get_data_many(url, "news", **kwargs)
            data = [{**d, "symbol": symbol} for d in data]
            results.append(data)

        with ThreadPoolExecutor() as executor:
            executor.map(get_data, [s.strip() for s in query.symbols.split(",")])

        results = [item for sublist in results for item in sublist]
        return results

    @staticmethod
    def transform_data(
        query: IntrinioCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCompanyNewsData]:
        """Return the transformed data."""
        return [IntrinioCompanyNewsData.model_validate(d) for d in data]

"""FMP Global News fetcher."""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from pydantic import Field, validator


class FMPGlobalNewsQueryParams(GlobalNewsQueryParams):
    """FMP Global News query.

    Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/
    """


class FMPGlobalNewsData(GlobalNewsData):
    """FMP Global News Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {"date": "publishedDate"}

    site: str = Field(description="Site of the news.")

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")


class FMPGlobalNewsFetcher(
    Fetcher[
        FMPGlobalNewsQueryParams,
        List[FMPGlobalNewsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPGlobalNewsQueryParams:
        """Transform the query params."""
        return FMPGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v4"

        pages = math.ceil(query.limit / 20)
        data = []

        for page in range(pages):
            url = f"{base_url}/general_news?page={page}&apikey={api_key}"
            response = get_data_many(url, **kwargs)
            data.extend(response)

        data = sorted(data, key=lambda x: x["publishedDate"], reverse=True)
        data = data[: query.limit]

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPGlobalNewsData]:
        """Return the transformed data."""
        return [FMPGlobalNewsData.parse_obj(d) for d in data]

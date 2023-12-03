"""FMP World News Model."""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, field_validator


class FMPWorldNewsQueryParams(WorldNewsQueryParams):
    """FMP World News Query.

    Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/
    """


class FMPWorldNewsData(WorldNewsData):
    """FMP World News Data."""

    __alias_dict__ = {"date": "publishedDate", "images": "image"}

    site: str = Field(description="Site of the news.")

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")


class FMPWorldNewsFetcher(
    Fetcher[
        FMPWorldNewsQueryParams,
        List[FMPWorldNewsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPWorldNewsQueryParams:
        """Transform the query params."""
        return FMPWorldNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPWorldNewsQueryParams,
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
    def transform_data(
        query: FMPWorldNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPWorldNewsData]:
        """Return the transformed data."""
        for d in data:
            if isinstance(d["image"], str):
                d["image"] = [{"url": d["image"]}]

        return [FMPWorldNewsData.model_validate(d) for d in data]

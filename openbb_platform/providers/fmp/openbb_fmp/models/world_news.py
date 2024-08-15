"""FMP World News Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class FMPWorldNewsQueryParams(WorldNewsQueryParams):
    """FMP World News Query.

    Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/
    """


class FMPWorldNewsData(WorldNewsData):
    """FMP World News Data."""

    __alias_dict__ = {"date": "publishedDate", "images": "image"}

    site: str = Field(description="News source.")

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")

    @field_validator("images", mode="before", check_fields=False)
    @classmethod
    def images_validate(cls, v):
        """Conform the response to a list."""
        if isinstance(v, str):
            return [{"o": v}]
        return v if isinstance(v, list) else None


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
        if params.get("start_date") or params.get("end_date"):
            warn("start_date and end_date are not supported for this endpoint.")
        return FMPWorldNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPWorldNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import math  # noqa
        import asyncio
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""
        pages = math.ceil(query.limit / 20)
        base_url = "https://financialmodelingprep.com/api/v4"
        results: List = []

        async def get_one(url):
            """Get data for one URL."""
            data = await amake_request(url, response_callback=response_callback)
            if data:
                results.extend(data)

        urls = [
            f"{base_url}/general_news?page={page}&apikey={api_key}"
            for page in range(pages)
        ]
        await asyncio.gather(*[get_one(url) for url in urls])

        if results:
            data = sorted(results, key=lambda x: x["publishedDate"], reverse=True)

            return data[: query.limit]
        raise EmptyDataError("The request was returned empty.")

    @staticmethod
    def transform_data(
        query: FMPWorldNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPWorldNewsData]:
        """Return the transformed data."""
        return [FMPWorldNewsData.model_validate(d) for d in data]

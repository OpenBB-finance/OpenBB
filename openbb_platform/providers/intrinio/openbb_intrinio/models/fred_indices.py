"""Intrinio FRED Indices Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_indices import (
    FredIndicesData,
    FredIndicesQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import async_get_data_one
from pydantic import Field


class IntrinioFredIndicesQueryParams(FredIndicesQueryParams):
    """Intrinio FRED Indices Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_economic_index_historical_data_v2
    """

    __alias_dict__ = {"limit": "page_size"}

    next_page: Optional[str] = Field(
        default=None,
        description="Token to get the next page of data from a previous API call.",
    )
    all_pages: Optional[bool] = Field(
        default=False,
        description="Returns all pages of data from the API call at once.",
    )
    sleep: Optional[float] = Field(
        default=1.0,
        description="Time to sleep between requests to avoid rate limiting.",
    )


class IntrinioFredIndicesData(FredIndicesData):
    """Intrinio FRED Indices Data."""


class IntrinioFredIndicesFetcher(
    Fetcher[
        IntrinioFredIndicesQueryParams,
        List[IntrinioFredIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioFredIndicesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioFredIndicesQueryParams(**transformed_params)

    @staticmethod
    async def extract_data(
        query: IntrinioFredIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(
            query.model_dump(), ["symbol", "all_pages", "sleep"]
        )

        url = (
            f"{base_url}/indices/economic/${query.symbol.replace('$', '')}/historical_data/level"
            f"?{query_str}&api_key={api_key}"
        )

        data = await async_get_data_one(url, query.limit, query.sleep, **kwargs)

        if query.all_pages:
            all_data: list = data.get("historical_data", [])
            next_page = data.get("next_page", None)

            while next_page:
                query_str = get_querystring(
                    query.model_dump(), ["symbol", "next_page", "all_pages", "sleep"]
                )

                url = (
                    f"{base_url}/indices/economic/${query.symbol.replace('$', '')}/historical_data/level"
                    f"?{query_str}&next_page={next_page}&api_key={api_key}"
                )

                data = await async_get_data_one(url, query.limit, query.sleep, **kwargs)

                all_data.extend(data.get("historical_data", []))

                next_page = data.get("next_page", None)

            return all_data

        return data.get("historical_data", [])

    @staticmethod
    def transform_data(
        query: IntrinioFredIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioFredIndicesData]:
        """Return the transformed data."""
        return [IntrinioFredIndicesData.model_validate(d) for d in data]

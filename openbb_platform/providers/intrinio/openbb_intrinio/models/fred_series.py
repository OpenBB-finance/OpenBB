"""Intrinio FRED Series Model."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
    get_querystring,
)
from pydantic import Field


class IntrinioFredSeriesQueryParams(SeriesQueryParams):
    """Intrinio FRED Series Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_economic_index_historical_data_v2
    """

    __alias_dict__ = {"limit": "page_size"}

    all_pages: Optional[bool] = Field(
        default=False,
        description="Returns all pages of data from the API call at once.",
    )
    sleep: Optional[float] = Field(
        default=1.0,
        description="Time to sleep between requests to avoid rate limiting.",
    )


class IntrinioFredSeriesData(SeriesData):
    """Intrinio FRED Series Data."""

    value: Optional[float] = Field(default=None, description="Value of the index.")


class IntrinioFredSeriesFetcher(
    Fetcher[
        IntrinioFredSeriesQueryParams,
        List[IntrinioFredSeriesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioFredSeriesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioFredSeriesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioFredSeriesQueryParams,
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

        async def callback(response: ClientResponse, session: ClientSession) -> dict:
            """Return the response."""
            init_response = await response.json()

            all_data: list = init_response.get("historical_data", [])

            if query.all_pages:
                next_page = init_response.get("next_page", None)
                while next_page:
                    if query.limit > 100:
                        await asyncio.sleep(query.sleep)

                    url = response.url.update_query(next_page=next_page).human_repr()
                    response_data = await session.get_json(url)

                    all_data.extend(response_data.get("historical_data", []))
                    next_page = response_data.get("next_page", None)

            return all_data

        return await amake_requests([url], callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioFredSeriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioFredSeriesData]:
        """Return the transformed data."""
        return [IntrinioFredSeriesData.model_validate(d) for d in data]

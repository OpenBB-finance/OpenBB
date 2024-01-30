"""Intrinio Latest Attributes Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.latest_attributes import (
    LatestAttributesData,
    LatestAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)


class IntrinioLatestAttributesQueryParams(LatestAttributesQueryParams):
    """Intrinio Latest Attributes Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_data_point_number_v2
            https://docs.intrinio.com/documentation/web_api/get_data_point_text_v2
    """


class IntrinioLatestAttributesData(LatestAttributesData):
    """Intrinio Latest Attributes Data."""


class IntrinioLatestAttributesFetcher(
    Fetcher[
        IntrinioLatestAttributesQueryParams,
        List[IntrinioLatestAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioLatestAttributesQueryParams:
        """Transform the query params."""
        return IntrinioLatestAttributesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioLatestAttributesQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"

        def generate_url(tag: str) -> str:
            """Returns the url for the given tag."""
            return f"{base_url}/{query.symbol}/data_point/{tag}?api_key={api_key}"

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            response_data = await response.json()
            tag = response.url.parts[-1]
            data = {"tag": tag, "value": response_data}

            return data

        urls = [generate_url(tag) for tag in query.tag.split(",")]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioLatestAttributesQueryParams,  # pylint: disable=unused-argument
        data: Dict,
        **kwargs: Any,
    ) -> List[IntrinioLatestAttributesData]:
        """Return the transformed data."""
        return [IntrinioLatestAttributesData.model_validate(d) for d in data]

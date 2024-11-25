"""Intrinio Latest Attributes Model."""

import warnings
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.warning import OpenBBWarning
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

    __json_schema_extra__ = {
        "tag": {"multiple_items_allowed": True},
        "symbol": {"multiple_items_allowed": True},
    }


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

        def generate_url(symbol: str, tag: str) -> str:
            """Return the url for the given symbol and tag."""
            return f"{base_url}/{symbol}/data_point/{tag}?api_key={api_key}"

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            response_data = await response.json()

            if isinstance(response_data, Dict) and (
                "error" in response_data or "message" in response_data
            ):
                warnings.warn(
                    message=str(response_data.get("error"))
                    or str(response_data.get("message")),
                    category=OpenBBWarning,
                )
                return {}
            if not response_data:
                return {}

            tag = response.url.parts[-1]
            symbol = response.url.parts[-3]

            return {"symbol": symbol, "tag": tag, "value": response_data}

        urls = [
            generate_url(symbol, tag)
            for symbol in query.symbol.split(",")
            for tag in query.tag.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioLatestAttributesQueryParams,  # pylint: disable=unused-argument
        data: Dict,
        **kwargs: Any,
    ) -> List[IntrinioLatestAttributesData]:
        """Return the transformed data."""
        return [IntrinioLatestAttributesData.model_validate(d) for d in data]

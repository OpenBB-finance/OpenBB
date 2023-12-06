"""Intrinio Search Attributes Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.search_attributes import (
    SearchAttributesData,
    SearchAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_one


class IntrinioSearchAttributesQueryParams(SearchAttributesQueryParams):
    """Intrinio Search Attributes Query.

    Source: https://docs.intrinio.com/documentation/web_api/search_data_tags_v2
    """

    __alias_dict__ = {"limit": "page_size"}


class IntrinioSearchAttributesData(SearchAttributesData):
    """Intrinio Search Attributes Data."""

    __alias_dict__ = {
        "parent_name": "parent",
        "transaction": "balance",
    }


class IntrinioSearchAttributesFetcher(
    Fetcher[
        IntrinioSearchAttributesQueryParams,
        List[IntrinioSearchAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioSearchAttributesQueryParams:
        """Transform the query params."""
        return IntrinioSearchAttributesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioSearchAttributesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.model_dump(by_alias=True), [])

        url = f"{base_url}/data_tags/search?{query_str}&api_key={api_key}"
        data = await get_data_one(url, **kwargs)

        # Intrinio doesn't return the correct number of results when using the limit parameter
        # Temporary fix until they fix it
        data = data.get("tags", [])[: query.limit]

        return data

    @staticmethod
    def transform_data(
        query: IntrinioSearchAttributesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioSearchAttributesData]:
        """Return the transformed data."""
        return [IntrinioSearchAttributesData.model_validate(item) for item in data]

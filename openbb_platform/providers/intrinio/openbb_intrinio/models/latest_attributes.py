"""Intrinio Latest Attributes Model."""

from typing import Any, Dict, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.latest_attributes import (
    LatestAttributesData,
    LatestAttributesQueryParams,
)
from openbb_intrinio.utils.helpers import get_data


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
        IntrinioLatestAttributesData,
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioLatestAttributesQueryParams:
        """Transform the query params."""
        return IntrinioLatestAttributesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioLatestAttributesQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        url = f"https://api-v2.intrinio.com/companies/{query.symbol}/data_point/{query.tag}?api_key={api_key}"
        return get_data(url)

    @staticmethod
    def transform_data(
        query: IntrinioLatestAttributesQueryParams,  # pylint: disable=unused-argument
        data: Dict,
        **kwargs: Any,
    ) -> IntrinioLatestAttributesData:
        """Return the transformed data."""
        return IntrinioLatestAttributesData.model_validate(data)

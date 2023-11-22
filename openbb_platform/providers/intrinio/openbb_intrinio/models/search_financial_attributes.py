"""Intrinio Search Financial Attributes Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.search_financial_attributes import (
    SearchFinancialAttributesData,
    SearchFinancialAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_one


class IntrinioSearchFinancialAttributesQueryParams(
    SearchFinancialAttributesQueryParams
):
    """Intrinio Search Financial Attributes Query."""

    __alias_dict__ = {"limit": "page_size"}


class IntrinioSearchFinancialAttributesData(SearchFinancialAttributesData):
    """Intrinio Search Financial Attributes Data."""

    __alias_dict__ = {
        "parent_name": "parent",
        "transaction": "balance",
    }


class IntrinioSearchFinancialAttributesFetcher(
    Fetcher[
        IntrinioSearchFinancialAttributesQueryParams,
        List[IntrinioSearchFinancialAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioSearchFinancialAttributesQueryParams:
        """Transform the query params."""
        return IntrinioSearchFinancialAttributesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioSearchFinancialAttributesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data: List[Dict] = []

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.model_dump(by_alias=True), [])

        url = f"{base_url}/data_tags/search?{query_str}&api_key={api_key}"
        data = get_data_one(url).get("tags", [])
        # Intrinio doesn't return the correct number of results when using the limit parameter
        # Temporary fix until they fix it
        data = data[: query.limit]

        return data

    @staticmethod
    def transform_data(
        query: IntrinioSearchFinancialAttributesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioSearchFinancialAttributesData]:
        """Return the transformed data."""
        return [
            IntrinioSearchFinancialAttributesData.model_validate(item) for item in data
        ]

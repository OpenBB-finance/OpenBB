"""Intrinio Financial Attributes Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_attributes import (
    FinancialAttributesData,
    FinancialAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many


class IntrinioFinancialAttributesQueryParams(FinancialAttributesQueryParams):
    """Intrinio Financial Attributes Query."""

    __alias_dict__ = {"sort": "sort_order", "limit": "page_size"}


class IntrinioFinancialAttributesData(FinancialAttributesData):
    """Intrinio Financial Attributes Data."""


class IntrinioFinancialAttributesFetcher(
    Fetcher[
        IntrinioFinancialAttributesQueryParams,
        List[IntrinioFinancialAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioFinancialAttributesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioFinancialAttributesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioFinancialAttributesQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        frequency = "yearly" if query.period == "annual" else "quarterly"
        data: List[Dict] = []

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.model_dump(by_alias=True), ["frequency"])
        query_str = f"{query_str}&frequency={frequency}"

        url = f"{base_url}/historical_data/{query.symbol}/{query.tag}?{query_str}&api_key={api_key}"
        # data = get_data_one(url).get("historical_data", [])
        data = await get_data_many(url, "historical_data")

        return data

    @staticmethod
    def transform_data(
        query: IntrinioFinancialAttributesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioFinancialAttributesData]:
        """Return the transformed data."""
        return [IntrinioFinancialAttributesData.model_validate(item) for item in data]

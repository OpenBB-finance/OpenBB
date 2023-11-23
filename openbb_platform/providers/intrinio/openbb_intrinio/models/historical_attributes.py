"""Intrinio Historical Attributes Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_attributes import (
    HistoricalAttributesData,
    HistoricalAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many


class IntrinioHistoricalAttributesQueryParams(HistoricalAttributesQueryParams):
    """Intrinio Historical Attributes Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_historical_data_v2
    """

    __alias_dict__ = {"sort": "sort_order", "limit": "page_size"}


class IntrinioHistoricalAttributesData(HistoricalAttributesData):
    """Intrinio Historical Attributes Data."""


class IntrinioHistoricalAttributesFetcher(
    Fetcher[
        IntrinioHistoricalAttributesQueryParams,
        List[IntrinioHistoricalAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioHistoricalAttributesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioHistoricalAttributesQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: IntrinioHistoricalAttributesQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol", "tag"])

        url = f"{base_url}/historical_data/{query.symbol}/{query.tag}?{query_str}&api_key={api_key}"
        return get_data_many(url, "historical_data")

    @staticmethod
    def transform_data(
        query: IntrinioHistoricalAttributesQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioHistoricalAttributesData]:
        """Return the transformed data."""
        return [IntrinioHistoricalAttributesData.model_validate(d) for d in data]

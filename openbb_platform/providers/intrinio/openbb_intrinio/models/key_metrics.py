"""Intrinio Key Metrics Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioKeyMetricsQueryParams(KeyMetricsQueryParams):
    """Intrinio Key Metrics Query.

    Source: https://data.intrinio.com/data-tag/beta
            https://data.intrinio.com/data-tag/volume
            https://data.intrinio.com/data-tag/52_week_high
            https://data.intrinio.com/data-tag/52_week_low
            https://data.intrinio.com/data-tag/dividendyield
            https://data.intrinio.com/data-tag/pricetoearnings
    """


class IntrinioKeyMetricsData(KeyMetricsData):
    """Intrinio Key Metrics Data."""

    __alias_dict__ = {
        "market_cap": "marketcap",
        "pe_ratio": "pricetoearnings",
    }

    beta: float = Field(description="Beta")
    volume: float = Field(description="Volume")
    fifty_two_week_high: float = Field(description="52 week high", alias="52_week_high")
    fifty_two_week_low: float = Field(description="52 week low", alias="52_week_low")
    dividend_yield: float = Field(description="Dividend yield", alias="dividendyield")


class IntrinioKeyMetricsFetcher(
    Fetcher[
        IntrinioKeyMetricsQueryParams,
        IntrinioKeyMetricsData,
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioKeyMetricsQueryParams:
        """Transform the query params."""
        return IntrinioKeyMetricsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioKeyMetricsQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data: Dict = {}
        tags = [
            "beta",
            "volume",
            "marketcap",
            "52_week_high",
            "52_week_low",
            "dividendyield",
            "pricetoearnings",
        ]

        data["symbol"] = query.symbol
        for tag in tags:
            url = f"https://api-v2.intrinio.com/companies/{query.symbol}/data_point/{tag}?api_key={api_key}"
            data[tag] = get_data_one(url).get("value")

        return data

    @staticmethod
    def transform_data(
        query: IntrinioKeyMetricsQueryParams, data: List[Dict], **kwargs: Any
    ) -> IntrinioKeyMetricsData:
        """Return the transformed data."""
        return IntrinioKeyMetricsData.model_validate(data)

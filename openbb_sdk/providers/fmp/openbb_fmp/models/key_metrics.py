"""Key Metrics fetcher."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Key Metrics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/
    """


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Key Metrics Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "pocf_ratio": "pocfratio",
            "research_and_development_to_revenue": "researchAndDdevelopementToRevenue",
        }


class FMPKeyMetricsFetcher(
    Fetcher[
        FMPKeyMetricsQueryParams,
        List[FMPKeyMetricsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPKeyMetricsQueryParams:
        """Transform the query params."""
        return FMPKeyMetricsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        data: List[Dict] = []

        def multiple_symbols(symbol: str, data: List[Dict]) -> None:
            url = create_url(
                3, f"key-metrics/{symbol}", api_key, query, exclude=["symbol"]
            )
            return data.extend(get_data_many(url, **kwargs))

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPKeyMetricsData]:
        """Return the transformed data."""
        return [FMPKeyMetricsData.parse_obj(d) for d in data]

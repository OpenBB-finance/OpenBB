"""FMP Stock Multiples Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_multiples import (
    StockMultiplesData,
    StockMultiplesQueryParams,
)


class FMPStockMultiplesQueryParams(StockMultiplesQueryParams):
    """FMP Stock Multiples Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Company-Key-Metrics
    """


class FMPStockMultiplesData(StockMultiplesData):
    """FMP Stock Multiples Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "pocf_ratio_ttm": "pocfratioTTM",
            "enterprise_value_over_ebitda_ttm": "enterpriseValueOverEBITDATTM",
            "net_debt_to_ebitda_ttm": "netDebtToEBITDATTM",
            "research_and_development_to_revenue_ttm": "researchAndDevelopementToRevenueTTM",
        }


class FMPStockMultiplesFetcher(
    Fetcher[
        FMPStockMultiplesQueryParams,
        List[FMPStockMultiplesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockMultiplesQueryParams:
        """Transform the query params."""
        return FMPStockMultiplesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockMultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = create_url(
            3, f"key-metrics-ttm/{query.symbol}", api_key, query, exclude=["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPStockMultiplesData]:
        """Return the transformed data."""
        return [FMPStockMultiplesData.parse_obj(d) for d in data]

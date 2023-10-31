"""FMP Price Performance Model."""

from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from pydantic import Field


class FMPPricePerformanceQueryParams(RecentPerformanceQueryParams):
    """FMP Price Performance query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/
    """


class FMPPricePerformanceData(RecentPerformanceData):
    """FMP Price Performance data."""

    symbol: str = Field(description="The ticker symbol.")

    __alias_dict__ = {
        "one_day": "1D",
        "one_week": "5D",
        "one_month": "1M",
        "three_month": "3M",
        "six_month": "6M",
        "one_year": "1Y",
        "three_year": "3Y",
        "five_year": "5Y",
        "ten_year": "10Y",
    }


class FMPPricePerformanceFetcher(
    Fetcher[
        FMPPricePerformanceQueryParams,
        List[FMPPricePerformanceData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPricePerformanceQueryParams:
        """Transform the query params."""
        return FMPPricePerformanceQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPricePerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/api/v3/stock-price-change/{query.symbol}?apikey={api_key}"

        data = get_data_one(url, **kwargs)
        return data if 0 in data else {0: data}

    @staticmethod
    def transform_data(
        query: FMPPricePerformanceQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[FMPPricePerformanceData]:
        """Transform the raw data into the standard model."""
        return [FMPPricePerformanceData.model_validate(data[i]) for i in data]

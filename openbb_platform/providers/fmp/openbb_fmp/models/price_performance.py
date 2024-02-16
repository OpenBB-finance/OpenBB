"""FMP Price Performance Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPPricePerformanceQueryParams(RecentPerformanceQueryParams):
    """FMP Price Performance Query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FMPPricePerformanceData(RecentPerformanceData):
    """FMP Price Performance Data."""

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

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Replace zero with None and convert percents to normalized values."""
        if isinstance(values, dict):
            for k, v in values.items():
                if k != "symbol":
                    values[k] = None if v == 0 else float(v) / 100
        return values


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
    async def aextract_data(
        query: FMPPricePerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint=f"stock-price-change/{query.symbol}",
            api_key=api_key,
            exclude=["symbol"],
        )
        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPPricePerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPPricePerformanceData]:
        """Return the transformed data."""
        return [FMPPricePerformanceData.model_validate(i) for i in data]

"""FMP Key Metrics Model."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many, get_data_one
from pydantic import Field


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Key Metrics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/
    """

    with_ttm: Optional[bool] = Field(
        default=False, description="Include trailing twelve months (TTM) data."
    )


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Key Metrics Data."""

    __alias_dict__ = {
        "pocf_ratio": "pocfratio",
        "research_and_development_to_revenue": "researchAndDdevelopementToRevenue",
        "net_debt_to_ebitda": "netDebtToEBITDA",
        "enterprise_value_over_ebitda": "enterpriseValueOverEBITDA",
    }

    calendar_year: Optional[ForceInt] = Field(
        default=None, description="Calendar year."
    )


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
        base_url = "https://financialmodelingprep.com/api/v3"

        data: List[Dict] = []

        def multiple_symbols(symbol: str, data: List[Dict]) -> None:
            url = (
                f"{base_url}/key-metrics/{symbol}?"
                f"period={query.period}&limit={query.limit}&apikey={api_key}"
            )

            # TTM data
            ttm_url = f"{base_url}/key-metrics-ttm/{symbol}?&apikey={api_key}"
            if query.with_ttm and (metrics_ttm := get_data_one(ttm_url, **kwargs)):
                data.append(
                    {
                        "symbol": symbol,
                        "period": "TTM",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "calendar_year": datetime.now().year,
                        **{k.replace("TTM", ""): v for k, v in metrics_ttm.items()},
                    }
                )

            return data.extend(get_data_many(url, **kwargs))

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        return data

    @staticmethod
    def transform_data(
        query: FMPKeyMetricsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPKeyMetricsData]:
        """Return the transformed data."""
        return [FMPKeyMetricsData.model_validate(d) for d in data]

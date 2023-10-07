"""FMP Historical EPS Calendar."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.historical_eps import (
    HistoricalEpsData,
    HistoricalEpsQueryParams,
)
from pydantic import Field


class FMPHistoricalEpsQueryParams(HistoricalEpsQueryParams):
    """FMP Historical EPS Query.

    Source: https://site.financialmodelingprep.com/developer/docs#earnings-historical-earnings
    """


class FMPHistoricalEpsData(HistoricalEpsData):
    """FMP Historical EPS Data."""

    __alias_dict__ = {
        "eps_actual": "eps",
        "eps_estimated": "epsEstimated",
        "announce_time": "time",
    }

    revenue: Optional[float] = Field(
        default=None, description="Revenue for the earnings date."
    )
    revenue_estimated: Optional[float] = Field(
        default=None,
        description="Estimated revenue for the earnings date.",
        alias="revenueEstimated",
    )
    fiscal_date_ending: Optional[dateType] = Field(
        default=None, description="Fiscal date ending for the reporting period."
    )
    updated_from_date: Optional[dateType] = Field(
        default=None, description="Updated from date."
    )


class FMPHistoricalEpsFetcher(
    Fetcher[
        FMPHistoricalEpsQueryParams,
        List[FMPHistoricalEpsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalEpsQueryParams:
        """Transform the query params."""
        return FMPHistoricalEpsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPHistoricalEpsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{query.symbol}?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPHistoricalEpsData]:
        """Return the transformed data."""
        return [FMPHistoricalEpsData.model_validate(d) for d in data]

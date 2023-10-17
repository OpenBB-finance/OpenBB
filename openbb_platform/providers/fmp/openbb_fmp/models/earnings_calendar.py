"""FMP Earnings Calendar fetcher."""


from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.earnings_calendar import (
    EarningsCalendarData,
    EarningsCalendarQueryParams,
)
from pydantic import Field


class FMPEarningsCalendarQueryParams(EarningsCalendarQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs#earnings-calendar-earnings
    """


class FMPEarningsCalendarData(EarningsCalendarData):
    """FMP Earnings Calendar Data."""

    __alias_dict__ = {
        "eps_actual": "eps",
        "eps_estimated": "epsEstimated",
        "announce_time": "time",
    }

    revenue: Optional[float] = Field(
        default=None, description="Revenue of the earnings calendar."
    )
    revenue_estimated: Optional[float] = Field(
        default=None,
        description="Estimated revenue of the earnings calendar.",
        alias="revenueEstimated",
    )
    fiscal_date_ending: Optional[dateType] = Field(
        default=None, description="Fiscal date ending for the company reporting."
    )
    updated_from_date: Optional[dateType] = Field(
        default=None, description="Updated from date."
    )


class FMPEarningsCalendarFetcher(
    Fetcher[
        FMPEarningsCalendarQueryParams,
        List[FMPEarningsCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEarningsCalendarQueryParams:
        """Transform the query params."""
        return FMPEarningsCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEarningsCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        if query.date:
            query.start_date = query.date
            query.end_date = query.date

        BASE_URL = "https://financialmodelingprep.com/api/v3/"
        url = (
            BASE_URL
            + f"earning_calendar?from={query.start_date}&to={query.end_date}&apikey={api_key}"
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEarningsCalendarQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEarningsCalendarData]:
        """Return the transformed data."""
        return [FMPEarningsCalendarData.model_validate(d) for d in data]

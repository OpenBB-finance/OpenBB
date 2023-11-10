"""FMP Earnings Calendar fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from pydantic import field_validator


class FMPCalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/
    """


class FMPCalendarEarningsData(CalendarEarningsData):
    """FMP Earnings Calendar Data."""

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @field_validator("updatedFromDate", mode="before", check_fields=False)
    def updated_from_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the updated from date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @field_validator("fiscalDateEnding", mode="before", check_fields=False)
    def fiscal_date_ending_validate(cls, v: str):  # pylint: disable=E0213
        """Return the fiscal date ending as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPCalendarEarningsFetcher(
    Fetcher[
        FMPCalendarEarningsQueryParams,
        List[FMPCalendarEarningsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCalendarEarningsQueryParams:
        """Transform the query params."""
        return FMPCalendarEarningsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCalendarEarningsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"historical/earning_calendar/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCalendarEarningsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCalendarEarningsData]:
        """Return the transformed data."""
        return [FMPCalendarEarningsData.model_validate(d) for d in data]

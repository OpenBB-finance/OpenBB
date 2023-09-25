"""FMP Earnings Calendar fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.earnings_calendar import (
    EarningsCalendarData,
    EarningsCalendarQueryParams,
)
from pydantic import validator


class FMPEarningsCalendarQueryParams(EarningsCalendarQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/
    """


class FMPEarningsCalendarData(EarningsCalendarData):
    """FMP Earnings Calendar Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("updatedFromDate", pre=True, check_fields=False)
    def updated_from_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the updated from date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("fiscalDateEnding", pre=True, check_fields=False)
    def fiscal_date_ending_validate(cls, v: str):  # pylint: disable=E0213
        """Return the fiscal date ending as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


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

        url = create_url(
            3, f"historical/earning_calendar/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPEarningsCalendarData]:
        """Return the transformed data."""
        return [FMPEarningsCalendarData.parse_obj(d) for d in data]

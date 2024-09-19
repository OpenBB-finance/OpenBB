"""FMP Earnings Calendar Model."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator


class FMPCalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/
    """

    __alias_dict__ = {
        "start_date": "from",
        "end_date": "to",
    }


class FMPCalendarEarningsData(CalendarEarningsData):
    """FMP Earnings Calendar Data."""

    __alias_dict__ = {
        "report_date": "date",
        "eps_consensus": "epsEstimated",
        "eps_actual": "eps",
        "revenue_actual": "revenue",
        "revenue_consensus": "revenueEstimated",
        "period_ending": "fiscalDateEnding",
        "reporting_time": "time",
        "updated_date": "updatedFromDate",
    }

    eps_actual: Optional[float] = Field(
        default=None,
        description="The actual earnings per share announced.",
    )
    revenue_actual: Optional[float] = Field(
        default=None,
        description="The actual reported revenue.",
    )
    revenue_consensus: Optional[float] = Field(
        default=None,
        description="The revenue forecast consensus.",
    )
    period_ending: Optional[dateType] = Field(
        default=None,
        description="The fiscal period end date.",
    )
    reporting_time: Optional[str] = Field(
        default=None,
        description="The reporting time - e.g. after market close.",
    )
    updated_date: Optional[dateType] = Field(
        default=None,
        description="The date the data was updated last.",
    )

    @field_validator(
        "report_date",
        "updated_date",
        "period_ending",
        mode="before",
        check_fields=False,
    )
    def date_validate(cls, v: Union[datetime, str]):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        return datetime.strftime(v, "%Y-%m-%d") if v else None


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
        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return FMPCalendarEarningsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCalendarEarningsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(3, "earning_calendar", api_key, query, [])

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCalendarEarningsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCalendarEarningsData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["date"], reverse=True)
        return [FMPCalendarEarningsData.model_validate(d) for d in data]

"""FMP Earnings Calendar Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from pydantic import Field, field_validator


class FMPCalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs#earnings-calendar
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
        "eps_actual": "epsActual",
        "revenue_actual": "revenueActual",
        "revenue_consensus": "revenueEstimated",
        "last_updated": "lastUpdated",
    }

    eps_actual: float | None = Field(
        default=None,
        description="The actual earnings per share announced.",
    )
    revenue_consensus: float | None = Field(
        default=None,
        description="The revenue forecast consensus.",
    )
    revenue_actual: float | None = Field(
        default=None,
        description="The actual reported revenue.",
    )
    last_updated: dateType | None = Field(
        default=None,
        description="The date the data was updated last.",
    )

    @field_validator(
        "report_date",
        "last_updated",
        mode="before",
        check_fields=False,
    )
    def date_validate(cls, v: datetime | str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        return datetime.strftime(v, "%Y-%m-%d") if v else None


class FMPCalendarEarningsFetcher(
    Fetcher[
        FMPCalendarEarningsQueryParams,
        list[FMPCalendarEarningsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCalendarEarningsQueryParams:
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
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_requests
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/stable/earnings-calendar?"
        start_date = query.start_date or datetime.now().date()
        end_date = query.end_date or datetime.now().date() + timedelta(days=7)

        # Create 7-day chunks between start_date and end_date
        urls: list = []
        current_start = start_date

        while current_start <= end_date:
            chunk_end = min(current_start + timedelta(days=7), end_date)
            url = f"{base_url}from={current_start}&to={chunk_end}&apikey={api_key}"
            urls.append(url)
            current_start = chunk_end + timedelta(days=1)

        # Get data from all URLs
        all_data: list = await amake_requests(
            urls, response_callback=response_callback, **kwargs
        )

        return all_data

    @staticmethod
    def transform_data(
        query: FMPCalendarEarningsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCalendarEarningsData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["date"], reverse=True)
        return [FMPCalendarEarningsData.model_validate(d) for d in data]

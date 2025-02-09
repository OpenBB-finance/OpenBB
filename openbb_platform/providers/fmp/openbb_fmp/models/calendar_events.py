"""FMP Company Events Calendar Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_events import (
    CalendarEventsData,
    CalendarEventsQueryParams,
)
from pydantic import Field


class FmpCalendarEventsQueryParams(CalendarEventsQueryParams):
    """FMP Company Events Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-confirmed-api
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}


class FmpCalendarEventsData(CalendarEventsData):
    """FMP Company Events Calendar Data."""

    __alias_dict__ = {
        "announcement_date": "publicationDate",
        "timing": "when",
        "description": "title",
    }

    exchange: Optional[str] = Field(
        default=None,
        description="Exchange where the symbol is listed.",
    )
    time: Optional[str] = Field(
        default=None,
        description="The estimated time of the event, local to the exchange.",
    )
    timing: Optional[str] = Field(
        default=None,
        description="The timing of the event - e.g. before, during, or after market hours.",
    )
    description: Optional[str] = Field(
        default=None,
        description="The title of the event.",
    )
    url: Optional[str] = Field(
        default=None,
        description="The URL to the press release for the announcement.",
    )
    announcement_date: Optional[dateType] = Field(
        default=None,
        description="The date when the event was announced.",
    )


class FMPCalendarEventsFetcher(
    Fetcher[FmpCalendarEventsQueryParams, list[FmpCalendarEventsData]]
):
    """FMP Company Events Calendar Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FmpCalendarEventsQueryParams:
        """Transform query parameters."""
        return FmpCalendarEventsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FmpCalendarEventsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract data from the API."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from datetime import timedelta
        from openbb_core.provider.utils.errors import EmptyDataError, OpenBBError
        from openbb_fmp.utils.helpers import get_data
        from pandas import date_range, to_datetime

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = (
            "https://financialmodelingprep.com/api/v4/earning-calendar-confirmed?"
        )

        start_date = to_datetime(
            query.start_date if query.start_date else dateType.today()
        )
        end_date = to_datetime(
            query.end_date if query.end_date else (dateType.today() + timedelta(days=3))
        )

        # Assuming limit of 1000 events per request, and peak earnings season
        # with 200+ events per day, in America alone, we split into 3-day ranges.
        # We don't actually know what the API limitations are, so this is a conservative guess.
        date_ranges = date_range(start=start_date, end=end_date, freq="3D")
        if end_date not in date_ranges:
            date_ranges = date_ranges.append(to_datetime([end_date]))

        urls: list = []
        results: list = []

        for i in range(len(date_ranges) - 1):
            from_date = date_ranges[i].strftime("%Y-%m-%d")
            to_date = date_ranges[i + 1].strftime("%Y-%m-%d")
            urls.append(
                f"{base_url}from={from_date}&to={to_date}&limit=1000&apikey={api_key}"
            )

        async def get_one(url):
            """Get data from one URL."""
            try:
                response = await get_data(url, **kwargs)
            except OpenBBError as e:
                raise e from e

            if response:
                results.extend(response)

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return sorted(results, key=lambda x: x["date"])

    @staticmethod
    def transform_data(
        query: FmpCalendarEventsQueryParams, data: list, **kwargs: Any
    ) -> list[FmpCalendarEventsData]:
        """Transform the data."""
        return [FmpCalendarEventsData.model_validate(d) for d in data]

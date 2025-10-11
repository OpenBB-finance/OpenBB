"""FMP Calendar Splits Model."""

# pylint: disable=unused-argument

from datetime import datetime, timedelta
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_splits import (
    CalendarSplitsData,
    CalendarSplitsQueryParams,
)


class FMPCalendarSplitsQueryParams(CalendarSplitsQueryParams):
    """FMP Calendar Splits Query.

    Source: https://site.financialmodelingprep.com/developer/docs#splits-calendar
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}


class FMPCalendarSplitsData(CalendarSplitsData):
    """FMP Calendar Splits Data."""


class FMPCalendarSplitsFetcher(
    Fetcher[
        FMPCalendarSplitsQueryParams,
        list[FMPCalendarSplitsData],
    ]
):
    """FMP Calendar Splits Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCalendarSplitsQueryParams:
        """Transform the query params. Start and end dates are set to a 1 year interval."""
        return FMPCalendarSplitsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCalendarSplitsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_requests  # noqa
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/stable/splits-calendar?"
        start_date = query.start_date or datetime.now().date() - timedelta(days=7)
        end_date = query.end_date or datetime.now().date() + timedelta(days=14)

        # Create 90-day chunks between start_date and end_date
        urls: list = []
        current_start = start_date

        while current_start <= end_date:
            chunk_end = min(current_start + timedelta(days=89), end_date)
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
        query: FMPCalendarSplitsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCalendarSplitsData]:
        """Return the transformed data."""
        return [FMPCalendarSplitsData.model_validate(d) for d in data]

"""Nasdaq Dividend Calendar Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_dividend import (
    CalendarDividendData,
    CalendarDividendQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class NasdaqCalendarDividendQueryParams(CalendarDividendQueryParams):
    """Nasdaq Dividend Calendar Query.

    Source: https://www.nasdaq.com/market-activity/dividends
    """


class NasdaqCalendarDividendData(CalendarDividendData):
    """Nasdaq Dividend Calendar Data."""

    __alias_dict__ = {
        "name": "companyName",
        "ex_dividend_date": "dividend_Ex_Date",
        "payment_date": "payment_Date",
        "record_date": "record_Date",
        "declaration_date": "announcement_Date",
        "amount": "dividend_Rate",
        "annualized_amount": "indicated_Annual_Dividend",
    }

    annualized_amount: Optional[float] = Field(
        default=None,
        description="The indicated annualized dividend amount.",
    )

    @field_validator(
        "ex_dividend_date",
        "record_date",
        "payment_date",
        "declaration_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_date(cls, v: str):
        """Validate the date."""
        v = v.replace("N/A", "")
        return datetime.strptime(v, "%m/%d/%Y").date() if v else None


class NasdaqCalendarDividendFetcher(
    Fetcher[
        NasdaqCalendarDividendQueryParams,
        List[NasdaqCalendarDividendData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqCalendarDividendQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return NasdaqCalendarDividendQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: NasdaqCalendarDividendQueryParams,
        credentials: Optional[Dict[str, str]],  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Nasdaq endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_nasdaq.utils.helpers import get_headers, date_range  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa

        IPO_HEADERS = get_headers(accept_type="json")
        data: List[Dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]

        async def get_calendar_data(date: str) -> None:
            """Get the calendar data."""
            response: List = []
            url = f"https://api.nasdaq.com/api/calendar/dividends?date={date}"
            r_json = await amake_request(url=url, headers=IPO_HEADERS, timeout=5)
            if (
                "data" in r_json  # type: ignore
                and "calendar" in r_json["data"]  # type: ignore
                and "rows" in r_json["data"]["calendar"]  # type: ignore
            ):
                response = r_json["data"]["calendar"]["rows"]  # type: ignore
            if response:
                data.extend(response)

        await asyncio.gather(*[get_calendar_data(date) for date in dates])

        return data

    @staticmethod
    def transform_data(
        query: NasdaqCalendarDividendQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqCalendarDividendData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return [
            NasdaqCalendarDividendData.model_validate(d)
            for d in sorted(data, key=lambda x: x["dividend_Ex_Date"], reverse=True)
        ]

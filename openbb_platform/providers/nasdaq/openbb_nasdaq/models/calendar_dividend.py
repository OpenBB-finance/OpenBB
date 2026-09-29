"""Nasdaq Dividend Calendar Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_dividend import (
    CalendarDividendData,
    CalendarDividendQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL


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

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    annualized_amount: float | None = Field(
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
        list[NasdaqCalendarDividendData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqCalendarDividendQueryParams:
        """Transform the query params."""
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
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio

        from openbb_nasdaq.utils.helpers import date_range, get_nasdaq_data

        data: list[dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]

        async def get_calendar_data(date: str) -> None:
            """Get the calendar data."""
            response: list = []
            payload = await get_nasdaq_data(
                f"calendar/dividends?date={date}", timeout=5
            )
            calendar = (payload or {}).get("calendar") or {}

            if calendar.get("rows"):
                response = calendar["rows"]
            if response:
                data.extend(response)

        await asyncio.gather(*[get_calendar_data(date) for date in dates])

        return data

    @staticmethod
    def transform_data(
        query: NasdaqCalendarDividendQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NasdaqCalendarDividendData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return [
            NasdaqCalendarDividendData.model_validate(d)
            for d in sorted(data, key=lambda x: x["dividend_Ex_Date"], reverse=True)
        ]

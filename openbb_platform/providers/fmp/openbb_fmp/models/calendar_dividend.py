"""FMP Dividend Calendar Model."""

# pylint: disable=unused-argument

from datetime import datetime, timedelta
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_dividend import (
    CalendarDividendData,
    CalendarDividendQueryParams,
)
from pydantic import Field, field_validator


class FMPCalendarDividendQueryParams(CalendarDividendQueryParams):
    """FMP Dividend Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/dividend-calendar-api/

    The maximum time interval between the start and end date can be 3 months.
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}


class FMPCalendarDividendData(CalendarDividendData):
    """FMP Dividend Calendar Data."""

    __alias_dict__ = {
        "amount": "dividend",
        "ex_dividend_date": "date",
        "record_date": "recordDate",
        "payment_date": "paymentDate",
        "declaration_date": "declarationDate",
        "adjusted_amount": "adjDividend",
        "dividend_yield": "yield",
    }

    adjusted_amount: float | None = Field(
        default=None,
        description="The adjusted-dividend amount.",
    )
    dividend_yield: float | None = Field(
        default=None,
        description="Annualized dividend yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    frequency: str | None = Field(
        default=None,
        description="Frequency of the regular dividend payment.",
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
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @field_validator("dividend_yield", mode="before", check_fields=False)
    @classmethod
    def dividend_yield_validate(cls, v):
        """Return the dividend yield as a float."""
        return v / 100 if v else None


class FMPCalendarDividendFetcher(
    Fetcher[
        FMPCalendarDividendQueryParams,
        list[FMPCalendarDividendData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCalendarDividendQueryParams:
        """Transform the query params."""
        return FMPCalendarDividendQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCalendarDividendQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_requests  # noqa
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/stable/dividends-calendar?"
        start_date = query.start_date or datetime.now().date()
        end_date = query.end_date or datetime.now().date() + timedelta(days=14)

        # Create 14-day chunks between start_date and end_date
        urls: list = []
        current_start = start_date

        while current_start <= end_date:
            chunk_end = min(current_start + timedelta(days=14), end_date)
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
        query: FMPCalendarDividendQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCalendarDividendData]:
        """Return the transformed data."""
        return [
            FMPCalendarDividendData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"])
        ]

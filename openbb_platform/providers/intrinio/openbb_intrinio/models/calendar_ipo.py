"""Intrinio IPO Calendar Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_ipo import (
    CalendarIpoData,
    CalendarIpoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_one
from openbb_intrinio.utils.references import IntrinioCompany, IntrinioSecurity
from pydantic import Field


class IntrinioCalendarIpoQueryParams(CalendarIpoQueryParams):
    """Intrinio IPO Calendar Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_ipos_v2
    """

    __alias_dict__ = {
        "symbol": "ticker",
        "limit": "page_size",
        "min_value": "offer_amount_greater_than",
        "max_value": "offer_amount_less_than",
    }

    status: Literal["upcoming", "priced", "withdrawn"] | None = Field(
        description="Status of the IPO. [upcoming, priced, or withdrawn]", default=None
    )
    min_value: int | None = Field(
        description="Return IPOs with an offer dollar amount greater than the given amount.",
        default=None,
    )
    max_value: int | None = Field(
        description="Return IPOs with an offer dollar amount less than the given amount.",
        default=None,
    )


class IntrinioCalendarIpoData(CalendarIpoData):
    """Intrinio IPO Calendar Data."""

    __alias_dict__ = {"symbol": "ticker", "ipo_date": "date"}

    status: Literal["upcoming", "priced", "withdrawn"] | None = Field(
        description=(
            "The status of the IPO. Upcoming IPOs have not taken place yet but are expected to. "
            "Priced IPOs have taken place. Withdrawn IPOs were expected to take place, but were subsequently withdrawn."
        ),
        default=None,
    )
    exchange: str | None = Field(
        description=(
            "The acronym of the stock exchange that the company is going to trade publicly on. Typically NYSE or NASDAQ."
        ),
        default=None,
    )
    offer_amount: float | None = Field(
        description="The total dollar amount of shares offered in the IPO. Typically this is share price * share count",
        default=None,
    )
    share_price: float | None = Field(
        description="The price per share at which the IPO was offered.", default=None
    )
    share_price_lowest: float | None = Field(
        description=(
            "The expected lowest price per share at which the IPO will be offered. "
            "Before an IPO is priced, companies typically provide a range of prices per share at which "
            "they expect to offer the IPO (typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_price_highest: float | None = Field(
        description=(
            "The expected highest price per share at which the IPO will be offered. "
            "Before an IPO is priced, companies typically provide a range of prices per share at which "
            "they expect to offer the IPO (typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_count: int | None = Field(
        description="The number of shares offered in the IPO.", default=None
    )
    share_count_lowest: int | None = Field(
        description=(
            "The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced, "
            "companies typically provide a range of shares that they expect to offer in the IPO "
            "(typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_count_highest: int | None = Field(
        description=(
            "The expected highest number of shares that will be offered in the IPO. Before an IPO is priced, "
            "companies typically provide a range of shares that they expect to offer in the IPO "
            "(typically available for upcoming IPOs)."
        ),
        default=None,
    )
    announcement_url: str | None = Field(
        description="The URL to the company's announcement of the IPO", default=None
    )
    sec_report_url: str | None = Field(
        description=(
            "The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing, which is required to be filed "
            "before an IPO takes place."
        ),
        default=None,
    )
    open_price: float | None = Field(
        description="The opening price at the beginning of the first trading day (only available for priced IPOs).",
        default=None,
    )
    close_price: float | None = Field(
        description="The closing price at the end of the first trading day (only available for priced IPOs).",
        default=None,
    )
    volume: int | None = Field(
        description="The volume at the end of the first trading day (only available for priced IPOs).",
        default=None,
    )
    day_change: float | None = Field(
        description=(
            "The percentage change between the open price and the close price on the first trading day "
            "(only available for priced IPOs)."
        ),
        default=None,
    )
    week_change: float | None = Field(
        description=(
            "The percentage change between the open price on the first trading day and the close price approximately "
            "a week after the first trading day (only available for priced IPOs)."
        ),
        default=None,
    )
    month_change: float | None = Field(
        description=(
            "The percentage change between the open price on the first trading day and the close price approximately "
            "a month after the first trading day (only available for priced IPOs)."
        ),
        default=None,
    )
    id: str | None = Field(description="The Intrinio ID of the IPO.", default=None)
    company: IntrinioCompany | None = Field(
        description="The company that is going public via the IPO.", default=None
    )
    security: IntrinioSecurity | None = Field(
        description="The primary Security for the Company that is going public via the IPO",
        default=None,
    )


class IntrinioCalendarIpoFetcher(
    Fetcher[IntrinioCalendarIpoQueryParams, list[IntrinioCalendarIpoData]]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> IntrinioCalendarIpoQueryParams:
        """Transform the query params."""
        return IntrinioCalendarIpoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCalendarIpoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies/ipos"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&api_key={api_key}"

        data = await get_data_one(url, **kwargs)

        return data.get("initial_public_offerings", [])

    @staticmethod
    def transform_data(
        query: IntrinioCalendarIpoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[IntrinioCalendarIpoData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return [IntrinioCalendarIpoData.model_validate(d) for d in data]

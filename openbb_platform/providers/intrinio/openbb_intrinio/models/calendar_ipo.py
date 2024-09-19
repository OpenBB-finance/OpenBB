"""Intrinio IPO Calendar Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

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

    status: Optional[Literal["upcoming", "priced", "withdrawn"]] = Field(
        description="Status of the IPO. [upcoming, priced, or withdrawn]", default=None
    )
    min_value: Optional[int] = Field(
        description="Return IPOs with an offer dollar amount greater than the given amount.",
        default=None,
    )
    max_value: Optional[int] = Field(
        description="Return IPOs with an offer dollar amount less than the given amount.",
        default=None,
    )


class IntrinioCalendarIpoData(CalendarIpoData):
    """Intrinio IPO Calendar Data."""

    __alias_dict__ = {"symbol": "ticker", "ipo_date": "date"}

    status: Optional[Literal["upcoming", "priced", "withdrawn"]] = Field(
        description=(
            "The status of the IPO. Upcoming IPOs have not taken place yet but are expected to. "
            "Priced IPOs have taken place. Withdrawn IPOs were expected to take place, but were subsequently withdrawn."
        ),
        default=None,
    )
    exchange: Optional[str] = Field(
        description=(
            "The acronym of the stock exchange that the company is going to trade publicly on. "
            "Typically NYSE or NASDAQ."
        ),
        default=None,
    )
    offer_amount: Optional[float] = Field(
        description="The total dollar amount of shares offered in the IPO. Typically this is share price * share count",
        default=None,
    )
    share_price: Optional[float] = Field(
        description="The price per share at which the IPO was offered.", default=None
    )
    share_price_lowest: Optional[float] = Field(
        description=(
            "The expected lowest price per share at which the IPO will be offered. "
            "Before an IPO is priced, companies typically provide a range of prices per share at which "
            "they expect to offer the IPO (typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_price_highest: Optional[float] = Field(
        description=(
            "The expected highest price per share at which the IPO will be offered. "
            "Before an IPO is priced, companies typically provide a range of prices per share at which "
            "they expect to offer the IPO (typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_count: Optional[int] = Field(
        description="The number of shares offered in the IPO.", default=None
    )
    share_count_lowest: Optional[int] = Field(
        description=(
            "The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced, "
            "companies typically provide a range of shares that they expect to offer in the IPO "
            "(typically available for upcoming IPOs)."
        ),
        default=None,
    )
    share_count_highest: Optional[int] = Field(
        description=(
            "The expected highest number of shares that will be offered in the IPO. Before an IPO is priced, "
            "companies typically provide a range of shares that they expect to offer in the IPO "
            "(typically available for upcoming IPOs)."
        ),
        default=None,
    )
    announcement_url: Optional[str] = Field(
        description="The URL to the company's announcement of the IPO", default=None
    )
    sec_report_url: Optional[str] = Field(
        description=(
            "The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing, which is required to be filed "
            "before an IPO takes place."
        ),
        default=None,
    )
    open_price: Optional[float] = Field(
        description="The opening price at the beginning of the first trading day (only available for priced IPOs).",
        default=None,
    )
    close_price: Optional[float] = Field(
        description="The closing price at the end of the first trading day (only available for priced IPOs).",
        default=None,
    )
    volume: Optional[int] = Field(
        description="The volume at the end of the first trading day (only available for priced IPOs).",
        default=None,
    )
    day_change: Optional[float] = Field(
        description=(
            "The percentage change between the open price and the close price on the first trading day "
            "(only available for priced IPOs)."
        ),
        default=None,
    )
    week_change: Optional[float] = Field(
        description=(
            "The percentage change between the open price on the first trading day and the close price approximately "
            "a week after the first trading day (only available for priced IPOs)."
        ),
        default=None,
    )
    month_change: Optional[float] = Field(
        description=(
            "The percentage change between the open price on the first trading day and the close price approximately "
            "a month after the first trading day (only available for priced IPOs)."
        ),
        default=None,
    )
    id: Optional[str] = Field(description="The Intrinio ID of the IPO.", default=None)
    company: Optional[IntrinioCompany] = Field(
        description="The company that is going public via the IPO.", default=None
    )
    security: Optional[IntrinioSecurity] = Field(
        description="The primary Security for the Company that is going public via the IPO",
        default=None,
    )


class IntrinioCalendarIpoFetcher(
    Fetcher[IntrinioCalendarIpoQueryParams, List[IntrinioCalendarIpoData]]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCalendarIpoQueryParams:
        """Transform the query params."""
        return IntrinioCalendarIpoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCalendarIpoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies/ipos"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&api_key={api_key}"

        data = await get_data_one(url, **kwargs)

        return data.get("initial_public_offerings", [])

    @staticmethod
    def transform_data(
        query: IntrinioCalendarIpoQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCalendarIpoData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return [IntrinioCalendarIpoData.model_validate(d) for d in data]

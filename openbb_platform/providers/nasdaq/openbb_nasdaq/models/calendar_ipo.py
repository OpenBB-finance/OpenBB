"""Nasdaq IPO Calendar Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_ipo import (
    CalendarIpoData,
    CalendarIpoQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL

STATUS_DATES = {
    "priced": "ipo_date",
    "filed": "filed_date",
    "withdrawn": "withdraw_date",
    "upcoming": "expected_price_date",
}


class NasdaqCalendarIpoQueryParams(CalendarIpoQueryParams):
    """Nasdaq IPO Calendar Query.

    Source: https://www.nasdaq.com/market-activity/ipos
    """

    status: Literal["upcoming", "priced", "filed", "withdrawn"] = Field(
        default="priced",
        description="The status of the offering.",
    )
    is_spo: bool = Field(
        default=False,
        description="If True, returns secondary public offerings (SPOs) instead.",
    )


class NasdaqCalendarIpoData(CalendarIpoData):
    """Nasdaq IPO Calendar Data."""

    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    name: str | None = Field(default=None, description="The name of the company.")
    offer_amount: float | None = Field(
        default=None, description="The dollar value of the shares offered."
    )
    share_count: int | None = Field(
        default=None, description="The number of shares offered."
    )
    expected_price_date: dateType | None = Field(
        default=None, description="The date the pricing is expected."
    )
    filed_date: dateType | None = Field(
        default=None, description="The date the offering was filed."
    )
    withdraw_date: dateType | None = Field(
        default=None, description="The date the offering was withdrawn."
    )
    deal_status: str | None = Field(default=None, description="The status of the deal.")


class NasdaqCalendarIpoFetcher(
    Fetcher[
        NasdaqCalendarIpoQueryParams,
        list[NasdaqCalendarIpoData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqCalendarIpoQueryParams:
        """Transform the query, defaulting to the trailing three hundred days."""
        from datetime import datetime, timedelta

        today = datetime.now().date()

        if params.get("start_date") is None:
            params["start_date"] = today - timedelta(days=300)

        if params.get("end_date") is None:
            params["end_date"] = today

        return NasdaqCalendarIpoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqCalendarIpoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio

        from openbb_nasdaq.utils.helpers import date_range, get_nasdaq_data

        months = sorted(
            {
                day.strftime("%Y-%m")
                for day in date_range(query.start_date, query.end_date)
            }
        )
        results: list[dict] = []
        offering = "&type=spo" if query.is_spo else ""

        async def get_one(month: str) -> None:
            """Collect the offerings listed for one month."""
            payload = (
                await get_nasdaq_data(f"ipo/calendar?date={month}{offering}") or {}
            )
            block = payload.get(query.status) or {}
            rows = (
                (block.get("upcomingTable") or {}).get("rows")
                if query.status == "upcoming"
                else block.get("rows")
            )

            if rows:
                results.extend(rows)

        await asyncio.gather(*[get_one(month) for month in months])

        return results

    @staticmethod
    def transform_data(
        query: NasdaqCalendarIpoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqCalendarIpoData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no offering matched the requested status and window.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_date, to_number

        if not data:
            raise EmptyDataError(
                f"No '{query.status}' offerings were found between"
                f" {query.start_date} and {query.end_date}."
            )

        results: list[NasdaqCalendarIpoData] = []

        for row in data:
            share_count = to_number(row.get("sharesOffered"))
            results.append(
                NasdaqCalendarIpoData.model_validate(
                    {
                        "symbol": row.get("proposedTickerSymbol"),
                        "name": row.get("companyName"),
                        "exchange": row.get("proposedExchange"),
                        "id": row.get("dealID"),
                        "ipo_date": to_date(row.get("pricedDate")),
                        "share_price": to_number(row.get("proposedSharePrice")),
                        "share_count": None
                        if share_count is None
                        else int(share_count),
                        "offer_amount": to_number(
                            row.get("dollarValueOfSharesOffered")
                        ),
                        "expected_price_date": to_date(row.get("expectedPriceDate")),
                        "filed_date": to_date(row.get("filedDate")),
                        "withdraw_date": to_date(row.get("withdrawDate")),
                        "deal_status": row.get("dealStatus"),
                    }
                )
            )

        field = STATUS_DATES[query.status]

        return sorted(results, key=lambda r: getattr(r, field) or dateType.min)

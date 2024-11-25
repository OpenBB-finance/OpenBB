"""Seeking Alpha Calendar Earnings Model."""

# pylint: disable=unused-argument

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from openbb_seeking_alpha.utils.helpers import HEADERS, date_range
from pydantic import Field, field_validator


class SACalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """Seeking Alpha Calendar Earnings Query.

    Source: https://seekingalpha.com/earnings/earnings-calendar
    """

    country: Literal["us", "ca"] = Field(
        default="us",
        description="The country to get calendar data for.",
        json_schema_extra={"choices": ["us", "ca"]},
    )


class SACalendarEarningsData(CalendarEarningsData):
    """Seeking Alpha Calendar Earnings Data."""

    market_cap: Optional[float] = Field(
        default=None,
        description="Market cap of the entity.",
    )
    reporting_time: Optional[str] = Field(
        default=None,
        description="The reporting time - e.g. after market close.",
    )
    exchange: Optional[str] = Field(
        default=None,
        description="The primary trading exchange.",
    )
    sector_id: Optional[int] = Field(
        default=None,
        description="The Seeking Alpha Sector ID.",
    )

    @field_validator("report_date", mode="before", check_fields=False)
    @classmethod
    def validate_release_date(cls, v):
        """Validate the release date."""
        v = v.split("T")[0]
        return datetime.strptime(v, "%Y-%m-%d").date()


class SACalendarEarningsFetcher(
    Fetcher[
        SACalendarEarningsQueryParams,
        List[SACalendarEarningsData],
    ]
):
    """Seeking Alpha Calendar Earnings Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SACalendarEarningsQueryParams:
        """Transform the query."""
        now = datetime.today().date()
        transformed_params = params
        if not params.get("start_date"):
            transformed_params["start_date"] = now
        if not params.get("end_date"):
            transformed_params["end_date"] = now + timedelta(days=3)
        return SACalendarEarningsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: SACalendarEarningsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Seeking Alpha endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.client import ClientSession
        from openbb_core.provider.utils.helpers import amake_request

        results: List[Dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]
        currency = "USD" if query.country == "us" else "CAD"
        messages: List = []

        async with ClientSession() as session:

            async def get_date(date, currency):
                """Get date for one date."""
                url = (
                    f"https://seekingalpha.com/api/v3/earnings_calendar/tickers?"
                    f"filter%5Bselected_date%5D={date}"
                    f"&filter%5Bwith_rating%5D=false&filter%5Bcurrency%5D={currency}"
                )
                response = await amake_request(
                    url=url, headers=HEADERS, session=session
                )
                # Try again if the response is blocked.
                if "blockScript" in response:
                    response = await amake_request(
                        url=url, headers=HEADERS, session=session
                    )
                    if "blockScript" in response:
                        message = json.dumps(response)
                        messages.append(message)
                        warn(message)
                if "data" in response:
                    results.extend(response.get("data"))  # type: ignore

            await asyncio.gather(*[get_date(date, currency) for date in dates])

        if not results:
            raise OpenBBError(f"Error with the Seeking Alpha request -> {messages}")

        return results

    @staticmethod
    def transform_data(
        query: SACalendarEarningsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[SACalendarEarningsData]:
        """Transform the data to the standard format."""
        transformed_data: List[SACalendarEarningsData] = []
        for row in sorted(data, key=lambda x: x["attributes"]["release_date"]):
            attributes = row.get("attributes", {})
            transformed_data.append(
                SACalendarEarningsData.model_validate(
                    {
                        "report_date": attributes.get("release_date"),
                        "reporting_time": attributes.get("release_time"),
                        "symbol": attributes.get("slug"),
                        "name": attributes.get("name"),
                        "market_cap": attributes.get("marketcap"),
                        "exchange": attributes.get("exchange"),
                        "sector_id": attributes.get("sector_id"),
                    }
                )
            )
        return transformed_data

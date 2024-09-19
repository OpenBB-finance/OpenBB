"""Nasdaq IPO Calendar Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_ipo import (
    CalendarIpoData,
    CalendarIpoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class NasdaqCalendarIpoQueryParams(CalendarIpoQueryParams):
    """Nasdaq IPO Calendar Query.

    Source: https://www.nasdaq.com/market-activity/ipos
    """

    status: Literal["upcoming", "priced", "filed", "withdrawn"] = Field(
        default="priced",
        description="The status of the IPO.",
    )
    is_spo: bool = Field(
        default=False,
        description="If True, returns data for secondary public offerings (SPOs).",
    )


class NasdaqCalendarIpoData(CalendarIpoData):
    """Nasdaq IPO Calendar Data."""

    __alias_dict__ = {
        "symbol": "proposedTickerSymbol",
        "ipo_date": "pricedDate",
        "share_price": "proposedSharePrice",
        "exchange": "proposedExchange",
        "id": "dealID",
        "name": "companyName",
        "offer_amount": "dollarValueOfSharesOffered",
        "share_count": "sharesOffered",
        "expected_price_date": "expectedPriceDate",
        "filed_date": "filedDate",
        "withdraw_date": "withdrawDate",
        "deal_status": "dealStatus",
    }

    name: Optional[str] = Field(
        default=None,
        description="The name of the company.",
    )
    offer_amount: Optional[float] = Field(
        default=None,
        description="The dollar value of the shares offered.",
    )
    share_count: Optional[int] = Field(
        default=None,
        description="The number of shares offered.",
    )
    expected_price_date: Optional[dateType] = Field(
        default=None,
        description="The date the pricing is expected.",
    )
    filed_date: Optional[dateType] = Field(
        default=None,
        description="The date the IPO was filed.",
    )
    withdraw_date: Optional[dateType] = Field(
        default=None,
        description="The date the IPO was withdrawn.",
    )
    deal_status: Optional[str] = Field(
        default=None,
        description="The status of the deal.",
    )

    @field_validator(
        "filed_date",
        "withdraw_date",
        "expected_price_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_date(cls, v):
        """Validate the date if available is a date object."""
        v = v.replace("N/A", "")
        return datetime.strptime(v, "%m/%d/%Y").date() if v else None

    @field_validator(
        "offer_amount",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_offer_amount(cls, v):
        """Validate the offer amount if available is a float."""
        return float(str(v).replace("$", "").replace(",", "")) if v else None

    @field_validator(
        "share_count",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_share_count(cls, v):
        """Validate the share count if available is an int."""
        return int(str(v).replace(",", "")) if v else None


class NasdaqCalendarIpoFetcher(
    Fetcher[
        NasdaqCalendarIpoQueryParams,
        List[NasdaqCalendarIpoData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqCalendarIpoQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        now = datetime.today().date().strftime("%Y-%m-%d")
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = datetime.strptime(
                now, "%Y-%m-%d"
            ) - timedelta(days=300)
        if params.get("end_date") is None:
            transformed_params["end_date"] = datetime.strptime(now, "%Y-%m-%d")

        return NasdaqCalendarIpoQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: NasdaqCalendarIpoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Nasdaq endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_nasdaq.utils.helpers import get_headers, date_range  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa

        IPO_HEADERS = get_headers(accept_type="json")

        data = []
        dates = sorted(
            list(
                set(
                    date.strftime("%Y-%m")
                    for date in date_range(query.start_date, query.end_date)
                )
            )
        )

        async def get_calendar_data(date: str):
            """Get the calendar data for the given date."""
            response: List = []
            url = (
                f"https://api.nasdaq.com/api/ipo/calendar?date={date}"
                if query.is_spo is False
                else f"https://api.nasdaq.com/api/ipo/calendar?type=spo&date={date}"
            )
            r_json = await amake_request(url, headers=IPO_HEADERS)
            r_json = r_json.get("data", {})  # type: ignore
            if query.status in r_json:
                response = (
                    r_json["upcoming"]["upcomingTable"]["rows"]  # type: ignore
                    if query.status == "upcoming"
                    else r_json[query.status]["rows"]  # type: ignore
                )
            if response:
                data.extend(response)

        await asyncio.gather(*[get_calendar_data(date) for date in dates])

        return data

    @staticmethod
    def transform_data(
        query: NasdaqCalendarIpoQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqCalendarIpoData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        if query.status == "priced":
            data = [
                {
                    **d,
                    "pricedDate": datetime.strptime(
                        d["pricedDate"], "%m/%d/%Y"
                    ).strftime("%Y-%m-%d"),
                }
                for d in data
            ]
            data = sorted(data, key=lambda x: x["pricedDate"])

        if query.status == "withdrawn":
            data = sorted(
                data, key=lambda x: datetime.strptime(x["withdrawDate"], "%m/%d/%Y")
            )

        if query.status == "filed":
            data = sorted(
                data, key=lambda x: datetime.strptime(x["filedDate"], "%m/%d/%Y")
            )

        return [NasdaqCalendarIpoData.model_validate(d) for d in data]

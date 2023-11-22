"""Nasdaq IPO Calendar Model."""

from concurrent.futures import ThreadPoolExecutor
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Literal, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_ipo import (
    CalendarIpoData,
    CalendarIpoQueryParams,
)
from openbb_nasdaq.utils.helpers import IPO_HEADERS, date_range
from pydantic import Field, field_validator


class NasdaqCalendarIpoQueryParams(CalendarIpoQueryParams):
    """Nasdaq IPO Calendar Query.

    Source: https://www.nasdaq.com/market-activity/ipos
    """

    status: Optional[Literal["upcoming", "priced", "filed", "withdrawn"]] = Field(
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
    }

    name: Optional[str] = Field(
        default=None,
        description="The name of the company.",
        alias="companyName",
    )
    offer_amount: Optional[float] = Field(
        default=None,
        description="The dollar value of the shares offered.",
        alias="dollarValueOfSharesOffered",
    )
    share_count: Optional[int] = Field(
        default=None,
        description="The number of shares offered.",
        alias="sharesOffered",
    )
    expected_price_date: Optional[dateType] = Field(
        default=None,
        description="The date the pricing is expected.",
        alias="expectedPriceDate",
    )
    filed_date: Optional[dateType] = Field(
        default=None, description="The date the IPO was filed.", alias="filedDate"
    )
    withdraw_date: Optional[dateType] = Field(
        default=None,
        description="The date the IPO was withdrawn.",
        alias="withdrawDate",
    )
    deal_status: Optional[str] = Field(
        default=None, description="The status of the deal.", alias="dealStatus"
    )

    @field_validator(
        "filed_date",
        "withdraw_date",
        "expected_price_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_date(cls, v: str):
        v = v.replace("N/A", "")
        return datetime.strptime(v, "%m/%d/%Y").date() if v else None

    @field_validator(
        "offer_amount",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_offer_amount(cls, v: str):
        return float(str(v).replace("$", "").replace(",", "")) if v else None

    @field_validator(
        "share_count",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_share_count(cls, v: str):
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
    def extract_data(
        query: NasdaqCalendarIpoQueryParams,
        credentials: Optional[Dict[str, str]],  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Nasdaq endpoint."""

        data = []
        dates = sorted(
            list(
                set(
                    [
                        date.strftime("%Y-%m")
                        for date in date_range(query.start_date, query.end_date)
                    ]
                )
            )
        )

        def get_calendar_data(date: str) -> None:
            response: List[Dict[Any, Any]] = [{}]
            url = (
                f"https://api.nasdaq.com/api/ipo/calendar?date={date}"
                if query.is_spo is False
                else f"https://api.nasdaq.com/api/ipo/calendar?type=spo&date={date}"
            )
            r = requests.get(url, headers=IPO_HEADERS, timeout=5)
            r_json = r.json()["data"] if "data" in r.json() else {}
            if query.status in r_json:
                response = (
                    r_json["upcoming"]["upcomingTable"]["rows"]
                    if query.status == "upcoming"
                    else r_json[query.status]["rows"]
                )
            if response is not None:
                data.extend(response)

        with ThreadPoolExecutor() as executor:
            executor.map(get_calendar_data, dates)

        return data

    @staticmethod
    def transform_data(
        query: NasdaqCalendarIpoQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> List[NasdaqCalendarIpoData]:
        """Return the transformed data."""
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

"""Nasdaq Dividend Calendar Model."""

# pylint: disable=unused-argument
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_dividend import (
    CalendarDividendData,
    CalendarDividendQueryParams,
)
from openbb_nasdaq.utils.helpers import IPO_HEADERS, date_range
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
    }

    annualized_amount: Optional[float] = Field(
        default=None,
        description="The indicated annualized dividend amount.",
        alias="indicated_Annual_Dividend",
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
        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return NasdaqCalendarDividendQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: NasdaqCalendarDividendQueryParams,
        credentials: Optional[Dict[str, str]],  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Nasdaq endpoint."""
        data: List[Dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]

        def get_calendar_data(date: str) -> None:
            response = []
            url = f"https://api.nasdaq.com/api/calendar/dividends?date={date}"
            r = requests.get(url, headers=IPO_HEADERS, timeout=5)
            r_json = r.json()
            if (
                "data" in r_json
                and "calendar" in r_json["data"]
                and "rows" in r_json["data"]["calendar"]
            ):
                response = r_json["data"]["calendar"]["rows"]
            if len(response) > 0:
                data.extend(response)

        with ThreadPoolExecutor() as executor:
            executor.map(get_calendar_data, dates)

        return data

    @staticmethod
    def transform_data(
        query: NasdaqCalendarDividendQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> List[NasdaqCalendarDividendData]:
        """Return the transformed data."""
        return [
            NasdaqCalendarDividendData.model_validate(d)
            for d in sorted(data, key=lambda x: x["dividend_Ex_Date"], reverse=True)
        ]

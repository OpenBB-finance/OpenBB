"""Nasdaq Earnings Calendar Model."""

# pylint: disable=unused-argument

from concurrent.futures import ThreadPoolExecutor
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from openbb_nasdaq.utils.helpers import IPO_HEADERS, date_range
from pydantic import Field, field_validator


class NasdaqCalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """Nasdaq Earnings Calendar Query.

    Source: https://www.nasdaq.com/market-activity/earnings
    """


class NasdaqCalendarEarningsData(CalendarEarningsData):
    """Nasdaq Earnings Calendar Data."""

    __alias_dict__ = {
        "report_date": "date",
        "eps_previous": "lastYearEPS",
        "eps_consensus": "epsForecast",
    }
    eps_actual: Optional[float] = Field(
        default=None,
        description="The actual earnings per share (USD) announced.",
        alias="eps",
    )
    surprise_percent: Optional[float] = Field(
        default=None,
        description="The earnings surprise as normalized percentage points.",
        alias="surprise",
    )
    num_estimates: Optional[int] = Field(
        default=None,
        description="The number of analysts providing estimates for the consensus.",
        alias="noOfEsts",
    )
    period_ending: Optional[str] = Field(
        default=None,
        description="The fiscal period end date.",
        alias="fiscalQuarterEnding",
    )
    previous_report_date: Optional[dateType] = Field(
        default=None,
        description="The previous report date for the same period last year.",
        alias="lastYearRptDt",
    )
    reporting_time: Optional[str] = Field(
        default=None,
        description="The reporting time - e.g. after market close.",
        alias="time",
    )
    market_cap: Optional[int] = Field(
        default=None,
        description="The market cap (USD) of the reporting entity.",
        alias="marketCap",
    )

    @field_validator(
        "period_ending",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_period_ending(cls, v: str):
        """Validate the date if available meets the %Y-%m convention."""
        v = v.replace("N/A", "")
        return datetime.strptime(v, "%b/%Y").strftime("%Y-%m") if v else None

    @field_validator("previous_report_date", mode="before", check_fields=False)
    @classmethod
    def validate_previous_report_date(cls, v: str):
        """Validate the date is a date object if available."""
        v = v.replace("N/A", "")
        return datetime.strptime(v, "%m/%d/%Y").date() if v else None

    @field_validator(
        "reporting_time",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_reporting_time(cls, v: str):
        """Validate the time if available does not contain prefixes."""
        return v.replace("time-", "") if v else None

    @field_validator(
        "market_cap",
        "eps_previous",
        "eps_consensus",
        "num_estimates",
        "eps_actual",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_numbers(cls, v: str):
        """Validate the numbers are floats."""
        v = (
            v.replace("N/A", "")
            .replace("$", "")
            .replace(",", "")
            .replace("(", "-")
            .replace(")", "")
        )
        return float(v) if v else None

    @field_validator(
        "surprise_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_surprise_percent(cls, v: str):
        """Validate the percent are normalized floats."""
        v = v.replace("N/A", "")
        return float(v) * 0.01 if v else None


class NasdaqCalendarEarningsFetcher(
    Fetcher[
        NasdaqCalendarEarningsQueryParams,
        List[NasdaqCalendarEarningsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqCalendarEarningsQueryParams:
        """Transform the query params."""
        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return NasdaqCalendarEarningsQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: NasdaqCalendarEarningsQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
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
            url = f"https://api.nasdaq.com/api/calendar/earnings?date={date}"
            r = requests.get(url, headers=IPO_HEADERS, timeout=5)
            r_json = r.json()
            if "data" in r_json and "rows" in r_json["data"]:
                response = r_json["data"]["rows"]
                _as_of_date = datetime.strptime(
                    r_json["data"]["asOf"], "%a, %b %d, %Y"
                ).date()
                if len(response) > 0:
                    data.extend([{**d, "date": _as_of_date} for d in response])

        with ThreadPoolExecutor() as executor:
            executor.map(get_calendar_data, dates)

        return sorted(data, key=lambda x: x["date"], reverse=True)

    @staticmethod
    def transform_data(
        query: NasdaqCalendarEarningsQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> List[NasdaqCalendarEarningsData]:
        """Return the transformed data."""
        return [NasdaqCalendarEarningsData.model_validate(d) for d in data]

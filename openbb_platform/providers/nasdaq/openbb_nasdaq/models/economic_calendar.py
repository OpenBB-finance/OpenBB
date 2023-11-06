"""Nasdaq Economic Calendar fetcher."""


import html
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from itertools import repeat
from typing import Any, Dict, List, Optional, Set, Union

from openbb_nasdaq.utils.helpers import date_range, get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from pydantic import Field, field_validator


class NasdaqEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Nasdaq Economic Calendar Query.

    Source: https://api.nasdaq.com/api
    """

    country: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Country of the event",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v: Union[str, List[str], Set[str]]):
        """Validate the country input."""
        countries = v.split(",") if isinstance(v, str) else v
        return list(map(lambda v: v.lower(), countries))


class NasdaqEconomicCalendarData(EconomicCalendarData):
    """Nasdaq Economic Calendar Data."""

    __alias_dict__ = {
        "event": "eventName",
    }
    description: Optional[str] = Field(default=None, description="Event description.")

    @field_validator(
        "actual", "previous", "consensus", mode="before", check_fields=False
    )
    @classmethod
    def clean_fields(cls, v: str):
        """Replace non-breaking space HTML entity."""
        return v.replace("&nbsp;", "-")

    @field_validator("description", mode="before", check_fields=False)
    @classmethod
    def clean_html(cls, v: str):
        """Format HTML entities to normal."""
        return html.unescape(v)


class NasdaqEconomicCalendarFetcher(
    Fetcher[
        NasdaqEconomicCalendarQueryParams,
        List[NasdaqEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqEconomicCalendarQueryParams:
        """Transform the query params."""
        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=3)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return NasdaqEconomicCalendarQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: NasdaqEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Quandl endpoint."""
        data: List[Dict] = []

        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]

        def get_calendar_data(date: str, data: List[Dict]) -> None:
            url = f"https://api.nasdaq.com/api/calendar/economicevents?date={date}"
            response = get_data_one(url, **kwargs).get("data", {}).get("rows", [])
            response = [
                {
                    **{k: v for k, v in item.items() if k != "gmt"},
                    "date": f"{date} 00:00"
                    if item.get("gmt") == "All Day"
                    else f"{date} {item.get('gmt', '')}",
                }
                for item in response
            ]
            data.extend(response)

        with ThreadPoolExecutor() as executor:
            executor.map(get_calendar_data, dates, repeat(data))

        if query.country:
            return [d for d in data if d.get("country", "").lower() in query.country]

        return data

    @staticmethod
    def transform_data(
        query: NasdaqEconomicCalendarQueryParams,  # pylint: disable=unused-argument
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> List[NasdaqEconomicCalendarData]:
        """Return the transformed data."""
        return [NasdaqEconomicCalendarData.model_validate(d) for d in data]

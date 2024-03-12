"""Nasdaq Economic Calendar Model."""

import html
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from itertools import repeat
from typing import Any, Dict, List, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_nasdaq.utils.helpers import IPO_HEADERS, date_range, remove_html_tags
from pydantic import Field, field_validator


class NasdaqEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Nasdaq Economic Calendar Query.

    Source: https://www.nasdaq.com/market-activity/economic-calendar
    """

    __json_schema_extra__ = {"country": ["multiple_items_allowed"]}

    country: Optional[str] = Field(
        default=None,
        description="Country of the event",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str):  # pylint: disable=E0213
        """Validate country."""
        return ",".join([v.lower() for v in c.replace(" ", "_").split(",")])


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
        if v:
            v = (
                html.unescape(v)
                .replace("\r\n\r\n", " ")
                .replace("\r\n", " ")
                .replace("''", "'")
            )
            v = remove_html_tags(v)
        return v if v else None


class NasdaqEconomicCalendarFetcher(
    Fetcher[
        NasdaqEconomicCalendarQueryParams,
        List[NasdaqEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

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

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: NasdaqEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Nasdaq endpoint."""
        data: List[Dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
        ]

        def get_calendar_data(date: str, data: List[Dict]) -> None:
            url = f"https://api.nasdaq.com/api/calendar/economicevents?date={date}"
            r = requests.get(url, headers=IPO_HEADERS, timeout=5)
            r_json = r.json()
            if "data" in r_json and "rows" in r_json["data"]:
                response = r_json["data"]["rows"]
            response = [
                {
                    **{k: v for k, v in item.items() if k != "gmt"},
                    "date": (
                        f"{date} 00:00"
                        if item.get("gmt") == "All Day"
                        else f"{date} {item.get('gmt', '')}".replace(
                            "Tentative", "00:00"
                        ).replace("24H", "00:00")
                    ),
                }
                for item in response
            ]
            data.extend(response)

        with ThreadPoolExecutor() as executor:
            executor.map(get_calendar_data, dates, repeat(data))

        if query.country:
            country = (
                query.country.split(",") if "," in query.country else query.country
            )
            country = [country] if isinstance(country, str) else country

            return [
                d
                for d in data
                if d.get("country", "").lower().replace(" ", "_") in country
            ]

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: NasdaqEconomicCalendarQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqEconomicCalendarData]:
        """Return the transformed data."""
        return [NasdaqEconomicCalendarData.model_validate(d) for d in data]

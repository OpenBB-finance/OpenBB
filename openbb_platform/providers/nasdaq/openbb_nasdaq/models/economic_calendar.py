"""Quandl Earnings Calendar fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from dateutil import parser
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_provider.utils.countries import country_list
from openbb_provider.utils.errors import EmptyDataError
from openbb_provider.utils.helpers import make_request
from pydantic import Field, field_validator


class NasdaqEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Nasdaq Economic Calendar Query.

    Source: https://api.nasdaq.com/api
    """

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(
        cls, country: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        if country is None:
            return None
        if isinstance(country, str):
            country = [country]
        countries = list(map(lambda x: x.lower(), country))
        if any(c not in country_list for c in countries):
            raise ValueError(f"'{country}' is not a valid country")
        return countries


class NasdaqEconomicCalendarData(EconomicCalendarData):
    """Nasdaq Earnings Calendar Data."""

    __alias_dict__ = {
        "event": "eventName",
    }

    time: Optional[str] = Field(
        default=None, alias="gmt", description="GMT of release (in HH:MM format)."
    )
    description: Optional[str] = Field(default=None, description="Event description.")

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, input_date: str) -> datetime:
        return parser.parse(input_date)


class NasdaqEconomicCalendarFetcher(
    Fetcher[
        NasdaqEconomicCalendarQueryParams,
        List[NasdaqEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the TE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqEconomicCalendarQueryParams:
        """Transform the query params."""
        return NasdaqEconomicCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Quandl endpoint."""

        start = query.start_date or datetime.today().date()
        end = query.end_date or datetime.today().date()
        dates = []
        while start <= end:
            dates.append(start.strftime("%Y-%m-%d"))
            start = start + timedelta(days=1)

        data = []
        for date in dates:
            try:
                response = (
                    make_request(
                        url=f"https://api.nasdaq.com/api/calendar/economicevents?date={date}",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
                        },
                    )
                    .json()
                    .get("data", {})
                    .get("rows", [])
                )
                for event in response:
                    event["date"] = date
                    event["actual"] = event.get("actual", "").replace("&nbsp;", "-")
                data.extend(response)
            except Exception:  # noqa: S112
                continue

        if len(data) == 0:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: NasdaqEconomicCalendarQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[NasdaqEconomicCalendarData]:
        """Return the transformed data."""
        if query.country:
            return [
                NasdaqEconomicCalendarData.model_validate(d)
                for d in data
                if d.get("country", "").lower() in query.country
            ]
        return [NasdaqEconomicCalendarData.model_validate(d) for d in data]

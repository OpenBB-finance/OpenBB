"""Nasdaq Economic Calendar fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union

from dateutil.parser import ParserError, parse
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_provider.utils.helpers import make_request
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
                    gmt = event.pop("gmt", "")
                    try:
                        event["date"] = parse(date + " " + gmt)
                    except ParserError:
                        event["date"] = parse(date)
                    event["actual"] = event.get("actual", "").replace("&nbsp;", "-")
                    event["previous"] = event.get("previous", "").replace("&nbsp;", "-")
                    event["consensus"] = event.get("consensus", "").replace(
                        "&nbsp;", "-"
                    )
                data.extend(response)
            except Exception:  # noqa: S112
                continue

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

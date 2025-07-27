"""Nasdaq Economic Calendar Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from pydantic import Field, field_validator


class NasdaqEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Nasdaq Economic Calendar Query.

    Source: https://www.nasdaq.com/market-activity/economic-calendar
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": None,
        }
    }

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
        # pylint: disable=import-outside-toplevel
        import html  # noqa
        from openbb_nasdaq.utils.helpers import remove_html_tags  # noqa

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
        list[NasdaqEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEconomicCalendarQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime, timedelta

        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=2)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return NasdaqEconomicCalendarQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEconomicCalendarQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_nasdaq.utils.helpers import get_headers, date_range

        IPO_HEADERS = get_headers(accept_type="json")
        data: list[dict] = []
        dates = [
            date.strftime("%Y-%m-%d")
            for date in date_range(query.start_date, query.end_date)
            if date.weekday() < 5  # Exclude weekends
        ]

        async def get_calendar_data(date: str):
            """Get the calendar data for a single date."""
            response: list = []
            url = f"https://api.nasdaq.com/api/calendar/economicevents?date={date}"
            r_json = await amake_request(url=url, headers=IPO_HEADERS)

            if (
                isinstance(r_json, dict)
                and (status := r_json.get("status", {}))
                and (messages := status.get("bCodeMessage", []))
                and (error_message := messages[0].get("errorMessage", ""))
                and not data
            ):
                raise OpenBBError(
                    f"Nasdaq Error -> {error_message}",
                )

            if r_json is not None and r_json.get("data"):  # type: ignore
                response = r_json["data"].get("rows")  # type: ignore

            if response:
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

        await asyncio.gather(*[get_calendar_data(date) for date in dates])

        if not data:
            raise OpenBBError(
                "There was an error with the request and it was returned empty."
            )

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

    @staticmethod
    def transform_data(
        query: NasdaqEconomicCalendarQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NasdaqEconomicCalendarData]:
        """Return the transformed data."""
        return [NasdaqEconomicCalendarData.model_validate(d) for d in data]

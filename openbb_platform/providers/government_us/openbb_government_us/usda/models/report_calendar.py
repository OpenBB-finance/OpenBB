"""FAS Report Calendar Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field

from openbb_government_us.usda.utils.fas_report_calendar import (
    COMMODITIES,
    REPORT_TYPES,
)

ReportType = Literal["export_sales", "trade_forecast", "world_markets_trade"]


class FasReportCalendarQueryParams(QueryParams):
    """FAS Report Calendar Query Parameters.

    Source: https://www.fas.usda.gov/data/scheduled-reports
    """

    __json_schema_extra__ = {
        "commodity": {"choices": sorted(COMMODITIES)},
        "report_type": {"choices": sorted(REPORT_TYPES)},
    }

    report_type: ReportType | None = Field(
        default=None,
        description="Filter by the type of report.",
    )
    commodity: str | None = Field(
        default=None,
        description="Filter by commodity.",
    )
    keyword: str | None = Field(
        default=None,
        description="Free-text filter. Matches a release's associated"
        + " commodities as well as its title, so it is broader than a title"
        + " search.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Applied to the release date after fetching.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Applied to the release date after fetching.",
    )


class FasReportCalendarData(Data):
    """FAS Report Calendar Data.

    The published schedule of upcoming USDA Foreign Agricultural Service
    report releases. The calendar is forward-looking only and does not
    enumerate past releases.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA FAS Report Calendar",
                "$.description": "Upcoming release schedule for USDA Foreign"
                " Agricultural Service reports.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "FAS"],
            },
        }
    )

    release_date: dateType = Field(
        description="Date of the release, in Eastern Time.",
    )
    release_time: str | None = Field(
        default=None,
        description="Time of day of the release, in Eastern Time.",
    )
    day_of_week: str | None = Field(
        default=None,
        description="Day of the week of the release.",
    )
    release_datetime: datetime | None = Field(
        default=None,
        description="Timestamp of the release, in UTC. None for releases whose"
        + " scheduled time has already passed, which the source stops"
        + " publishing a calendar entry for.",
    )
    report_type: str | None = Field(
        default=None,
        description="Type of the report.",
    )
    title: str = Field(
        description="Title of the report.",
    )
    url: str | None = Field(
        default=None,
        description="URL of the release announcement.",
    )
    released: bool = Field(
        description="Whether the release time has already passed.",
    )


class FasReportCalendarFetcher(
    Fetcher[
        FasReportCalendarQueryParams,
        list[FasReportCalendarData],
    ]
):
    """Fetch the USDA FAS report release calendar."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FasReportCalendarQueryParams:
        """Transform the query params."""
        return FasReportCalendarQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FasReportCalendarQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the calendar from the FAS website."""
        from openbb_government_us.usda.utils.fas_report_calendar import (
            afetch_calendar,
            build_url,
            parse_calendar,
        )

        html = await afetch_calendar(
            build_url(
                report_type=query.report_type,
                commodity=query.commodity,
                keyword=query.keyword,
            )
        )
        return parse_calendar(html)

    @staticmethod
    def transform_data(
        query: FasReportCalendarQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FasReportCalendarData]:
        """Transform the data."""
        from zoneinfo import ZoneInfo

        from openbb_core.provider.utils.errors import EmptyDataError

        eastern = ZoneInfo("America/New_York")
        results: list[FasReportCalendarData] = []
        for row in data:
            release_datetime = row["release_datetime"]
            if release_datetime is not None:
                release_date = release_datetime.astimezone(eastern).date()
            else:
                release_date = _fallback_date(row["month_day"], eastern)
            if query.start_date and release_date < query.start_date:
                continue
            if query.end_date and release_date > query.end_date:
                continue
            results.append(
                FasReportCalendarData.model_validate(
                    {
                        "release_date": release_date,
                        "release_time": row["release_time"],
                        "day_of_week": row["day_of_week"],
                        "release_datetime": release_datetime,
                        "report_type": row["report_type"],
                        "title": row["title"],
                        "url": row["url"],
                        "released": row["released"],
                    }
                )
            )
        if not results:
            raise EmptyDataError("The request was returned empty.")
        return sorted(results, key=lambda item: (item.release_date, item.title))


def _fallback_date(month_day: str | None, eastern: Any) -> dateType:
    """Derive a release date for a card that carries no calendar entry.

    Cards omit their iCalendar block only once the scheduled time has passed,
    so the release is the current Eastern-Time day.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    if not month_day:
        raise OpenBBError("The release carries neither a timestamp nor a date.")
    return datetime.now(tz=eastern).date()

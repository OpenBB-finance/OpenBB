"""Congress Calendars Model."""

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


class CongressCalendarsQueryParams(QueryParams):
    """Congress Calendars Query Parameters."""

    __json_schema_extra__ = {
        "chamber": {
            "x-widget_config": {
                "options": [
                    {"label": "House", "value": "house"},
                    {"label": "Senate", "value": "senate"},
                    {"label": "Both", "value": "both"},
                ],
                "paramName": "chamber",
                "label": "Chamber",
            },
        },
        "congress": {
            "x-widget_config": {"type": "number"},
        },
    }

    chamber: Literal["house", "senate", "both"] = Field(
        default="house",
        description="The chamber of Congress whose calendar to retrieve."
        + " Use 'both' for House and Senate editions together.",
    )
    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 119 for the 119th Congress)."
        + " When None, defaults to the current Congress.",
    )
    calendar_date: str | None = Field(
        default=None,
        description="Filter to a specific calendar date (YYYY-MM-DD), or"
        + " 'mostrecent' for the latest edition. When None, returns all editions.",
    )
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " When None, default sets to 100. Set to 0 for no limit.",
    )
    offset: int | None = Field(
        default=None,
        description="The starting record returned. 0 is the first record.",
    )
    sort_by: Literal["asc", "desc"] = Field(
        default="desc", description="Sort by calendar date. Default is latest first."
    )


class CongressCalendarsData(Data):
    """Congress Calendars Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Calendars",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Daily House and Senate calendar editions.",
                "$.params": [
                    {
                        "paramName": "package_id",
                        "label": "Package ID",
                        "description": "Ghost parameter to group by the calendar edition."
                        + " Create a group and use the 'Congressional Calendar Viewer'"
                        + " widget to view the calendar.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    package_id: str = Field(
        description="The GovInfo package identifier for the calendar edition.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Package ID",
                "headerTooltip": "Click a cell here to group by this edition and view"
                + " the calendar in the 'Congressional Calendar Viewer' widget.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "package_id",
                },
            },
        },
    )
    calendar_date: dateType = Field(
        description="The date of the calendar edition.",
    )
    chamber: str = Field(description="The chamber of Congress.")
    congress: int = Field(
        description="The congress session number.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    title: str = Field(description="The calendar edition title.")
    pdf: str = Field(
        description="URL to the calendar in PDF format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    htm: str = Field(
        description="URL to the calendar in HTML format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    xml: str = Field(
        description="URL to the calendar in XML format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


class CongressCalendarsFetcher(
    Fetcher[
        CongressCalendarsQueryParams,
        list[CongressCalendarsData],
    ]
):
    """Transform the query, extract and transform data from the GovInfo CCAL sitemaps."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressCalendarsQueryParams:
        """Transform the query params."""
        return CongressCalendarsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressCalendarsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract calendar editions from the GovInfo CCAL year sitemaps."""
        import asyncio

        from openbb_congress_gov.utils.bulk import filter_calendars, load_calendars
        from openbb_congress_gov.utils.helpers import year_to_congress

        congress = (
            query.congress
            if query.congress is not None
            else year_to_congress(datetime.now().year)
        )
        chambers = ["house", "senate"] if query.chamber == "both" else [query.chamber]
        loaded = await asyncio.gather(
            *[load_calendars(congress, chamber) for chamber in chambers]
        )
        records = [record for chamber_records in loaded for record in chamber_records]

        return filter_calendars(
            records,
            publishdate=query.calendar_date,
            limit=query.limit,
            offset=query.offset,
            sort_by=query.sort_by,
        )

    @staticmethod
    def transform_data(
        query: CongressCalendarsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressCalendarsData]:
        """Transform raw calendar records into CongressCalendarsData models."""
        return [CongressCalendarsData(**record) for record in data]

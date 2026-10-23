"""IMF Maritime Disruption Events Model."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class ImfDisruptionEventsQueryParams(QueryParams):
    """IMF Maritime Disruption Events Query Parameters."""

    __json_schema_extra__ = {
        "country": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/portwatch/list_country_choices",
                "style": {"popupWidth": 350},
            }
        },
        "alertlevel": {
            "x-widget_config": {
                "type": "text",
                "options": [
                    {"label": "All Alerts", "value": "ALL"},
                    {"label": "Red", "value": "RED"},
                    {"label": "Orange", "value": "ORANGE"},
                    {"label": "Green", "value": "GREEN"},
                ],
            }
        },
        "eventtype": {"x-widget_config": {"type": "text"}},
        "start_date": {"x-widget_config": {"type": "date"}},
        "end_date": {"x-widget_config": {"type": "date"}},
        "active_only": {"x-widget_config": {"type": "boolean"}},
        "theme": {"x-widget_config": {"show": False}},
    }

    country: str | None = Field(
        default=None,
        description="ISO3 country code to restrict the event list to.",
        title="Country",
    )
    alertlevel: Literal["ALL", "RED", "ORANGE", "GREEN"] = Field(
        default="ALL",
        description="Alert level filter: 'ALL', 'RED', 'ORANGE', or 'GREEN'.",
        title="Alert Level",
    )
    eventtype: str | None = Field(
        default=None,
        description="Optional event-type filter (e.g. 'Cyclone', 'Conflict').",
        title="Event Type",
    )
    start_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) lower bound on the event start (fromdate).",
        title="Start Date",
    )
    end_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) upper bound on the event start (fromdate).",
        title="End Date",
    )
    active_only: bool = Field(
        default=False,
        description="If True, restrict to events whose end date is in the future or unset.",
        title="Active Only",
    )
    theme: Literal["dark", "light"] | None = Field(
        default=None,
        description="Theme for the map chart. Only used when ``chart=True``.",
        title="Theme",
    )


class ImfDisruptionEventsData(Data):
    """IMF Maritime Disruption Event Data."""

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Maritime Disruption Events",
                "$.description": (
                    "Maritime disruption events from IMF Port Watch with country,"
                    " type, alert level, and date filters."
                ),
                "$.gridData": {"w": 40, "h": 16},
                "$.refetchInterval": False,
                "$.category": "IMF Utilities",
                "$.subCategory": "Port Watch",
                "$.source": ["UN Global Platform; IMF PortWatch"],
            }
        },
    )

    __alias_dict__ = {
        "object_id": "ObjectId",
        "shape_area": "Shape__Area",
        "shape_length": "Shape__Length",
        "html_name": "htmlname",
        "html_description": "htmldescription",
        "page_id": "pageid",
        "longitude": "long",
        "latitude": "lat",
    }

    eventid: int = Field(description="Event identifier.", title="Event ID")
    eventname: str = Field(description="Event name.", title="Event")
    eventtype: str | None = Field(
        default=None, description="Event type (e.g. 'Conflict').", title="Type"
    )
    alertlevel: str | None = Field(
        default=None,
        description="Alert level (RED / ORANGE / GREEN).",
        title="Alert Level",
    )
    severitytext: str | None = Field(
        default=None,
        description="Free-form severity description.",
        title="Severity",
    )
    country: str | None = Field(
        default=None,
        description="ISO3 country code of the affected event.",
        title="Country",
    )
    fromdate: str | None = Field(
        default=None, description="Event start date.", title="From"
    )
    todate: str | None = Field(
        default=None, description="Event end date (null if ongoing).", title="To"
    )
    editdate: str | None = Field(
        default=None, description="Last update timestamp.", title="Edited"
    )
    year: int | None = Field(
        default=None, description="Year of the event start.", title="Year"
    )
    n_affectedports: int | None = Field(
        default=None,
        description="Number of ports flagged as affected by this event.",
        title="Affected Ports",
    )
    affectedports: str | None = Field(
        default=None,
        description="Comma-separated list of affected port IDs.",
        title="Affected Ports List",
    )
    affectedpopulation: str | None = Field(
        default=None,
        description="Estimated population of the affected area.",
        title="Affected Population",
    )
    latitude: float | None = Field(
        default=None,
        description="Latitude of the event's centroid.",
        title="Latitude",
    )
    longitude: float | None = Field(
        default=None,
        description="Longitude of the event's centroid.",
        title="Longitude",
    )
    html_name: str | None = Field(
        default=None,
        description="Event name with embedded HTML for rich tooltips.",
        title="HTML Name",
    )
    html_description: str | None = Field(
        default=None,
        description="Event description with embedded HTML.",
        title="HTML Description",
    )
    page_id: str | None = Field(
        default=None,
        description="IMF Port Watch event-detail page identifier.",
        title="Page ID",
    )
    object_id: int | None = Field(
        default=None,
        description="Internal ArcGIS feature row identifier.",
        title="Object ID",
    )
    shape_area: float | None = Field(
        default=None,
        description="Affected-area polygon area in projected units.",
        title="Shape Area",
    )
    shape_length: float | None = Field(
        default=None,
        description="Affected-area polygon perimeter in projected units.",
        title="Shape Length",
    )


class ImfDisruptionEventsFetcher(
    Fetcher[ImfDisruptionEventsQueryParams, list[ImfDisruptionEventsData]]
):
    """IMF Maritime Disruption Events Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfDisruptionEventsQueryParams:
        """Validate and coerce request params."""
        return ImfDisruptionEventsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfDisruptionEventsQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch matching disruption events from IMF Port Watch."""
        from openbb_imf.utils.port_watch_helpers import get_disruption_events

        level = None if query.alertlevel.upper() in ("", "ALL") else query.alertlevel
        return await get_disruption_events(
            query.country,
            query.eventtype,
            level,
            query.active_only,
            query.start_date,
            query.end_date,
        )

    @staticmethod
    def transform_data(
        query: ImfDisruptionEventsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfDisruptionEventsData]:
        """Coerce raw rows into ``ImfDisruptionEventsData`` instances."""
        return [ImfDisruptionEventsData.model_validate(row) for row in data]

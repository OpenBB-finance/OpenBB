"""IMF Disruption Sankey Spillover Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, PrivateAttr

api_prefix = SystemService().system_settings.api_settings.prefix


class ImfDisruptionSankeyQueryParams(QueryParams):
    """IMF Disruption Sankey Query Parameters."""

    __json_schema_extra__ = {
        "event_id": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/portwatch/list_disruption_event_choices",
                "style": {"popupWidth": 600},
            }
        },
        "theme": {"x-widget_config": {"show": False}},
    }

    event_id: str = Field(
        default="LATEST",
        description="Disruption event ID, or 'LATEST' for the most recent event.",
        title="Event",
    )
    theme: Literal["dark", "light"] | None = Field(
        default=None,
        description="Theme for the Sankey chart. Only used when ``chart=True``.",
        title="Theme",
    )

    _event_label: str | None = PrivateAttr(default=None)


class ImfDisruptionSankeyData(Data):
    """IMF Disruption Sankey Edge Data."""

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Disruption Capacity Spillover",
                "$.description": (
                    "Sankey edges showing how vessel capacity reroutes between"
                    " ports during a maritime disruption event. Source: IMF Port"
                    " Watch."
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
        "source_port": "from_",
        "source_port_id": "from_id",
        "source_country_code": "from_iso3",
        "target_port": "to_",
        "target_port_id": "to_id",
        "target_country_code": "to_iso3",
    }

    eventid: int = Field(description="Event identifier.", title="Event ID")
    source: int = Field(
        description="Source node index in the Sankey diagram.", title="Source Index"
    )
    target: int = Field(
        description="Target node index in the Sankey diagram.", title="Target Index"
    )
    source_port: str = Field(
        description="Display label for the source port (e.g. 'Colombo (Sri Lanka)').",
        title="Source Port",
    )
    target_port: str = Field(
        description="Display label for the destination port.",
        title="Target Port",
    )
    source_port_id: str | None = Field(
        default=None,
        description="IMF Port Watch port ID of the source.",
        title="Source Port ID",
    )
    target_port_id: str | None = Field(
        default=None,
        description="IMF Port Watch port ID of the destination.",
        title="Target Port ID",
    )
    source_country_code: str | None = Field(
        default=None,
        description="ISO3 country code of the source port.",
        title="Source ISO3",
    )
    target_country_code: str | None = Field(
        default=None,
        description="ISO3 country code of the destination port.",
        title="Target ISO3",
    )
    perc_disaster_capacity: float | None = Field(
        default=None,
        description="Share (%) of the disrupted capacity rerouted along this edge.",
        title="% Capacity",
    )
    object_id: int | None = Field(
        default=None,
        description="Internal ArcGIS feature row identifier.",
        title="Object ID",
    )


class ImfDisruptionSankeyFetcher(
    Fetcher[ImfDisruptionSankeyQueryParams, list[ImfDisruptionSankeyData]]
):
    """IMF Disruption Sankey Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfDisruptionSankeyQueryParams:
        """Validate and coerce request params."""
        return ImfDisruptionSankeyQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfDisruptionSankeyQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Resolve ``LATEST`` and fetch the Sankey spillover edges."""
        from openbb_imf.utils.port_watch_helpers import (
            get_disruption_events,
            get_disruption_sankey_edges,
        )

        if query.event_id.upper() == "LATEST":
            events = await get_disruption_events()
            if not events:
                raise OpenBBError("No disruption events available.")
            resolved_id = int(events[0]["eventid"])
            query._event_label = events[0].get("eventname") or f"Event {resolved_id}"
        else:
            resolved_id = int(query.event_id)
            query._event_label = f"Event {resolved_id}"

        return await get_disruption_sankey_edges(resolved_id)

    @staticmethod
    def transform_data(
        query: ImfDisruptionSankeyQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfDisruptionSankeyData]:
        """Coerce raw rows into ``ImfDisruptionSankeyData`` instances."""
        return [ImfDisruptionSankeyData.model_validate(row) for row in data]

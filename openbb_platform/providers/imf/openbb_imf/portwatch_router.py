"""IMF Port Watch sub-router (mounted at ``/imf/portwatch``)."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

portwatch_router = Router(prefix="", description="IMF Port Watch endpoints.")


@portwatch_router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get port ID choices for IMF Port Watch.",
            parameters={},
        )
    ],
)
async def list_port_id_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of IMF Port Watch port IDs."""
    from openbb_imf.utils.port_watch_helpers import get_port_id_choices

    return get_port_id_choices()


@portwatch_router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="ISO3 country choices.", parameters={})],
)
async def list_country_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of ISO3 countries from the IMF Port Watch ports database."""
    from openbb_imf.utils.port_watch_helpers import list_countries

    return list_countries()


@portwatch_router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Tradenow regions.", parameters={})],
)
async def list_tradenow_region_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of TradeNow regions for dropdown widgets."""
    from openbb_imf.utils.port_watch_helpers import get_tradenow_region_choices

    return await get_tradenow_region_choices()


@portwatch_router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Container metric ports.", parameters={})],
)
async def list_container_port_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of ports present in the Container Metrics table, with TOP10."""
    from openbb_imf.utils.port_watch_helpers import get_container_port_choices

    choices = await get_container_port_choices()
    return [{"label": "Top 10 by Metric", "value": "TOP10"}, *choices]


@portwatch_router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Disruption events.", parameters={})],
)
async def list_disruption_event_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of disruption events ordered by start date, with LATEST."""
    from openbb_imf.utils.port_watch_helpers import get_sankey_event_choices

    events = await get_sankey_event_choices()
    return [{"label": "Latest Disruption", "value": "LATEST"}, *events]


@portwatch_router.command(
    model="CountryActivity",
    examples=[
        APIEx(
            description="Daily maritime activity for the USA.",
            parameters={"country_code": "USA", "provider": "imf"},
        )
    ],
)
async def country_activity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Daily country-level port calls, imports, and exports from IMF Port Watch."""
    return await OBBject.from_query(OBBQuery(**locals()))


@portwatch_router.command(
    model="MonthlyTrade",
    examples=[
        APIEx(
            description="Monthly TradeNow indices for the USA.",
            parameters={"code": "USA", "provider": "imf"},
        )
    ],
)
async def monthly_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly TradeNow trade-value, trade-volume, and AIS port-call series."""
    return await OBBject.from_query(OBBQuery(**locals()))


@portwatch_router.command(
    model="ContainerMetrics",
    examples=[
        APIEx(
            description="Top-10 container port calls.",
            parameters={"metric": "portcalls", "provider": "imf"},
        )
    ],
)
async def container_metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly container metrics by port (long format)."""
    return await OBBject.from_query(OBBQuery(**locals()))


@portwatch_router.command(
    model="DisruptionEvents",
    examples=[
        APIEx(
            description="All current disruption events.",
            parameters={"provider": "imf"},
        )
    ],
)
async def disruption_events(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Maritime disruption events with country / type / alert / date filters."""
    return await OBBject.from_query(OBBQuery(**locals()))


@portwatch_router.command(
    model="DisruptionEvents",
    examples=[
        APIEx(
            description="Map of current disruption events.",
            parameters={"provider": "imf"},
        )
    ],
)
async def disruptions_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Disruption events surfaced as a Scattergeo chart when ``chart=True``."""
    return await OBBject.from_query(OBBQuery(**locals()))


@portwatch_router.command(
    model="DisruptionSankey",
    examples=[
        APIEx(
            description="Sankey edges for the latest disruption event.",
            parameters={"event_id": "LATEST", "provider": "imf"},
        )
    ],
)
async def disruption_sankey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Capacity-spillover Sankey edges for a single disruption event."""
    return await OBBject.from_query(OBBQuery(**locals()))

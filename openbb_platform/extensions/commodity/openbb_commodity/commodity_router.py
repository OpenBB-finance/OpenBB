"""The Commodity router."""

# pylint: disable=unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="", description="Commodity market data.")


@router.command(
    model="LbmaFixing",
    examples=[
        APIEx(parameters={"provider": "nasdaq"}),
        APIEx(
            description="Get the daily LBMA fixing prices for silver in 2023.",
            parameters={
                "asset": "silver",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "transform": "rdiff",
                "collapse": "monthly",
                "provider": "nasdaq",
            },
        ),
    ],
)
async def lbma_fixing(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Daily LBMA Fixing Prices in USD/EUR/GBP."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PetroleumStatusReport",
    examples=[
        APIEx(
            description="Get the EIA's Weekly Petroleum Status Report.",
            parameters={"provider": "eia"},
        ),
        APIEx(
            description="Select the category of data, and filter for a specific table within the report.",
            parameters={
                "category": "weekly_estimates",
                "table": "imports",
                "provider": "eia",
            },
        ),
    ],
)
async def petroleum_status_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """EIA Weekly Petroleum Status Report."""
    return await OBBject.from_query(Query(**locals()))

"""The Commodity router."""

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
from pydantic import BaseModel

router = Router(prefix="", description="Commodity market data.")


# pylint: disable=unused-argument
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
) -> OBBject[BaseModel]:
    """Daily LBMA Fixing Prices in USD/EUR/GBP."""
    return await OBBject.from_query(Query(**locals()))

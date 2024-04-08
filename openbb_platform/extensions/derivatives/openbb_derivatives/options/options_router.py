"""Options Router."""

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

router = Router(prefix="/options")

# pylint: disable=unused-argument


@router.command(
    model="OptionsChains",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            description='Use the "date" parameter to get the end-of-day-data for a specific date, where supported.',
            parameters={"symbol": "AAPL", "date": "2023-01-25", "provider": "intrinio"},
        ),
    ],
)
async def chains(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the complete options chain for a ticker."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="OptionsUnusual",
    examples=[
        APIEx(parameters={"provider": "intrinio"}),
        APIEx(
            description="Use the 'symbol' parameter to get the most recent activity for a specific symbol.",
            parameters={"symbol": "TSLA", "provider": "intrinio"},
        ),
    ],
)
async def unusual(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the complete options chain for a ticker."""
    return await OBBject.from_query(Query(**locals()))

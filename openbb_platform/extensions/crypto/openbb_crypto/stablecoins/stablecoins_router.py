# pylint: disable=W0613:unused-argument
"""Crypto Stablecoins Router."""

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

router = Router(prefix="/stablecoins")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="StablecoinsList",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def list(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get all stablecoins along with their circulating amounts."""
    return await OBBject.from_query(Query(**locals()))

@router.command(
    model="StablecoinsCurrent",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def current(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get current market cap sum of all stablecoins on each chain."""
    return await OBBject.from_query(Query(**locals()))

@router.command(
    model="StablecoinsHistorical",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical prices of all stablecoins."""
    return await OBBject.from_query(Query(**locals()))

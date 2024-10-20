# pylint: disable=W0613:unused-argument
"""Crypto TVL Router."""

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

router = Router(prefix="/tvl")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="TvlChains",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def chains(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the current TVL for all chains."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TvlHistorical",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
        APIEx(parameters={"provider": "defillama", "symbol": "uniswap"}),
        APIEx(parameters={"provider": "defillama", "symbol_type": "chain"}),
        APIEx(
            parameters={
                "provider": "defillama",
                "symbol": "ethereum",
                "symbol_type": "chain",
            }
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the historical TVL for a given protocol, chain or all chains."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TvlCurrent",
    examples=[
        APIEx(parameters={"symbol": "uniswap", "provider": "defillama"}),
    ],
)
async def current(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the current TVl of a given protocol."""
    return await OBBject.from_query(Query(**locals()))

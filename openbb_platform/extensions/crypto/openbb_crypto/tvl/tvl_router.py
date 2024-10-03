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


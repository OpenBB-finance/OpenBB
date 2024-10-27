# pylint: disable=W0613:unused-argument
"""Crypto Yields Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/yields")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="YieldsPools",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
        PythonEx(parameters={"provider": "defillama"}),
    ],
)
async def pools(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the the latest data for all pools."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="YieldsHistorical",
    examples=[
        APIEx(
            parameters={
                "provider": "defillama",
                "pool_id": "747c1d2a-c668-4682-b9f9-296708a3dd90",
            }
        ),
        PythonEx(
            parameters={
                "provider": "defillama",
                "pool_id": "747c1d2a-c668-4682-b9f9-296708a3dd90",
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

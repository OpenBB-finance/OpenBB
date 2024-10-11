# pylint: disable=W0613:unused-argument
"""Crypto Coins Router."""

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

router = Router(prefix="/coins")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="BlockTimestamp",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def block(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the closest block to a timestamp."""
    return await OBBject.from_query(Query(**locals()))

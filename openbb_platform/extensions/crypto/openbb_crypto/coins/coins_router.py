# pylint: disable=W0613:unused-argument
"""Crypto Coins Router."""

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
    """Get the closest block to a timestamp for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsCurrent",
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
    """Get the current price of coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsFirst",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def first(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the earliest timestamp price record for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsChange",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def change(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the percentage change in pricer over time for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsChart",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
    ],
)
async def chart(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the price at regular intervals for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsHistorical",
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
    """Get the historical price for a coin."""
    return await OBBject.from_query(Query(**locals()))

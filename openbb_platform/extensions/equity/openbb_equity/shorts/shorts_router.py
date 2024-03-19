"""Shorts Router."""

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

router = Router(prefix="/shorts")

# pylint: disable=unused-argument


@router.command(
    model="EquityFTD",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "sec"})],
)
async def fails_to_deliver(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get reported Fail-to-deliver (FTD) data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ShortVolume",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "stockgrid"})],
)
async def short_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get reported Fail-to-deliver (FTD) data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityShortInterest",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "finra"})],
)
async def short_interest(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get reported short volume and days to cover data."""
    return await OBBject.from_query(Query(**locals()))

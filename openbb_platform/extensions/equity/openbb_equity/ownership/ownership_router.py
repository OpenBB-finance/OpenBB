"""Ownership Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/ownership")

# pylint: disable=unused-argument


@router.command(model="EquityOwnership")
async def major_holders(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Equity Ownership. Information about the company ownership."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="InstitutionalOwnership")
async def institutional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Institutional Ownership. Institutional ownership data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="InsiderTrading")
async def insider_trading(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Insider Trading. Information about insider trading."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ShareStatistics")
async def share_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Share Statistics. Share statistics for a given company."""
    return await OBBject.from_query(Query(**locals()))

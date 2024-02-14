"""Disc router for ETFs."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/discovery")

# pylint: disable=unused-argument


@router.command(model="ETFGainers", operation_id="etf_gainers")
async def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the top ETF gainers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ETFLosers", operation_id="etf_losers")
async def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the top ETF losers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ETFActive", operation_id="etf_active")
async def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the most active ETFs."""
    return await OBBject.from_query(Query(**locals()))

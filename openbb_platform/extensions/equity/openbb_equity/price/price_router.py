"""Price Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/price")

# pylint: disable=unused-argument


@router.command(model="EquityQuote")
async def quote(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the latest quote for a given stock. Quote includes price, volume, and other data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityNBBO")
async def nbbo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the National Best Bid and Offer for a given stock."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityHistorical")
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical price data for a given stock. This includes open, high, low, close, and volume."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="PricePerformance")
async def performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get price performance data for a given stock. This includes price changes for different time periods."""
    return await OBBject.from_query(Query(**locals()))

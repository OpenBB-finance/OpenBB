"""Calendar Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/calendar")

# pylint: disable=unused-argument


@router.command(model="CalendarIpo")
async def ipo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Upcoming and Historical IPO Calendar."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CalendarDividend")
async def dividend(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Upcoming and Historical Dividend Calendar."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CalendarSplits")
async def splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Calendar Splits. Show Stock Split Calendar."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CalendarEarnings")
async def earnings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Upcoming and Historical earnings calendar."""
    return await OBBject.from_query(Query(**locals()))

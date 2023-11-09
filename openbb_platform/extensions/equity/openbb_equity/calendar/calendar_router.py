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
from pydantic import BaseModel

router = Router(prefix="/calendar")

# pylint: disable=unused-argument


@router.command(model="CalendarIpo")
def ipo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Upcoming and Historical IPO Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CalendarDividend")
def dividend(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Upcoming and Historical Dividend Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockSplitCalendar")
def split(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Split Calendar. Show Stock Split Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EarningsCalendar")
def earnings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Upcoming and Historical earnings calendar."""
    return OBBject(results=Query(**locals()).execute())

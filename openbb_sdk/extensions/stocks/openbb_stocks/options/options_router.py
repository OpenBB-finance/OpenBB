"""Options Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/options")


@router.command(model="OptionsChains")
def chains(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the complete options chain for a ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command
def eodchain() -> OBBject[Empty]:  # type: ignore
    """Gets option chain at a specific date."""
    return OBBject(results=Empty())


@router.command
def hist() -> OBBject[Empty]:  # type: ignore
    """Get historical data for a single option contract."""
    return OBBject(results=Empty())


@router.command
def info() -> OBBject[Empty]:  # type: ignore
    """Display option information (volatility, IV rank, etc.)."""
    return OBBject(results=Empty())


@router.command
def pcr() -> OBBject[Empty]:  # type: ignore
    """Display historical rolling put/call ratio for ticker over a defined window."""
    return OBBject(results=Empty())


@router.command
def unu() -> OBBject[Empty]:  # type: ignore
    """Show unusual options activity."""
    return OBBject(results=Empty())

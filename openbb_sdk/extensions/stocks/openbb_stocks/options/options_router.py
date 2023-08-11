"""Options Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import Obbject
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
) -> Obbject[BaseModel]:
    """Get the complete options chain for a ticker."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def eodchain() -> Obbject[Empty]:  # type: ignore
    """Gets option chain at a specific date."""
    return Obbject(results=Empty())


@router.command
def hist() -> Obbject[Empty]:  # type: ignore
    """Get historical data for a single option contract."""
    return Obbject(results=Empty())


@router.command
def info() -> Obbject[Empty]:  # type: ignore
    """Display option information (volatility, IV rank, etc.)."""
    return Obbject(results=Empty())


@router.command
def pcr() -> Obbject[Empty]:  # type: ignore
    """Display historical rolling put/call ratio for ticker over a defined window."""
    return Obbject(results=Empty())


@router.command
def unu() -> Obbject[Empty]:  # type: ignore
    """Show unusual options activity."""
    return Obbject(results=Empty())

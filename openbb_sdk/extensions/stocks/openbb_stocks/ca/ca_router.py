# pylint: disable=W0613:unused-argument
"""Comparison Analysis Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/ca")


@router.command(model="StockPeers")
def get(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Company peers."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def balance() -> CommandOutput[Empty]:  # type: ignore
    """Company balance sheet."""
    return CommandOutput(results=Empty())


@router.command
def cashflow() -> CommandOutput[Empty]:  # type: ignore
    """Company cashflow."""
    return CommandOutput(results=Empty())


@router.command
def hcorr() -> CommandOutput[Empty]:  # type: ignore
    """Company historical correlation."""
    return CommandOutput(results=Empty())


@router.command
def hist() -> CommandOutput[Empty]:  # type: ignore
    """Company historical prices."""
    return CommandOutput(results=Empty())


@router.command
def income() -> CommandOutput[Empty]:  # type: ignore
    """Company income statement."""
    return CommandOutput(results=Empty())


@router.command
def scorr() -> CommandOutput[Empty]:  # type: ignore
    """Company sector correlation."""
    return CommandOutput(results=Empty())


@router.command
def screener() -> CommandOutput[Empty]:  # type: ignore
    """Company screener."""
    return CommandOutput(results=Empty())


@router.command
def sentiment() -> CommandOutput[Empty]:  # type: ignore
    """Company sentiment."""
    return CommandOutput(results=Empty())


@router.command
def similar() -> CommandOutput[Empty]:  # type: ignore
    """Company similar."""
    return CommandOutput(results=Empty())


@router.command
def volume() -> CommandOutput[Empty]:  # type: ignore
    """Company volume."""
    return CommandOutput(results=Empty())

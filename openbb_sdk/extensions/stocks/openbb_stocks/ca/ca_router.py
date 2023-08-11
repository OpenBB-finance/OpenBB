# pylint: disable=W0613:unused-argument
"""Comparison Analysis Router."""

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

router = Router(prefix="/ca")


@router.command(model="StockPeers")
def peers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Company peers."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def balance() -> Obbject[Empty]:  # type: ignore
    """Company balance sheet."""
    return Obbject(results=Empty())


@router.command
def cashflow() -> Obbject[Empty]:  # type: ignore
    """Company cashflow."""
    return Obbject(results=Empty())


@router.command
def hcorr() -> Obbject[Empty]:  # type: ignore
    """Company historical correlation."""
    return Obbject(results=Empty())


@router.command
def hist() -> Obbject[Empty]:  # type: ignore
    """Company historical prices."""
    return Obbject(results=Empty())


@router.command
def income() -> Obbject[Empty]:  # type: ignore
    """Company income statement."""
    return Obbject(results=Empty())


@router.command
def scorr() -> Obbject[Empty]:  # type: ignore
    """Company sector correlation."""
    return Obbject(results=Empty())


@router.command
def screener() -> Obbject[Empty]:  # type: ignore
    """Company screener."""
    return Obbject(results=Empty())


@router.command
def sentiment() -> Obbject[Empty]:  # type: ignore
    """Company sentiment."""
    return Obbject(results=Empty())


@router.command
def similar() -> Obbject[Empty]:  # type: ignore
    """Company similar."""
    return Obbject(results=Empty())


@router.command
def volume() -> Obbject[Empty]:  # type: ignore
    """Company volume."""
    return Obbject(results=Empty())

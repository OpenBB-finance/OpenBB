# pylint: disable=W0613:unused-argument
"""Comparison Analysis Router."""

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

router = Router(prefix="/ca")


@router.command(model="StockPeers")
def peers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Company peers."""
    return OBBject(results=Query(**locals()).execute())


@router.command
def balance() -> OBBject[Empty]:  # type: ignore
    """Company balance sheet."""
    return OBBject(results=Empty())


@router.command
def cashflow() -> OBBject[Empty]:  # type: ignore
    """Company cashflow."""
    return OBBject(results=Empty())


@router.command
def hcorr() -> OBBject[Empty]:  # type: ignore
    """Company historical correlation."""
    return OBBject(results=Empty())


@router.command
def hist() -> OBBject[Empty]:  # type: ignore
    """Company historical prices."""
    return OBBject(results=Empty())


@router.command
def income() -> OBBject[Empty]:  # type: ignore
    """Company income statement."""
    return OBBject(results=Empty())


@router.command
def scorr() -> OBBject[Empty]:  # type: ignore
    """Company sector correlation."""
    return OBBject(results=Empty())


@router.command
def screener() -> OBBject[Empty]:  # type: ignore
    """Company screener."""
    return OBBject(results=Empty())


@router.command
def sentiment() -> OBBject[Empty]:  # type: ignore
    """Company sentiment."""
    return OBBject(results=Empty())


@router.command
def similar() -> OBBject[Empty]:  # type: ignore
    """Company similar."""
    return OBBject(results=Empty())


@router.command
def volume() -> OBBject[Empty]:  # type: ignore
    """Company volume."""
    return OBBject(results=Empty())

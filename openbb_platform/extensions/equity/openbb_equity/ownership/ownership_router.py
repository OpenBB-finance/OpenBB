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
from pydantic import BaseModel

router = Router(prefix="/ownership")

# pylint: disable=unused-argument


@router.command(model="EquityOwnership")
def major_holders(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Equity Ownership. Information about the company ownership."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="InstitutionalOwnership")
def institutional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Institutional Ownership. Institutional ownership data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="InsiderTrading")
def insider_trading(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Insider Trading. Information about insider trading."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ShareStatistics")
def share_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Share Statistics. Share statistics for a given company."""
    return OBBject(results=Query(**locals()).execute())

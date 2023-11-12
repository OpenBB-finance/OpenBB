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
from pydantic import BaseModel

router = Router(prefix="/discovery")

# pylint: disable=unused-argument


@router.command(model="ETFGainers")
def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top ETF gainers."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ETFLosers")
def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top ETF losers."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ETFActive")
def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the most active ETFs."""
    return OBBject(results=Query(**locals()).execute())

"""Disc router for Equities."""
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

router = Router(prefix="/disc")


@router.command(model="EquityGainers")
def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top Equity gainers."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityLosers")
def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top Equity losers."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityActive")
def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the most active Equities."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityUndervaluedLargeCaps")
def undervalued_large_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get undervalued large cap Equities."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityUndervaluedGrowthEquities")
def undervalued_growth_equities(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get undervalued growth Equities."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityAggressiveSmallCaps")
def aggressive_small_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get aggressive small cap Equities."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="GrowthTechEquities")
def growth_tech_equities(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get growth tech Equities."""
    return OBBject(results=Query(**locals()).execute())

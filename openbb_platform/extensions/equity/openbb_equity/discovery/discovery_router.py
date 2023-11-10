"""Disc router for Equities."""
# pylint: disable=unused-argument
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


@router.command(model="EquityUndervaluedGrowth")
def undervalued_growth(
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
def growth_tech(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get growth tech Equities."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="TopRetail")
def top_retail(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Tracks over $30B USD/day of individual investors trades.

    It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
    ADRs, and ETPs.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="UpcomingReleaseDays")
def upcoming_release_days(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get upcoming release days."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="DiscoveryFilings")
def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the most-recent filings submitted to the SEC."""
    return OBBject(results=Query(**locals()).execute())

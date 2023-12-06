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
async def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top Equity gainers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityLosers")
async def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the top Equity losers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityActive")
async def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the most active Equities."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityUndervaluedLargeCaps")
async def undervalued_large_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get undervalued large cap Equities."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityUndervaluedGrowth")
async def undervalued_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get undervalued growth Equities."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityAggressiveSmallCaps")
async def aggressive_small_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get aggressive small cap Equities."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="GrowthTechEquities")
async def growth_tech(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get growth tech Equities."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TopRetail")
async def top_retail(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Tracks over $30B USD/day of individual investors trades.

    It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
    ADRs, and ETPs.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="UpcomingReleaseDays")
async def upcoming_release_days(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get upcoming release days."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="DiscoveryFilings")
async def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the most-recent filings submitted to the SEC."""
    return await OBBject.from_query(Query(**locals()))

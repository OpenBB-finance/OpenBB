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

router = Router(prefix="/discovery")


@router.command(model="EquityGainers")
async def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the top price gainers in the stock market."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityLosers")
async def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the top price losers in the stock market."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityActive")
async def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the most actively traded stocks based on volume."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityUndervaluedLargeCaps")
async def undervalued_large_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get potentially undervalued large cap stocks."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityUndervaluedGrowth")
async def undervalued_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get potentially undervalued growth stocks."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EquityAggressiveSmallCaps")
async def aggressive_small_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get top small cap stocks based on earnings growth."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="GrowthTechEquities")
async def growth_tech(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get top tech stocks based on revenue and earnings growth."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TopRetail")
async def top_retail(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Tracks over $30B USD/day of individual investors trades.

    It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
    ADRs, and ETPs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="UpcomingReleaseDays")
async def upcoming_release_days(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get upcoming earnings release dates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DiscoveryFilings",
    examples=[
        "# Get filings for the year 2023, limited to 100 results",
        "obb.equity.discovery.filings(start_date='2023-01-01', end_date='2023-12-31')",
    ],
)
async def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more. SEC
    filings include Form 10-K, Form 10-Q, Form 8-K, the proxy statement, Forms 3, 4, and 5, Schedule 13, Form 114,
    Foreign Investment Disclosures and others. The annual 10-K report is required to be
    filed annually and includes the company's financial statements, management discussion and analysis,
    and audited financial statements.
    """
    return await OBBject.from_query(Query(**locals()))

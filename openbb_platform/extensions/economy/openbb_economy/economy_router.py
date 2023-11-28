"""Economy Router."""
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

from openbb_economy.gdp.gdp_router import router as gdp_router

router = Router(prefix="")
router.include_router(gdp_router)

# pylint: disable=unused-argument


@router.command(model="EconomicCalendar")
async def calendar(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Economic Calendar."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ConsumerPriceIndex")
async def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Consumer Price Index (CPI) Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RiskPremium")
async def risk_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Market Risk Premium."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="BalanceOfPayments")
async def balance_of_payments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Balance of Payments Reports."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FredSearch")
async def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    Search for FRED series or economic releases by ID or fuzzy query.
    This does not return the observation values, only the metadata.
    Use this function to find series IDs for `fred_series()`.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FredSeries")
async def fred_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get data by series ID from FRED."""
    return await OBBject.from_query(Query(**locals()))

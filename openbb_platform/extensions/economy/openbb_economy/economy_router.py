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
def calendar(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Economic Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ConsumerPriceIndex")
def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Consumer Price Index (CPI) Data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RiskPremium")
def risk_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Market Risk Premium."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="BalanceOfPayments")
def balance_of_payments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Balance of Payments Reports."""
    return OBBject(results=Query(**locals()).execute())

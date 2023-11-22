"""ETF Router."""

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

from openbb_etf.discovery.discovery_router import router as discovery_router

router = Router(prefix="")
router.include_router(discovery_router)

# pylint: disable=unused-argument


@router.command(model="EtfSearch")
def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search for ETFs.

    An empty query returns the full list of ETFs from the provider.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfHistorical")
def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Historical Market Price."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfInfo")
def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Information Overview."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfSectors")
def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Sector weighting."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfCountries")
def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Country weighting."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PricePerformance")
def price_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price performance as a return, over different periods."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfHoldings")
def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the holdings for an individual ETF."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfHoldingsDate")
def holdings_date(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the holdings filing date for an individual ETF."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EtfHoldingsPerformance")
def holdings_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the ETF holdings performance."""
    return OBBject(results=Query(**locals()).execute())

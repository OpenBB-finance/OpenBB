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
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search for ETFs.

    An empty query returns the full list of ETFs from the provider.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfHistorical", operation_id="etf_historical")
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Historical Market Price."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfInfo")
async def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Information Overview."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfSectors")
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Sector weighting."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfCountries")
async def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """ETF Country weighting."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="PricePerformance")
async def price_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price performance as a return, over different periods."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfHoldings")
async def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the holdings for an individual ETF."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfHoldingsDate")
async def holdings_date(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the holdings filing date for an individual ETF."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EtfHoldingsPerformance")
async def holdings_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the ETF holdings performance."""
    return await OBBject.from_query(Query(**locals()))

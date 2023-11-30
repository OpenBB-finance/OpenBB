"""Index Router."""
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

router = Router(prefix="")

# pylint: disable=unused-argument


@router.command(model="MarketIndices")
async def market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Market Indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EuropeanIndices")
async def european(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical European Indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexConstituents")
async def constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Constituents. Constituents of an index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EuropeanIndexConstituents")
async def european_constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """European Index Constituents. Constituents of select european indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexSnapshots")
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Snapshots. Current levels for all indices from a provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="AvailableIndices")
async def available(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Available Indices. Available indices for a given provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexSearch")
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Search. Search for indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SP500Multiples")
async def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios."""
    return await OBBject.from_query(Query(**locals()))

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
def market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Market Indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndices")
def european(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical European Indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="FredIndices")
def fred(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Fred Indices. Close values for selected Fred indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexConstituents")
def constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Constituents. Constituents of an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndexConstituents")
def european_constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """European Index Constituents. Constituents of select european indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSnapshots")
def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Snapshots. Current levels for all indices from a provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AvailableIndices")
def available(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Available Indices. Available indices for a given provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSearch")
def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Search. Search for indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="SP500Multiples")
def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios."""
    return OBBject(results=Query(**locals()).execute())

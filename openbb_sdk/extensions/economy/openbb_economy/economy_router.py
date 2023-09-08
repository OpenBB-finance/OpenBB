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

router = Router(prefix="")


# Remove this once the placeholders are replaced with real commands.

# pylint: disable=unused-argument


@router.command(model="MajorIndicesConstituents")
def const(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the constituents of an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CPI")
def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """CPI."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="MajorIndicesHistorical")
def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get historical  levels for an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndexHistorical")
def european_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get historical close values for select European indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndexConstituents")
def european_index_constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get  current levels for constituents of select European indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AvailableIndices")
def available_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Lists of available indices from a provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RiskPremium")
def risk(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Market Risk Premium."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSearch")
def index_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search for indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSnapshots")
def index_snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get current  levels for all indices from a provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="COTSearch")
def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Fuzzy search and list of curated Commitment of Traders Reports series information."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="COT")
def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Lookup Commitment of Traders Reports by series ID."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="SP500Multiples")
def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical S&P 500 multiples and Shiller PE ratios."""
    return OBBject(results=Query(**locals()).execute())

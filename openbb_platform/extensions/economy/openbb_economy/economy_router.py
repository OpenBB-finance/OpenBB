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
    """Major Indices Constituents. Constituents of an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CPI")
def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """CPI. Consumer Price Index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="MajorIndicesHistorical")
def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Major Indices Historical. Historical  levels for an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndexHistorical")
def european_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """European Index Historical. Historical close values for selected European indices."""
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
    """Available Indices. Available indices for a given provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RiskPremium")
def risk(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Market Risk Premium. Historical market risk premium."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSearch")
def index_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Search. Search for indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IndexSnapshots")
def index_snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Index Snapshots. Current levels for all indices from a provider."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="COTSearch")
def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    Curated Commitment of Traders Reports.
    Fuzzy search and list of curated Commitment of Traders Reports series information.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="COT")
def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Commitment of Traders Reports. Lookup Commitment of Traders Reports by series ID."""
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


@router.command(model="FredHistorical")
def fred_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Fred Historical. Historical close values for selected Fred indices."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="GDPNom")
def gdpnom(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """GDP Data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="GDPReal")
def gdpreal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """GDP Data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="GDPForecast")
def gdpforecast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """GDP Data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EconomicCalendar")
def econcal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """GDP Data."""
    return OBBject(results=Query(**locals()).execute())

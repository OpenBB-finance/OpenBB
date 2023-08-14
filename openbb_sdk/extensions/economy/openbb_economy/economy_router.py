from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
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


@router.command
def corecpi(
    cc: CommandContext, provider_choices: ProviderChoices
) -> Obbject[Empty]:  # type: ignore
    """CORECPI."""
    return Obbject(results=Empty())


@router.command(model="MajorIndicesConstituents")
def const(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Get the constituents of an index."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="CPI")
def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """CPI."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def cpi_options(
    cc: CommandContext, provider_choices: ProviderChoices
) -> Obbject[Empty]:
    """Get the options for v3 cpi(options=True)"""
    return Obbject(results=Empty())


@router.command(model="MajorIndicesEOD")
def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Get OHLCV data for an index."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="AvailableIndices")
def available_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """AVAILABLE_INDICES."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="RiskPremium")
def risk(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Market Risk Premium."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def macro(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:  # type: ignore
    """Query EconDB for macro data."""
    return Obbject(results=Empty())


@router.command
def macro_countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """MACRO_COUNTRIES."""
    return Obbject(results=Empty())


@router.command
def macro_parameters(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """MACRO_PARAMETERS."""
    return Obbject(results=Empty())


@router.command
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """BALANCE."""
    return Obbject(results=Empty())


@router.command
def bigmac(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """BIGMAC."""
    return Obbject(results=Empty())


@router.command
def country_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """COUNTRY_CODES."""
    return Obbject(results=Empty())


@router.command
def currencies(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """CURRENCIES."""
    return Obbject(results=Empty())


@router.command
def debt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """DEBT."""
    return Obbject(results=Empty())


@router.command
def events(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """EVENTS."""
    return Obbject(results=Empty())


@router.command
def fgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """FGDP."""
    return Obbject(results=Empty())


@router.command
def fred(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """FRED."""
    return Obbject(results=Empty())


@router.command
def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """FRED Search (was fred_notes)."""
    return Obbject(results=Empty())


@router.command
def futures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """FUTURES. 2 sources"""
    return Obbject(results=Empty())


@router.command
def gdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """GDP."""
    return Obbject(results=Empty())


@router.command
def glbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """GLBONDS."""
    return Obbject(results=Empty())


@router.command
def indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """INDICES."""
    return Obbject(results=Empty())


@router.command
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """OVERVIEW."""
    return Obbject(results=Empty())


@router.command
def perfmap(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """PERFMAP."""
    return Obbject(results=Empty())


@router.command
def performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """PERFORMANCE."""
    return Obbject(results=Empty())


@router.command
def revenue(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """REVENUE."""
    return Obbject(results=Empty())


@router.command
def rgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """RGDP."""
    return Obbject(results=Empty())


@router.command
def rtps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """RTPS."""
    return Obbject(results=Empty())


@router.command
def search_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """SEARCH_INDEX."""
    return Obbject(results=Empty())


@router.command
def spending(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """SPENDING."""
    return Obbject(results=Empty())


@router.command
def trust(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """TRUST."""
    return Obbject(results=Empty())


@router.command
def usbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """USBONDS."""
    return Obbject(results=Empty())


@router.command
def valuation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> Obbject[Empty]:
    """VALUATION."""
    return Obbject(results=Empty())

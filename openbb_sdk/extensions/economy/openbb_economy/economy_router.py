from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
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
) -> OBBject[Empty]:  # type: ignore
    """CORECPI."""
    return OBBject(results=Empty())


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


@router.command
def cpi_options(
    cc: CommandContext, provider_choices: ProviderChoices
) -> OBBject[Empty]:
    """Get the options for v3 cpi(options=True)"""
    return OBBject(results=Empty())


@router.command(model="MajorIndicesEOD")
def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get OHLCV data for an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AvailableIndices")
def available_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """AVAILABLE_INDICES."""
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


@router.command
def macro(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:  # type: ignore
    """Query EconDB for macro data."""
    return OBBject(results=Empty())


@router.command
def macro_countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """MACRO_COUNTRIES."""
    return OBBject(results=Empty())


@router.command
def macro_parameters(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """MACRO_PARAMETERS."""
    return OBBject(results=Empty())


@router.command
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """BALANCE."""
    return OBBject(results=Empty())


@router.command
def bigmac(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """BIGMAC."""
    return OBBject(results=Empty())


@router.command
def country_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """COUNTRY_CODES."""
    return OBBject(results=Empty())


@router.command
def currencies(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """CURRENCIES."""
    return OBBject(results=Empty())


@router.command
def debt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """DEBT."""
    return OBBject(results=Empty())


@router.command
def events(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """EVENTS."""
    return OBBject(results=Empty())


@router.command
def fgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """FGDP."""
    return OBBject(results=Empty())


@router.command
def fred(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """FRED."""
    return OBBject(results=Empty())


@router.command
def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """FRED Search (was fred_notes)."""
    return OBBject(results=Empty())


@router.command
def futures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """FUTURES. 2 sources"""
    return OBBject(results=Empty())


@router.command
def gdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """GDP."""
    return OBBject(results=Empty())


@router.command
def glbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """GLBONDS."""
    return OBBject(results=Empty())


@router.command
def indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """INDICES."""
    return OBBject(results=Empty())


@router.command
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """OVERVIEW."""
    return OBBject(results=Empty())


@router.command
def perfmap(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """PERFMAP."""
    return OBBject(results=Empty())


@router.command
def performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """PERFORMANCE."""
    return OBBject(results=Empty())


@router.command
def revenue(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """REVENUE."""
    return OBBject(results=Empty())


@router.command
def rgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """RGDP."""
    return OBBject(results=Empty())


@router.command
def rtps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """RTPS."""
    return OBBject(results=Empty())


@router.command
def search_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """SEARCH_INDEX."""
    return OBBject(results=Empty())


@router.command
def spending(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """SPENDING."""
    return OBBject(results=Empty())


@router.command
def trust(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """TRUST."""
    return OBBject(results=Empty())


@router.command
def usbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """USBONDS."""
    return OBBject(results=Empty())


@router.command
def valuation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> OBBject[Empty]:
    """VALUATION."""
    return OBBject(results=Empty())

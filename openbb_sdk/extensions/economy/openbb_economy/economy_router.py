from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
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


# Remove this once the placeholders are replaced with real commands

# pylint: disable=unused-argument


@router.command
def corecpi(
    cc: CommandContext, provider_choices: ProviderChoices
) -> CommandOutput[Empty]:  # type: ignore
    """CORECPI."""
    return CommandOutput(results=Empty())


@router.command(model="MajorIndicesConstituents")
def const(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """"""
    return CommandOutput(results=Query(**locals()).execute())


# pylint: disable=too-many-arguments
@router.command(model="CPI")
def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """CPI."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def cpi_options(
    cc: CommandContext, provider_choices: ProviderChoices
) -> CommandOutput[Empty]:
    """Get the options for v3 cpi(options=True)"""
    return CommandOutput(results=Empty())


@router.command(model="MajorIndicesPrice")
def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Get OHLCV data for an index."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="AvailableIndices")
def available_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """AVAILABLE_INDICES."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="RiskPremium")
def risk(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Market Risk Premium."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def macro(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:  # type: ignore
    """Query EconDB for macro data."""
    return CommandOutput(results=Empty())


@router.command
def macro_countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """MACRO_COUNTRIES."""
    return CommandOutput(results=Empty())


@router.command
def macro_parameters(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """MACRO_PARAMETERS."""
    return CommandOutput(results=Empty())


@router.command
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """BALANCE."""
    return CommandOutput(results=Empty())


@router.command
def bigmac(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """BIGMAC."""
    return CommandOutput(results=Empty())


@router.command
def country_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """COUNTRY_CODES."""
    return CommandOutput(results=Empty())


@router.command
def currencies(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """CURRENCIES."""
    return CommandOutput(results=Empty())


@router.command
def debt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """DEBT."""
    return CommandOutput(results=Empty())


@router.command
def events(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """EVENTS."""
    return CommandOutput(results=Empty())


@router.command
def fgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """FGDP."""
    return CommandOutput(results=Empty())


@router.command
def fred(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """FRED."""
    return CommandOutput(results=Empty())


@router.command
def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """FRED Search (was fred_notes)."""
    return CommandOutput(results=Empty())


@router.command
def futures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """FUTURES. 2 sources"""
    return CommandOutput(results=Empty())


@router.command
def gdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """GDP."""
    return CommandOutput(results=Empty())


@router.command
def glbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """GLBONDS."""
    return CommandOutput(results=Empty())


@router.command
def indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """INDICES."""
    return CommandOutput(results=Empty())


@router.command
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """OVERVIEW."""
    return CommandOutput(results=Empty())


@router.command
def perfmap(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """PERFMAP."""
    return CommandOutput(results=Empty())


@router.command
def performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """PERFORMANCE."""
    return CommandOutput(results=Empty())


@router.command
def revenue(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """REVENUE."""
    return CommandOutput(results=Empty())


@router.command
def rgdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """RGDP."""
    return CommandOutput(results=Empty())


@router.command
def rtps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """RTPS."""
    return CommandOutput(results=Empty())


@router.command
def search_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """SEARCH_INDEX."""
    return CommandOutput(results=Empty())


@router.command
def spending(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """SPENDING."""
    return CommandOutput(results=Empty())


@router.command
def trust(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """TRUST."""
    return CommandOutput(results=Empty())


@router.command
def usbonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """USBONDS."""
    return CommandOutput(results=Empty())


@router.command
def valuation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
) -> CommandOutput[Empty]:
    """VALUATION."""
    return CommandOutput(results=Empty())

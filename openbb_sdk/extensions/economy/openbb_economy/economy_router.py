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


@router.command(model="EuropeanIndicesEOD")
def european_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get historical closine values for an index."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanIndexConstituents")
def european_index_constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get historical closine values for an index."""
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


@router.command(model="IndexSearch")
def search_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search Available Indices."""
    return OBBject(results=Query(**locals()).execute())


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


@router.command(model="SP500Multiples")
def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get historical values, multiples, and ratios for the S&P 500.

    Choices for `series_name` are: [
        'Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Ratio by Year', 'PE Ratio by Month',
        'Dividend by Year', 'Dividend by Month', 'Dividend Growth by Quarter', 'Dividend Growth by Year',
        'Dividend Yield by Year', 'Dividend Yield by Month', 'Earnings by Year', 'Earnings by Month',
        'Earnings Growth by Year', 'Earnings Growth by Quarter', 'Real Earnings Growth by Year',
        'Real Earnings Growth by Quarter', 'Earnings Yield by Year', 'Earnings Yield by Month',
        'Real Price by Year', 'Real Price by Month', 'Inflation Adjusted Price by Year',
        'Inflation Adjusted Price by Month', 'Sales by Year', 'Sales by Quarter', 'Sales Growth by Year',
        'Sales Growth by Quarter', 'Real Sales by Year', 'Real Sales by Quarter', 'Real Sales Growth by Year',
        'Real Sales Growth by Quarter', 'Price to Sales Ratio by Year', 'Price to Sales Ratio by Quarter',
        'Price to Book Value Ratio by Year', 'Price to Book Value Ratio by Quarter',
        'Book Value per Share by Year', 'Book Value per Share by Quarter'
    ]
    """
    return OBBject(results=Query(**locals()).execute())

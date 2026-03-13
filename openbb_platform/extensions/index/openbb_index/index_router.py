"""Index Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_index.price.price_router import router as price_router

router = Router(prefix="", description="Indices data.")
router.include_router(price_router)

# pylint: disable=unused-argument


@router.command(
    model="IndexConstituents",
    examples=[
        APIEx(parameters={"symbol": "dowjones", "provider": "fmp"}),
        APIEx(
            description="Providers other than FMP will use the ticker symbol.",
            parameters={"symbol": "BEP50P", "provider": "cboe"},
        ),
    ],
)
async def constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Index Constituents."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSnapshots",
    examples=[
        APIEx(parameters={"provider": "tmx"}),
        APIEx(parameters={"region": "us", "provider": "cboe"}),
    ],
)
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index Snapshots. Current levels for all indices from a provider, grouped by `region`."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AvailableIndices",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(parameters={"provider": "yfinance"}),
    ],
)
async def available(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """All indices available from a given provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSearch",
    examples=[
        APIEx(parameters={"provider": "cboe"}),
        APIEx(parameters={"query": "SPX", "provider": "cboe"}),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Filter indices for rows containing the query."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SP500Multiples",
    examples=[
        APIEx(parameters={"provider": "multpl"}),
        APIEx(parameters={"series_name": "shiller_pe_year", "provider": "multpl"}),
    ],
)
async def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical S&P 500 multiples and Shiller PE ratios."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSectors",
    examples=[APIEx(parameters={"symbol": "^TX60", "provider": "tmx"})],
)
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Index Sectors. Sector weighting of an index."""
    return await OBBject.from_query(Query(**locals()))

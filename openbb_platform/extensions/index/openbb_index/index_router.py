"""Index Router."""

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import Example
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_index.price.price_router import router as price_router

router = Router(prefix="")
router.include_router(price_router)

# pylint: disable=unused-argument


@router.command(
    model="MarketIndices",
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint is deprecated; use `/index/price/historical` instead.",
        since=(4, 1),
        expected_removal=(4, 3),
    ),
    api_examples=[Example(parameters={"symbol": "SPX"})],
)
async def market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical Market Indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexConstituents",
    api_examples=[
        Example(parameters={"symbol": "dowjones", "provider": "fmp"}),
        Example(
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
    """Index Constituents."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSnapshots",
    api_examples=[Example(parameters={"region": "us", "provider": "cboe"})],
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
    api_examples=[Example(parameters={"provider": "yfinance"})],
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
    api_examples=[Example(parameters={"query": "SPX", "provider": "cboe"})],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Filters indices for rows containing the query."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SP500Multiples",
    api_examples=[
        Example(parameters={"series_name": "shiller_pe_year", "provider": "nasdaq"})
    ],
)
async def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical S&P 500 multiples and Shiller PE ratios."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSectors",
    api_examples=[Example(parameters={"symbol": "^TX60", "provider": "tmx"})],
)
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index Sectors. Sector weighting of an index."""
    return await OBBject.from_query(Query(**locals()))

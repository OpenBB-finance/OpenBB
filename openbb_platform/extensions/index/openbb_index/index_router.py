"""Index Router."""

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.command_context import CommandContext
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
)
async def market(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical Market Indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexConstituents")
async def constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index Constituents. Constituents of an index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexSnapshots")
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index Snapshots. Current levels for all indices from a provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="AvailableIndices")
async def available(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Available Indices. Available indices for a given provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IndexSearch")
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index Search. Search for indices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SP500Multiples")
async def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios."""
    return await OBBject.from_query(Query(**locals()))

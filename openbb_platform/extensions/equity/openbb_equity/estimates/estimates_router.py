"""Estimates Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/estimates")

# pylint: disable=unused-argument


@router.command(
    model="PriceTarget",
    exclude_auto_examples=True,
    examples=[
        'obb.equity.estimates.price_target(start_date="2020-01-01", end_date="2024-02-16",limit=10, symbol="msft", provider="benzinga",action="downgrades").to_df()'  # noqa: E501 pylint: disable=line-too-long
    ],
)
async def price_target(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get analyst price targets by company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AnalystEstimates",
    exclude_auto_examples=True,
    examples=[
        'obb.equity.estimates.historical("AAPL", period="quarter", provider="fmp").to_df()',
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical analyst estimates for earnings and revenue."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PriceTargetConsensus",
    exclude_auto_examples=True,
    examples=[
        'obb.equity.estimates.consensus("AAPL,MSFT", provider="yfinance").to_df()'
    ],
)
async def consensus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get consensus price target and recommendation."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AnalystSearch",
    exclude_auto_examples=True,
    examples=[
        'obb.equity.estimates.analyst_search(firm_name="Wedbush", provider="benzinga").to_df()',
    ],
)
async def analyst_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search for specific analysts and get their forecast track record."""
    return await OBBject.from_query(Query(**locals()))

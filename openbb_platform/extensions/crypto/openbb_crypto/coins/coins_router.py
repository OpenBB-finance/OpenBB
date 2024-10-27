# pylint: disable=W0613:unused-argument
"""Crypto Coins Router."""

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

router = Router(prefix="/coins")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="BlockTimestamp",
    examples=[
        APIEx(
            parameters={
                "provider": "defillama",
                "chain": "ethereum",
                "timestamp": "2024-01-01",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "chain": "ethereum",
                "timestamp": "2024-01-01T12:12:12",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "chain": "ethereum",
                "timestamp": "1729957601",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "chain": "ethereum",
                "timestamp": 1729957601,
            }
        ),
    ],
)
async def block(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the closest block to a timestamp for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsCurrent",
    examples=[
        APIEx(parameters={"provider": "defillama", "token": "coingecko:ethereum"}),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "1D",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "4H",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "4m",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "1W",
            }
        ),
    ],
)
async def current(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the current price of coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsFirst",
    examples=[
        APIEx(parameters={"provider": "defillama", "token": "coingecko:ethereum"}),
    ],
)
async def first(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the earliest timestamp price record for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsChange",
    examples=[
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "2024-01-01",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "2024-01-01T12:12:12",
                "period": "1W",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "1729957601",
                "period": "7D",
                "look_forward": True,
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": 1729957601,
                "period": "24m",
                "look_forward": True,
            }
        ),
    ],
)
async def change(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the percentage change in pricer over time for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsChart",
    examples=[
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "start_date": "2024-09-01",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "end_date": "2024-10-01",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "start_date": 1725129000,
                "span": 10,
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "start_date": 1725129000,
                "span": 100,
                "period": "1D",
                "search_width": "8h",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "end_date": 1727721000,
                "span": 10,
                "period": "1W",
                "search_width": "1D",
            }
        ),
    ],
)
async def chart(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the price at regular intervals for a coin."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CoinsHistorical",
    examples=[
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "2024-01-01",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "2024-01-01T12:12:12",
                "search_width": "1W",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": "1729957601",
                "search_width": "7D",
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "timestamp": 1729957601,
                "search_width": "4m",
            }
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the historical price for a coin."""
    return await OBBject.from_query(Query(**locals()))

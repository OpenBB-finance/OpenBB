"""Futures Router."""

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

router = Router(prefix="/futures")


# pylint: disable=unused-argument
@router.command(
    model="FuturesHistorical",
    examples=[
        APIEx(parameters={"symbol": "ES", "provider": "yfinance"}),
        APIEx(
            description="Enter multiple symbols.",
            parameters={"symbol": "ES,NQ", "provider": "yfinance"},
        ),
        APIEx(
            description='Enter expiration dates as "YYYY-MM".',
            parameters={
                "symbol": "ES",
                "provider": "yfinance",
                "expiration": "2025-12",
            },
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical futures prices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FuturesCurve",
    examples=[
        APIEx(parameters={"symbol": "VX", "provider": "cboe", "date": "2024-06-25"}),
        APIEx(
            parameters={"symbol": "NG", "provider": "yfinance"},
        ),
    ],
)
async def curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Futures Term Structure, current or historical."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FuturesInstruments",
    examples=[
        APIEx(parameters={"provider": "deribit"}),
    ],
)
async def instruments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get reference data for available futures instruments by provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FuturesInfo",
    examples=[
        APIEx(parameters={"provider": "deribit", "symbol": "BTC"}),
        APIEx(parameters={"provider": "deribit", "symbol": "SOLUSDC"}),
        APIEx(parameters={"provider": "deribit", "symbol": "SOL_USDC-PERPETUAL"}),
        APIEx(parameters={"provider": "deribit", "symbol": "BTC,ETH"}),
    ],
)
async def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get current trading statistics by futures contract symbol."""
    return await OBBject.from_query(Query(**locals()))

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
        APIEx(parameters={"symbol": "VX", "provider": "cboe"}),
        APIEx(
            description="Enter a date to get the term structure from a historical date.",
            parameters={"symbol": "NG", "provider": "yfinance", "date": "2023-01-01"},
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

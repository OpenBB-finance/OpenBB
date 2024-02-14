"""Futures Router."""

from openbb_core.app.model.command_context import CommandContext
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
    exclude_auto_examples=True,
    examples=[
        'obb.derivatives.futures.historical("ES", provider="yfinance")',
        '#### Enter expiration dates as "YYYY-MM" ####',
        'obb.derivatives.futures.historical("ES", provider="yfinance", expiration="2025-12")',
        "#### Enter multiple symbols as a list. ####",
        'obb.derivatives.futures.historical(["ES", "NQ", "ESZ24.CME", "NQZ24.CME"], provider="yfinance")',
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
    exclude_auto_examples=True,
    examples=[
        'obb.derivatives.futures.curve("NG", provider="yfinance")',
        "#### Enter a date to get the term structure from a historical date. ####",
        'obb.derivatives.futures.curve("NG", provider="yfinance", date="2023-01-01")',
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

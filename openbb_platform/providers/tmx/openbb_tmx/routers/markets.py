"""TMX Markets sub-router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

router = Router(prefix="/markets", description="TMX market-wide data.")


@router.command(
    model="MarketMovers",
    examples=[
        APIEx(
            description="Gainers and losers by exchange.",
            parameters={"exchange": "tsx", "provider": "tmx"},
        )
    ],
)
async def movers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Rank the biggest movers on an exchange."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="EquityTrades",
    examples=[
        APIEx(
            description="Time and sales with broker attribution.",
            parameters={"symbol": "AC", "provider": "tmx"},
        )
    ],
)
async def trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Recent trades, with the buying and selling brokers."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="ShortInterest",
    examples=[
        APIEx(
            description="Reported short interest.",
            parameters={"symbol": "AC", "provider": "tmx"},
        )
    ],
)
async def short_interest(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Short interest and days to cover."""
    return await OBBject.from_query(OBBQuery(**locals()))

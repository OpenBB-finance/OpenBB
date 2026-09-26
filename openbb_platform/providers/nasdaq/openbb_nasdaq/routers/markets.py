"""Nasdaq Markets sub-router."""

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

router = Router(prefix="/markets", description="Nasdaq market-wide data.")


@router.command(
    model="MarketMovers",
    examples=[
        APIEx(
            description="The most actively traded stocks by share volume.",
            parameters={"provider": "nasdaq"},
        ),
        APIEx(
            description="The biggest ETF advancers.",
            parameters={
                "asset_class": "etf",
                "category": "most_advanced",
                "provider": "nasdaq",
            },
        ),
    ],
)
async def movers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Nasdaq market movers - most active, advancers, decliners, and Nasdaq-100."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqMarketStatus",
    examples=[
        APIEx(
            description="The current US market session status.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def status(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the US market session status, and the next open and close times."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqPriceQuote",
    examples=[
        APIEx(
            description="A light quote for a mixed-asset watchlist.",
            parameters={"symbol": "AAPL,QQQ,OMXS30", "provider": "nasdaq"},
        )
    ],
)
async def quotes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Batch quotes for any mix of stocks, funds, indexes, and crypto pairs."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    methods=["GET"],
    widget_config={
        "name": "Nasdaq Upcoming Events",
        "category": "Economy",
        "subCategory": "Calendar",
    },
    examples=[APIEx(description="Event counts for the next session.", parameters={})],
)
async def upcoming(date: str | None = None) -> list[dict]:
    """Get counts and a preview of upcoming earnings, dividends, splits, and IPOs."""
    from openbb_nasdaq.utils.constants import CALENDAR_EVENTS
    from openbb_nasdaq.utils.helpers import get_nasdaq_data

    path = "calendar/upcoming" + (f"?date={date}" if date else "")
    data = await get_nasdaq_data(path) or []

    return [
        {
            "event": block.get("name"),
            "count": block.get("eventCount"),
            "preview": block.get(CALENDAR_EVENTS.get(block.get("name"), "")) or [],
        }
        for block in data
    ]

"""Calendar Router."""

from openbb_core.app.model import CommandContext, Example, OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/calendar")

# pylint: disable=unused-argument


@router.command(
    model="CalendarIpo",
    api_examples=[
        Example(parameters={"limit": 100}),
        Example(description="Get all IPOs available.", parameters={}),
        Example(
            description="Get IPOs for specific dates.",
            parameters={"start_date": "2024-02-01", "end_date": "2024-02-07"},
        ),
    ],
)
async def ipo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical and upcoming initial public offerings (IPOs)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarDividend",
    api_examples=[
        Example(parameters={}),
        Example(
            description="Get dividend calendar for specific dates.",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
            },
        ),
    ],
)
async def dividend(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical and upcoming dividend payments. Includes dividend amount, ex-dividend and payment dates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarSplits",
    api_examples=[
        Example(parameters={}),
        Example(
            description="Get stock splits calendar for specific dates.",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
            },
        ),
    ],
)
async def splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical and upcoming stock split operations."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarEarnings",
    api_examples=[
        Example(parameters={}),
        Example(
            description="Get earnings calendar for specific dates.",
            parameters={"start_date": "2024-02-01", "end_date": "2024-02-07"},
        ),
    ],
)
async def earnings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical and upcoming company earnings releases. Includes earnings per share (EPS) and revenue data."""
    return await OBBject.from_query(Query(**locals()))

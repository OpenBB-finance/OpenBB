# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""News Router."""

from openbb_core.app.model import CommandContext, Example, OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="")


@router.command(
    model="WorldNews",
    examples=[
        Example(parameters={"limit": 2500}),
        Example(
            description="Get news on the specified dates.",
            parameters={"start_date": "2024-02-01", "end_date": "2024-02-07"},
        ),
        Example(
            description="Display the headlines of the news.",
            parameters={"display": "headline", "provider": "benzinga"},
        ),
        Example(
            description="Get news by topics.",
            parameters={"topics": "finance", "provider": "benzinga"},
        ),
        Example(
            description="Get news by source using 'tingo' as provider.",
            parameters={"provider": "tiingo", "source": "bloomberg"},
        ),
        Example(
            description="Filter aticles by term using 'biztoc' as provider.",
            parameters={"provider": "biztoc", "term": "apple"},
        ),
    ],
)
async def world(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """World News. Global news data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompanyNews",
    examples=[
        Example(parameters={"limit": 2500}),
        Example(
            description="Get news on the specified dates.",
            parameters={
                "symbol": "AAPL",
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
            },
        ),
        Example(
            description="Display the headlines of the news.",
            parameters={
                "symbol": "AAPL",
                "display": "headline",
                "provider": "benzinga",
            },
        ),
        Example(
            description="Get news for multiple symbols.",
            parameters={"symbol": "aapl,tsla"},
        ),
        Example(
            description="Get news company's ISIN.",
            parameters={"symbol": "NVDA", "isin": "US0378331005"},
        ),
    ],
)
async def company(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Company News. Get news for one or more companies."""
    return await OBBject.from_query(Query(**locals()))

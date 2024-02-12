# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""News Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
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
        "# Get news on the specified dates.",
        "obb.news.world(start_date='2024-02-01', end_date='2024-02-07')",
        "# Display the headlines of the news.",
        "obb.news.world(display='headline', provider='benzinga')",
        "# Get news by topics.",
        "obb.news.world(topics='finance', provider='benzinga')",
        "# Get news by source using 'tingo' as provider.",
        "obb.news.world(provider='tiingo', source='bloomberg')",
        "# Filter aticles by term using 'biztoc' as provider.",
        "obb.news.world(provider='biztoc', term='apple')",
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
        "# Get news on the specified dates.",
        "obb.news.company(symbol='AAPL', start_date='2024-02-01', end_date='2024-02-07')",
        "# Display the headlines of the news.",
        "obb.news.company(symbol='AAPL', display='headline', provider='benzinga')",
        "# Get news for multiple symbols.",
        "obb.news.company(symbol='aapl,tsla')",
        "# Get news company's ISIN.",
        "obb.news.company(symbol='NVDA', isin='US0378331005')",
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

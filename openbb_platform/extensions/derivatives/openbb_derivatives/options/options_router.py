"""Options Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/options")

# pylint: disable=unused-argument


@router.command(
    model="OptionsChains",
    exclude_auto_examples=True,
    examples=[
        'chains = obb.derivatives.options.chains(symbol="AAPL", provider="intrinio").to_df()',
        '#### Use the "date" parameter to get the end-of-day-data for a specific date, where supported. ####',
        'eod_chains = obb.derivatives.options.chains(symbol="AAPL", date="2023-01-25", provider="intrinio").to_df()',
    ],
)
async def chains(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the complete options chain for a ticker."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="OptionsUnusual",
    exclude_auto_examples=True,
    examples=[
        "options = obb.derivatives.options.unusual().to_df()",
        '#### Use the "symbol" parameter to get the most recent activity for a specific symbol. ####',
        'options = obb.derivatives.options.unusual(symbol="TSLA").to_df()',
    ],
)
async def unusual(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the complete options chain for a ticker."""
    return await OBBject.from_query(Query(**locals()))

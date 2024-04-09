"""Price Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/price")

# pylint: disable=unused-argument


@router.command(
    model="IndexHistorical",
    exclude_auto_examples=True,
    examples=[
        'obb.index.price.historical("^GSPC", provider="fmp").to_df()',
        "#### Not all providers have the same symbols. ####",
        'obb.index.price.historical("SPX", provider="intrinio").to_df()',
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical Index Levels."""
    return await OBBject.from_query(Query(**locals()))

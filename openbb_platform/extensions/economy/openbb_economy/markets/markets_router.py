"""Economy Markets Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/markets")

# pylint: disable=unused-argument


# @router.command(model="MarketsCategoryQuotes")
# async def quote_category(
#     cc: CommandContext,
#     provider_choices: ProviderChoices,
#     standard_params: StandardParams,
#     extra_params: ExtraParams,
# ) -> OBBject:
#     """Get quotes for a specific category of markets."""
#     return await OBBject.from_query(Query(**locals()))


# @router.command(model="MarketsSymbolQuotes")
# async def quote_symbol(
#     cc: CommandContext,
#     provider_choices: ProviderChoices,
#     standard_params: StandardParams,
#     extra_params: ExtraParams,
# ) -> OBBject:
#     """Get quotes for a specific symbol."""
#     return await OBBject.from_query(Query(**locals()))


@router.command(model="MarketsHistorical")
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get quotes for a specific symbol."""
    return await OBBject.from_query(Query(**locals()))
